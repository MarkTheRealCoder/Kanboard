
function buildDnDPayload() {
    const columns = document.querySelectorAll('.column-silhouette');
    const payload = [];

    for (let i = 0; i < columns.length; i++) {
        const column = columns[i];
        const cards = column.querySelectorAll('.card-silhouette');

        const columnIndex = i;
        const columnId = column.querySelector('data').value;
        const cardCount = cards.length;

        const cardsPayload = [];
        for (let j = 0; j < cardCount; j++) {
            const cardIndex = j;
            const cardId = cards[j].querySelector('data').value;
            cardsPayload.push({id: cardId, index: cardIndex});
        }

        payload.push({id: columnId, index: columnIndex, cards: cardsPayload});
    }
    return payload;
}


function getSyncronizedColumns(path) {
    fetch(path, {
        method: 'GET',
        headers: {'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json'}
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error(`Request failed with status ${response.status}`);
        })
        .then(data => {
            $('#column-container').html(data.message);
        })
        .catch(error => {
            console.error(error);
        });
}

function sendDnDPayload(path_update, path_sync) {
    const payload = buildDnDPayload();

    fetch(path_update, {
        method: 'POST',
        headers: {'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (response.ok) {
            getSyncronizedColumns(path_sync);
        }
        else throw new Error(`Request failed with status ${response.status}`);
    })
    .catch(error => {
        console.error(error);
    });
}

/*
* */






function getNearestElementByType(container, type, event) {
    const elements = container.querySelectorAll(type); // Get all elements of the given type
    let x = event.clientX;
    let y = event.clientY;
    let nearestElement = null;
    let minDistance = Infinity;
    if (elements.length === 0) return "empty";

    for (let element of elements) {
        const rect = element.getBoundingClientRect();
        const elementCenterX = rect.left + rect.width / 2;
        const elementCenterY = rect.top + rect.height / 2;

        // Calculate the distance between the coordinate (x, y) and the center of the element
        const distance = Math.sqrt(
            Math.pow(elementCenterX - x, 2) + Math.pow(elementCenterY - y, 2)
        );

        // Update if this element is closer
        if (distance < minDistance) {
            minDistance = distance;
            nearestElement = element;
        }
    }

    return nearestElement; // Return the nearest element of the given type
}


class DragAndDrop {

    findSide = (type, element, event) => {
        if (element === "empty") return 'empty';
        const rect = element.getBoundingClientRect();
        const x = event.clientX;
        const y = event.clientY;
        const midX = (rect.left + rect.right) / 2;
        const midY = (rect.top + rect.bottom) / 2;
        const comparator = type === 'column' ? x : y;
        const comparator2 = type === 'column' ? midX : midY;
        return comparator < comparator2 ? 'Before' : 'After';
    }

    isCursorOverElement = (element, event) => {
        const rect = element.getBoundingClientRect();
        const x = event.clientX;
        const y = event.clientY;
        // console.log(`x: ${x}, y: ${y}`);
        // console.log(`left: ${rect.left}, right: ${rect.right}, top: ${rect.top}, bottom: ${rect.bottom}`);
        return (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom);
    }

    isCursorOverAnyElement = (query, event) => {
        let result = null;
        for (let element of document.querySelectorAll(query)) {
            // console.log(`Hovered? -> ${element}`);
            if (this.isCursorOverElement(element, event)) result = element;
        }
        return result;
    }

    createPlaceholder = () => {
        const placeholder = document.createElement('hr');
        placeholder.id = 'dnd-placeholder';
        return placeholder;
    }

    placePlaceholder = (hovered, type, boa/*Before or After*/) => {
        let placeholder = document.getElementById('dnd-placeholder') || this.createPlaceholder();

        placeholder.classList = [];
        placeholder.classList.add(`placeholder-${type}`);

        if (boa === 'empty') {
            hovered.appendChild(placeholder);
            return;
        }

        const container = hovered.parentElement;

        container.insertBefore(placeholder, boa === 'Before' ? hovered : hovered.nextSibling);
    }

    moveElement = (element) => {
        if (element === null) return;
        const placeholder = document.getElementById('dnd-placeholder');
        const oldContainer = element.parentElement;
        const container = placeholder.parentElement;
        oldContainer.removeChild(element);
        container.insertBefore(element, placeholder);
        element.removeAttribute('id');
        document.dispatchEvent(new CustomEvent('elementMoved'));
    }

    constructor(correspondences) {

        this.map = correspondences

        let currentElement = null;
        let expectedContainer = null;

        document.addEventListener('dragstart', (event) => {
            const target = event.target;
            if (target.getAttribute('draggable')) {
                for (let key of Object.keys(this.map)) {
                    if (target.classList.contains(key)) {
                        currentElement = key;
                        expectedContainer = this.map[key];
                        target.id = 'dragged';
                    }
                }
            }
        });

        document.addEventListener('dragover', (event) => {
            event.preventDefault();
            let hovered = {element: null, is_container: false};
            const type = currentElement.includes('column') ? 'column' : 'card';
            const elementClass = `.${currentElement}`;

            hovered.element = this.isCursorOverAnyElement(elementClass, event)
            if (!hovered.element) {
                hovered.element = this.isCursorOverAnyElement(`${expectedContainer}`, event);
                hovered.is_container = true;
            }

            if (!hovered.element) return;

            let element = (!hovered.is_container) ? hovered.element : getNearestElementByType(hovered.element, elementClass, event);
            let boa = this.findSide(type, element, event);
            if (element === "empty") element = hovered.element;
            this.placePlaceholder(element, type, boa);

        });

        document.addEventListener('dragend', function (event) {

        });

        document.addEventListener('drop', (event) => {
            event.preventDefault();

            console.log("Drop event");
            const target = document.getElementById('dragged');
            this.moveElement(target);
            const toBeRemoved = document.getElementById('dnd-placeholder');
            if (toBeRemoved) toBeRemoved.parentElement.removeChild(toBeRemoved);
        });
    }
}
