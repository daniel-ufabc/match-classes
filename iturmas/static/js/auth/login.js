const $form = document.querySelector('form')
const $submitButton = document.querySelector('button[type="submit"]')

const attemptLogin = () => {
    const email = $form.email.value.trim()
    const password = $form.password.value.trim()
    const next = $form.next.value.trim()
    const data = { email, password }

    $.ajax({method: "POST",
        url: "/auth/login",
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: (result) => {
            if (next) {
                location.href = next
            } else {
                location.href = '/'
            }
        },
        error: (jqXHR, textStatus, errorThrown) => {
            $submitButton.removeAttribute('disabled')
            if (jqXHR.status >= 400 && jqXHR.status < 500) {
                bad_note('Email ou senha incorretos.')
            } else {
                console.log(jqXHR.status)
                bad_note('Erro ao tentar conexão com o servidor.')
            }

            $form.password.value = ''
            $form.password.focus()
        }
    });
};

$form.addEventListener('submit', (e) => {
    e.preventDefault()
    $submitButton.setAttribute('disabled', 'disabled')
    attemptLogin()
})

$(document).ready(() => {
    $form.email.focus()
});