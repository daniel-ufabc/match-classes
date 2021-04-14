function flash(msg) {
    new Noty({
        type: 'info',
        theme: 'bootstrap-v4',
        text: msg,
        timeout: 3000
    }).show();
}

function note(msg) {
    new Noty({
        type: 'success',
        theme: 'bootstrap-v4',
        text: msg,
        timeout: 3000
    }).show();
}

var good_note = note;

function bad_note(msg, error) {
    if (error) {
        console.log(error);
        msg += ' Mais detalhes no console.'
    }
    new Noty({
        type: 'error',
        theme: 'bootstrap-v4',
        text: msg,
        timeout: 3000
    }).show();
}
