var auto_refresh = false;
var auto_refresh_timeout = null;

function RefreshInfo() {
    $.ajax({
        url: '/list_stats',
        type: 'GET',
        success: function(data) {
            $('#stats').html(data);
        },
        error: function(data) {
            if (data.status == 400) {
                $('#stats').text('Login required...');
                window.location.href = '/logout';
            }
        }
    });

    $.ajax({
        url: '/list_runs',
        type: 'GET',
        success: function(data){
            $('#runs').html(data);
        }
    });

    var time = new Date();
    var h = "" + time.getHours();
    var m = "" + time.getMinutes();
    var s = "" + time.getSeconds();
    if (h.length == 1) { h = "0" + h; };
    if (m.length == 1) { m = "0" + m; };
    if (s.length == 1) { s = "0" + s; };
    $('#my_datetime').html(h + ":" + m + ":" + s);
    if (auto_refresh) {
        clearTimeout(auto_refresh_timeout);
        auto_refresh_timeout = setTimeout("RefreshInfo()", 5000);
    }
}

RefreshInfo();

$('#auto_refresh_toggle').click(function() {
    auto_refresh = ($(this).attr("aria-pressed") != "true");
    RefreshInfo()
    setTimeout(() => { document.getElementById('auto_refresh_toggle').blur() }, 300)
});

var execute = function() {
    $('#executeModal').modal('hide');
    var max_search = $('#maxSearch').val();
    var default_parameter = document.getElementById('preferredParameter').selectedIndex;
    var success_text = 'O processo de atribuição de turmas foi iniciado com sucesso. Por favor aguarde sua conclusão.';
    var error_text = 'Não foi possível iniciar o processo de atribuição de turmas. Veja o console para mais detalhes.';
    $.ajax({method: "POST",
        url: '/match/start',
        data: { max_search, default_parameter },
        success: function(result) {
            note(success_text)
            if (!auto_refresh)
                $("#auto_refresh_toggle").click();
            else
                setTimeout(RefreshInfo, 500);
        },
        error: function(result) {
            console.log(result)
            bad_note(error_text)
        }
    });
}

var run_assignment_service = function() {
    $('assignClassesModal').modal('show');
};

var stop_assignment_service = function() {
    var success_text = 'Processos de alocação interrompidos.';
    var error_text = 'Não foi possível interromper os processos.';
    $.ajax({method: "POST",
        url: '/kill_processes',
        data: {},
        success: function(result) {
            new Noty({
                type: 'success',
                theme: 'bootstrap-v4',
                text: success_text,
                timeout: 3000
            }).show();
            RefreshInfo();
        },
        error: function(result) {
            console.log(result);
            new Noty({
                type: 'error',
                theme: 'bootstrap-v4',
                text: result.responseText, // previously: error_text
                timeout: 3000
            }).show();
        }
    });
};


var ask_clear_database = function(msg) {
    if (msg === undefined) {
        msg = "Você realmente quer limpar o banco de dados?"
    }
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
                var success_text = 'O banco de dados foi apagado.';
                var error_text = 'Não foi possível apagar o banco de dados.';
                var passwd = prompt("Por favor, digite a senha:");
                if (passwd != null) {
                    $.ajax({method: "POST",
                        url: '/clear_db',
                        data: {
                            passwd: passwd,
                        },
                        success: function(result) {
                            new Noty({
                                type: 'success',
                                theme: 'bootstrap-v4',
                                text: success_text,
                                timeout: 3000
                            }).show();
                             RefreshInfo();
                        },
                        error: function(result) {
                            console.log(result);
                            new Noty({
                                type: 'error',
                                theme: 'bootstrap-v4',
                                text: error_text,
                                timeout: 3000
                            }).show();
                        }
                    });
                }
            }
        }
    });
};