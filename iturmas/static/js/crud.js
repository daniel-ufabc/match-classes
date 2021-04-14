// must set crud.domain before using crud methods...

function AJAX_wrapper({ domain, data, success_text, success_callback, error_text, error_callback, method }) {
    $.ajax({
        method,
        url: '/crud/' + domain,
        data,
        success: function(result) {
            if (success_text) {
                note(success_text)
            }
            if (success_callback) {
                success_callback(result);
            }
        },
        error: function(result) {
            console.log(result);
            if (error_text) {
                bad_note(error_text)
            }
            if (error_callback) {
                error_callback(result);
            }
        }
    })
}

var crud = {
    domain: 'undefined',
    create({ data, success_text, error_text }, success_callback) {
        if (success_text === undefined) {
            success_text = 'Item inserido com sucesso.'
        }
        if (error_text === undefined) {
            error_text = 'Problema na inserção do item.'
        }
        AJAX_wrapper({
            domain: this.domain,
            method: 'POST',
            data,
            success_text,
            error_text,
            success_callback
        })

    },
    read({ data, success_text, error_text }, success_callback) {
        if (error_text === undefined) {
            error_text = 'Item não encontrado.'
        }
        // The value of success_text defaults to undefined (so no Noty displayed),
        //     which is the expected behaviour if a read operation succeeds.
        AJAX_wrapper({
            domain: this.domain,
            data,
            success_callback,
            success_text,
            error_text
        })
    },
    update({ data, success_text, error_text }, success_callback) {
        if (success_text === undefined) {
            success_text = 'Cadastro atualizado com sucesso.'
        }
        if (error_text === undefined) {
            error_text = 'Problemas na atualização dos dados.'
        }
        data = data || {}
        data.update = true
        AJAX_wrapper({
            domain: this.domain,
            method: 'PATCH',
            data,
            success_text,
            success_callback,
            error_text
        })
    },
    remove({ data, success_text, error_text}, success_callback) {
        if (success_text === undefined) {
            success_text = 'Item excluído com sucesso.'
        }
        if (error_text === undefined) {
            error_text = 'Não foi possível excluir o item desejado.'
        }
        AJAX_wrapper({
            domain: this.domain,
            method: 'DELETE',
            data,
            success_text,
            error_text,
            success_callback
        })
    }
}

function validate(data) {
    if ('properties' in data) {
        try {
            obj = JSON.parse(data.properties)
        }
        catch (err) {
            bad_note('O campo propriedades deve conter um JSON válido.')
            return false
        }
    }
    return true
}