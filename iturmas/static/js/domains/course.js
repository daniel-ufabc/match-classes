// depends on crud.js and search.js being loaded

if (typeof domain !== 'undefined') {
    throw 'Domain already defined! You must include only one of js/domains/*.js';
}

var domain = 'courses';
crud.domain = domain;

var editCodeWarningTimeout;

$("#search_string").keyup(function(event) {
    if (event.keyCode === 13) {
        event.stopPropagation();
        search();
    }
});

function search(offset) {
    const limit = document.getElementById('maxperpageSelect').value
    generic_search({ domain, offset, limit, item_text: 'Disciplinas cadastradas' })
}

var insert_course = function() {
    const success_text = 'Disciplina cadastrada com sucesso.'
    const error_text = 'Problemas na inserção da disciplina.'
    const data = {
        name: $('#courseNameInsertInput').val().trim(),
        code:  $('#courseCodeInsertInput').val().trim(),
        properties: $('#coursePropertiesInsertInput').val()
    }
    crud.create({ data, success_text, error_text }, (result) => {
        $('#courseNameInsertInput').val('');
        $('#courseCodeInsertInput').val('');
        $('#coursePropertiesInsertInput').val('');
        search();
    })
}

var delete_course = function(code) {
    const name = $('#collapse' + code).attr('data-iturmas-name')
    const message = "Você realmente quer excluir a disciplina " + name + "?"

    bootbox.confirm({
        message: message,
        buttons: {
            cancel: {
                label: 'Sim, excluir!',
                className: 'btn-danger'
            },
            confirm: {
                label: 'Não',
                className: 'btn-light'
            }
        },
        callback: function (result) {
            if (result == false) {
                const success_text = 'Disciplina excluída com sucesso.'
                const error_text = 'Não foi possível excluir a disciplina desejada.'
                crud.remove({ data: { code }, success_text, error_text }, () => {
                    search()
                })
            }
        }
    })
}

var showWarning = function() {
    clearTimeout(editCodeWarningTimeout)
    const editCodeWarning = $('#editCodeWarning')
    if (editCodeWarning.hasClass('my-hidden')) {
        editCodeWarning.removeClass('my-hidden')
    }
    editCodeWarningTimeout = setTimeout(function() {
        const editCodeWarning = $('#editCodeWarning')
        if (!editCodeWarning.hasClass('my-hidden')) {
            editCodeWarning.addClass('my-hidden')
        }
    }, 5000);
}

var edit_course = function(code) {
    crud.read({ data: { code } }, function(course) {
        $('#courseNameEditInput').val(course.name)
        $('#courseCodeEditInput').val(course.code)
        const jsonPretty = JSON.stringify(JSON.parse(course.properties), null, 4)
        $('#coursePropertiesEditInput').val(jsonPretty)
        $('#editCourseModal').modal('show')
    })
}

var cancel_edit_course = function() {
    $('#courseNameEditInput').val('')
    $('#courseCodeEditInput').val('')
    $('#coursePropertiesEditInput').val('')
    $('#editCourseModal').modal('hide')
}

var finish_edit_course = function() {
    const success_text = 'Dados da disciplina atualizados com sucesso.'
    const error_text = 'Problemas na atualização dos dados da disciplina.'
    const data = {
        name: $('#courseNameEditInput').val().trim(),
        code:  $('#courseCodeEditInput').val().trim(),
        properties: $('#coursePropertiesEditInput').val(),
        update: true
    }

    crud.update({ data, success_text, error_text }, () => {
        cancel_edit_course()
        search()
    })
}