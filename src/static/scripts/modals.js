
window.addEventListener('DOMContentLoaded', () => {
    const modalWrapper = $('#modal-wrapper');
    modalWrapper.on('click', function(event) {
        if (event.target === this) modalWrapper.hide();
    });
});


function openModal(path) {
    fetch(path, {
        method: 'GET',
        headers: {
            'Content-Type': 'html/text',
            'X-CSRFToken': getCSRFToken()
        }
    }).then(response => {
        if (response.ok) return response.text();
        throw new Error(`Request failed with status ${response.status}`);
    }).then(data => {
        const modalWrapper = $('#modal-wrapper');
        const modal = $('#modal');
        modal.html(data);
        modalWrapper.show();
    }).catch(error => {
        console.error(error);
    });
}
