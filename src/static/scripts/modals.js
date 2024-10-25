
document.addEventListener('DOMContentLoaded', () => {
    const modalWrapper = $('#modal-wrapper');
    modalWrapper.on('click', function(event) {
        if (event.target === this) modalWrapper.hide();
    });

    document.addEventListener('click', (event) => {
        const target = event.target;
        if (target === $('#column-modal-wrapper').get(0)) {
            toggleModal();
        }
        getTargettedBoardElement(target);

    });

    $(document).on('column-wrapper-show', () => {
        const wrapper = $('#column-modal-wrapper')
        const column = $(wrapper).children('.column-silhouette')[0];
        const columnTitle = $(column).find('a.column-modal-href')[0];
        const reference = columnTitle.href;
        openModal(reference, (data) => {
            const display = $('#column-modal-panel');
            display.html(data);
        });
    });

});


function hideModal(modal_wrapper=null) {
    if (!modal_wrapper) {
        $('#modal-wrapper').hide();
        return;
    }
    toggleModal();
}


function openModal(path, modalExecutable=null) {
    console.log(path);
    fetch(path, {
        method: 'GET',
        headers: {
            'Content-Type': 'html/text',
            'X-CSRFToken': getCSRFToken()
        }
    }).then(async response => {
        if (response.ok && response.headers.get('Content-Type').includes('text/html')) {
            return response.text();
        }
        let message = await response.text().then((error) => {return error;});
        message = JSON.parse(message);
        console.log(Object.keys(message));
        displayMessage(message);
        throw new Error(message.message);
    }).then(data => {
        if (modalExecutable) {
            modalExecutable(data);
            return;
        }
        const modalWrapper = $('#modal-wrapper');
        const modal = $('#modal');
        //console.log(data);
        modal.html(data);
        modalWrapper.show();
    }).catch(error => {
        console.error(error);
    });
}

function toggleDragging(column, value) {
    $(column).attr('draggable', value);
    $(column).find('.card-silhouette').attr('draggable', value);
}

function getTargettedBoardElement(target) {
    switch (target.tagName) {
        case 'H2':
            handleColumnTarget(target);
            break;
        case 'H4':
            handleCardTarget(target);
            break;
        default:
            break;
    }
}

function handleColumnTarget(target) {
    const parent = $(target).parents('.column-silhouette').get(0);
    if (!parent) return;

    if (parent.parentElement.id === 'column-modal-wrapper') {
        toggleModal();
        return;
    }

    const placeholder = document.createElement('div');
    placeholder.id = 'modal-column-placeholder';

    const wrapper = $('#column-modal-wrapper')
    const columnContainer = $('#column-container');

    const index = $(parent).index();
    parent.before(placeholder);
    wrapper.prepend(parent);
    toggleDragging(parent, false);

    wrapper.show().trigger('column-wrapper-show');
}

function handleCardTarget(target) {
    const parent = $(target).parents('.card-silhouette').get(0);
    if (!parent) return;

    const path = $(parent).find('.card-modal-href').get(0).href;
    openModal(path);
}

function toggleModal() {
    const modalWrapperColumn = $('#column-modal-wrapper');
    const columnPlaceholder = $('#modal-column-placeholder');
    const column = modalWrapperColumn.children('.column-silhouette')[0];
    columnPlaceholder.replaceWith(column);
    toggleDragging(column, true);
    modalWrapperColumn.hide();
}




