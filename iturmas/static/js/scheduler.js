scheduler = {
    ajax({ method, url, data, error_msg }) {
        method = method || 'GET'
        data = data || {}
        $.ajax({
            method,
            url,
            data,
            error: (jqXHR, textStatus, errorThrown) => {
                if (error_msg) {
                    bad_note(error_msg, errorThrown)
                }
            },
            complete: () => {
                RefreshInfo()
            }
        })
    },
    start() {
        $('#executeModal').modal('show')
    },
    stop() {
        this.ajax({
            url: '/match/stop',
            error_msg: 'Não foi possível parar o processo de alocação.'
        })
    },
    reset() {
        this.ajax({
            url: '/match/reset',
            error_msg: 'Não foi possível limpar os dados gerados pelo o processo de alocação.'
        })
    }
}