// depends on crud.js and search.js being loaded

if (typeof domain !== 'undefined') {
    throw 'Domain already defined! You must include only one of js/domains/*.js';
}

var domain = 'classes';
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
    generic_search({ domain, offset, limit, item_text: 'Turmas cadastradas' })
}

var insert_class = function() {
    const success_text = 'Turma cadastrada com sucesso.'
    const error_text = 'Problemas na inserção da turma.'
    const data = {
        code: $('#classCodeInsertInput').val().trim(),
        course_code:  $('#classCourseCodeInsertInput').val().trim(),
        schedule: $('#classScheduleInsertInput').val().trim(),
        vacancies: $('#classVacanciesInsertInput').val().trim(),
        properties: $('#classPropertiesInsertInput').val()
    }
    if (validate(data)) {
        crud.create({ data, success_text, error_text}, () => {
            $('#classCodeInsertInput').val('')
            $('#classCourseCodeInsertInput').val('')
            $('#classScheduleInsertInput').val('')
            $('#classVacanciesInsertInput').val('')
            $('#classPropertiesInsertInput').val('')
            search()
        })
    }
};

var delete_class = function(code) {
    const message = "Você realmente quer excluir a turma " + code + "?"

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
                const success_text = 'Turma excluída com sucesso.'
                const error_text = 'Não foi possível excluir a turma desejada.'
                crud.remove({ data: { code }, success_text, error_text}, () => {
                    search();
                })
            }
        }
    })
}

var showWarning = function() {
    clearTimeout(editCodeWarningTimeout);
    var editCodeWarning = $('#editCodeWarning');
    if (editCodeWarning.hasClass('my-hidden')) {
        editCodeWarning.removeClass('my-hidden');
    }
    editCodeWarningTimeout = setTimeout(function() {
        var editCodeWarning = $('#editCodeWarning');
        if (!editCodeWarning.hasClass('my-hidden')) {
            editCodeWarning.addClass('my-hidden');
        }
    }, 5000);
}

var edit_class = function(code) {
    crud.read({ data: { code } }, function(_class) {
        $('#classCodeEditInput').val(_class.code)
        $('#classCourseCodeEditInput').val(_class.course_code)
        $('#classScheduleEditInput').val(_class.schedule)
        $('#classVacanciesEditInput').val(_class.vacancies)
        const jsonPretty = JSON.stringify(JSON.parse(_class.properties), null, 4)
        $('#classPropertiesEditInput').val(jsonPretty)
        $('#editClassModal').modal('show')
    })
}

var cancel_edit_class = function() {
    $('#classCodeEditInput').val('')
    $('#classCourseCodeEditInput').val('')
    $('#classScheduleEditInput').val('')
    $('#classVacanciesEditInput').val('')
    $('#classPropertiesEditInput').val('')
    $('#editClassModal').modal('hide')
}

var finish_edit_class = function() {
    const success_text = 'Dados da turma atualizados com sucesso.'
    const error_text = 'Problemas na atualização dos dados da turma.'
    const data = {
        code: $('#classCodeEditInput').val().trim(),
        course_code:  $('#classCourseCodeEditInput').val().trim(),
        schedule: $('#classScheduleEditInput').val().trim(),
        vacancies: $('#classVacanciesEditInput').val().trim(),
        properties: $('#classPropertiesEditInput').val(),
        update: true

    }
    if (validate(data)) {
        crud.update({ data, success_text, error_text}, () => {
            cancel_edit_class()
            search()
        })
    }
}