function pollJobStatus(job_id, finished_callback, failed_callback) {
    if (!failed_callback && !finished_callback) {
        return
    }
    $.ajax({
        method: 'GET',
        url: '/batch/job_status/' + job_id,
        success: (response) => {
            if (failed_callback && response.status === 'failed') {
                failed_callback(response)
            } else if (finished_callback && response.status === 'finished') {
                finished_callback(response)
            } else {
                setTimeout(() => {
                    pollJobStatus(job_id, finished_callback, failed_callback)
                }, 5000);
            }
        }
    })
}

function pick_file_and_send(domain, update=false) {
    const $form = document.getElementById('fileUploadForm')
    $form.file.onchange = () => {
        const formData = new FormData()
        if (update) {
            formData.append('update', 'true')
        }
        formData.append('file', $form.file.files[0])
        filename = $form.file.value.split('\\').pop();
        $.ajax({
            method: 'POST',
            url: '/batch/upload/' + domain,
            data: formData,
            contentType: false,
            processData: false,
            success: (result) => {
                note('Arquivo "' + filename + '" foi enviado com sucesso e está sendo processado.')
                pollJobStatus(result.job_id, (response) => {
                    if ('error' in response) {
                        return bad_note('Erro ao processar o arquivo "' + filename + '". ', response.error)
                    }
                    note('Arquivo "' + filename + '" foi processado com sucesso.')
                    RefreshInfo()
                })
            },
            error: (error) => bad_note('Não foi possível enviar o arquivo "' + filename + '".', error),
            complete: () => {
                $form.reset()
            }
        })
    }
    $form.file.click()
}

function ask_before_damage(msg, ajax_damage) {
    bootbox.confirm({
        message: msg,
        buttons: {
            cancel: {
                label: 'Sim, excluir TUDO!',
                className: 'btn-danger'
            },
            confirm: {
                label: 'NÃO',
                className: 'btn-light'
            }
        },
        callback: function (result) {
            if (result == false) {
                ajax_damage()
            }
        }
    })
}

function clear_table(domain) {
    ask_before_damage('Deseja realmente apagar a tabela "' + domain + '"?', () => {
        var password = prompt("Por favor, digite a senha: ")
        if (password != null) {
            $.ajax({
                method: 'DELETE',
                url: '/admin/table/' + domain,
                data: JSON.stringify({ password }),
                 contentType: 'application/json',
                success: (response) => {
                    note('Tabela "' + domain + '" foi apagada com sucesso.')
                    RefreshInfo();  // defined in panel.js
                },
                error: (error) => bad_note('Não foi possível apagar os dados da tabela "' + domain + '".', error)
            })
        }
    })
}

function download(link, basename) {
    $.ajax({
        method: 'GET',
        url: '/batch/check/' + link,
        success: () => {
            const a_link = document.createElement('a')
            a_link.href = '/batch/download/' + link
            a_link.download = basename
            a_link.style.display = 'none'
            document.body.appendChild(a_link)
            a_link.click()
        },
        error: () => {
            bad_note('Erro ao processar o arquivo "' + basename + '" para download.')
        }
    })


}

function download_click_handler(e) {
    const target = e.currentTarget;
    e.preventDefault();
    const basename = target.download
    const domain = target.getAttribute('data-domain')
    if (basename && domain) {
        target.disabled = 'disabled'
        $.ajax({
            method: 'GET',
            url: '/batch/request/' + domain,
            success: (result) => {
                note('O arquivo "' + basename + '" está sendo processado, e o download iniciará em breve.')
                pollJobStatus(result.job_id, (response) => {
                    download(response.basename, basename)
                }, (response) => {
                    bad_note('Erro ao processar o arquivo "' + basename + '" para download.', response.error)
                })
            },
            error: (result) => {
                bad_note('O arquivo "' + basename + '" não pôde ser processado para download no momento.')
            },
            complete: () => {
                target.removeAttribute('disabled')
            }
        })
    }
}

function upload_preferences() {
    const $form = document.getElementById('fileUploadForm')
    $form.file.onchange = () => {
        filename = $form.file.files[0].name
        ask_before_damage('Essa operação irá apagar TODAS as preferências registradas no banco de dados e irá ' +
            'substituí-las com o conteúdo do arquivo que você escolheu (' + filename + '). ' +
            'Deseja realmente prosseguir?', () => {
            var password = prompt("Por favor, digite a senha: ")
            if (password != null) {
                const formData = new FormData()
                formData.append('update', 'true')
                formData.append('password', password)
                formData.append('file', $form.file.files[0])
                filename = $form.file.value.split('\\').pop();
                $.ajax({
                    method: 'POST',
                    url: '/batch/upload_preferences',
                    data: formData,
                    contentType: false,
                    processData: false,
                    success: (result) => {
                        note('O arquivo com as preferências foi enviado com sucesso e está sendo processado.')
                        pollJobStatus(result.job_id, (response) => {
                            note('O arquivo com as preferências foi processado com sucesso.')
                            RefreshInfo()
                        }, (response) => {
                            bad_note('Erro ao processar o arquivo com as preferências.', response.error)
                        })
                    },
                    error: (error) => bad_note('Não foi possível enviar o arquivo com as preferências.', error),
                    complete: () => {
                        $form.reset()
                    }
                })

            }
        })
    }
    $form.file.click()
}