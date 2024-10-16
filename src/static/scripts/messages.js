let TIMER = null;


window.onload = function() {
    const msgBox = $('#service-message');
    msgBox.css('visibility', 'hidden');
    msgBox.on( "click", function() {
        $( this ).fadeOut(2000, () => {clearTimeout(TIMER)});
    });

}

function displayMessage(data) {
    const status = data.status;
    const message = data.message;
    let bg_col = '#218838';
    let border_col = '#28a745';
    switch (status) {
        case 100:
            bg_col = '#f1d842';
            border_col = '#faf483';
            break;
        case 500:
            bg_col = '#c82333';
            border_col = '#dc3545';
            break;
        default:
            break;
    }

    const msgBox = $('#service-message')
    let closed = false;

    if (TIMER) {
        clearTimeout(TIMER);
        msgBox.fadeOut(0);
    }
    msgBox.text(message)
        .css('background-color', bg_col)
        .css('border-color', border_col)
        .css('visibility', 'visible')
        .fadeIn(500);

    TIMER = setTimeout(() => {
        msgBox.fadeOut(2000);
    }, 5000)
}