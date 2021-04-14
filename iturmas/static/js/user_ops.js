// assumes crud.js has been loaded...

function processKey(e) {
    if (e.keyCode == 32) {
        e.target.checked = ! e.target.checked
    }
}

document.querySelector('#adminOpt').addEventListener('keyup', processKey)
document.querySelector('#inviteOpt').addEventListener('keyup', processKey)

function add_user() {
    document.querySelector('#emailInput').value = ''
    document.querySelector('#adminOpt').checked = false
    document.querySelector('#inviteOpt').checked = false
    $('#addUserModal').modal('show')
    $('#addUserModal').on('shown.bs.modal', function (e) {
          document.getElementById('emailInput').focus()
    })
}

function execute_add_user() {
    $('#addUserModal').modal('hide')
    const email = document.querySelector('#emailInput').value.trim()
    const data = { email, password: '' }
    if (document.querySelector('#adminOpt').checked) {
        data.role = 'admin'
    } else {
        data.role = 'student'
    }

    crud.domain = 'users'
    const success_text = 'Usuário registrado com sucesso. ' +
        'Ele precisa fazer o primeiro acesso para confirmar o e-mail e definir  a senha.'
    const error_text = 'Não foi possível registrar um usuário com o email "' + email + '".'
    crud.create({ data, success_text, error_text }, () => {
        if (document.querySelector('#inviteOpt').checked) {
            // Invite AJAX
        }
        RefreshInfo()  // as in panel.js
    })
}

function remove_user() {
    const email = prompt('Por favor, digite o e-mail que identifica o usuário a ser removido. ' +
    'Observe que, se o usuário for um aluno registrado no sistema, ele ainda assim conseguirá fazer login.')
    if (email) {
        ask_before_damage('Deseja realmente remover o usuário "' + email + '"?', () => {
        crud.domain = 'users'
            crud.remove({
                data: { email },
                success_text: 'Usuário removido com sucesso.',
                error_text: 'Não foi possível remover o usuário "' + email + '".'
            }, () => {
                RefreshInfo()
            })
        })
    }
}