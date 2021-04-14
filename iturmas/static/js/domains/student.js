// depends on crud.js and search.js being loaded

if (typeof domain !== 'undefined') {
    throw 'Domain already defined! You must include only one of js/domains/*.js';
}

var domain = 'students';
crud.domain = domain;

var studentEditCodeWarningTimeout;

$("#search_string").keyup(function(event) {
    if (event.keyCode === 13) {
        event.stopPropagation();
        search();
    }
});

function search(offset) {
    const limit = document.getElementById('maxperpageSelect').value;
    generic_search({ domain, offset, limit, item_text: 'Alunos cadastrados' })
}

var insert_student = function() {
    const success_text = 'Aluno cadastrado com sucesso.'
    const error_text = 'Problemas na inserção do aluno.'
    const data = {
        name: $('#studentInputName').val().trim(),
        email: $('#studentInputEmail').val().trim(),
        code:  $('#studentInputCode').val().trim(),
        max_load:  $('#studentInputMaxLoad').val().trim(),
        properties: $('#studentInputProperties').val()
    }
    crud.create({ data, success_text, error_text }, () => {
        $('#studentInputName').val('')
        $('#studentInputEmail').val('')
        $('#studentInputCode').val('')
        $('#studentInputMaxLoad').val('')
        $('#studentInputProperties').val('')
        search()
    })
}

var delete_student = function(code) {
    const name = $('#collapse' + code).attr('data-iturmas-name')
    const message = "Você realmente quer excluir o aluno " + name + "?"

    bootbox.confirm({
        message: "Você realmente quer excluir o aluno " + name + "?",
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
                const success_text = 'Aluno excluído com sucesso.'
                const error_text = 'Não foi possível excluir o aluno desejado.'
                crud.remove({ data: { code }, success_text, error_text }, () => {
                    search()
                })
            }
        }
    })
}

var showWarning = function() {
    clearTimeout(studentEditCodeWarningTimeout)
    const editRA = $('#editStudentCodeWarning')
    if (editRA.hasClass('my-hidden')) {
        $('#editStudentCodeWarning').removeClass('my-hidden')
    }
    studentEditCodeWarningTimeout = setTimeout(function() {
        const editRA = $('#editStudentCodeWarning')
        if (!editRA.hasClass('my-hidden')) {
            $('#editStudentCodeWarning').addClass('my-hidden')
        }
    }, 5000);
}

var edit_student = function(code) {
    crud.read({ data: { code } }, function(student) {
        $('#studentEditName').val(student.name)
        $('#studentEditEmail').val(student.email)
        $('#studentEditCode').val(student.code)
        $('#studentEditMaxLoad').val(student.max_load)
        const jsonPretty = JSON.stringify(JSON.parse(student.properties), null, 4)
        $('#studentEditProperties').val(jsonPretty)
        $('#editStudentModal').modal('show')
    })
}

var cancel_edit_student = function() {
    $('#studentEditName').val('')
    $('#studentEditEmail').val('')
    $('#studentEditCode').val('')
    $('#studentEditMaxLoad').val('')
    $('#studentEditProperties').val('')
    $('#editStudentModal').modal('hide')
}

var finish_edit_student = function() {
    const success_text = 'Dados do aluno atualizados com sucesso.'
    const error_text = 'Problemas na atualização dos dados do aluno.'
    const data = {
        name: $('#studentEditName').val().trim(),
        email: $('#studentEditEmail').val().trim(),
        code:  $('#studentEditCode').val().trim(),
        max_load:  $('#studentEditMaxLoad').val().trim(),
        properties: $('#studentEditProperties').val(),
        update: true
    }

    crud.update({ data, success_text, error_text }, () => {
        cancel_edit_student()
        search()
    })
}