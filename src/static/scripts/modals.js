
window.addEventListener('DOMContentLoaded', () => {
    const modalWrapper = $('#modal-wrapper');
    modalWrapper.on('click', function(event) {
        if (event.target === this) modalWrapper.hide();
    });
});

function hideModal() {
    $('#modal-wrapper').hide();
}


function openModal(path) {
    console.log(path);
    fetch(path, {
        method: 'GET',
        headers: {
            'Content-Type': 'html/text',
            'X-CSRFToken': getCSRFToken()
        }
    }).then(async response => {
        if (response.ok) return response.text();
        let message = `Request failed: ${await response.text().then((error) => {return error;})}`;
        displayMessage({message: message, status: 500});
        throw new Error(message);
    }).then(data => {
        const modalWrapper = $('#modal-wrapper');
        const modal = $('#modal');
        modal.html(data);
        modalWrapper.show();
    }).catch(error => {
        console.error(error);
    });
}
