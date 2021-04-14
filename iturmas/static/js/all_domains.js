var search_string = '';
var offset = 0;
var total = 0;

// Function search() and variable domain must be defined in specific domain js file.

$("#search_string").keyup(function(event) {
    if (event.keyCode === 13) {
        event.stopPropagation();
        console.log("ENTER on search_string");
        search_string = $('#search_string').val();
        search(0); // must be defined in specific domain js file
    }
});

function topFunction() {
  document.body.scrollTop = 0;              // For Safari
  document.documentElement.scrollTop = 0;   // For Chrome, Firefox, IE and Opera
}

var crud = function() {};

crud.create = function(data, success_callback=function(){},
    success_text='Item inserido com sucesso.',
    error_text='Problema na inserção do item.') {
    $.ajax({method: "POST",
        url: '/' + domain + '/insert',
        data: data,
        success: function(result) {
            new Noty({
                type: 'success',
                theme: 'bootstrap-v4',
                text: success_text,
                timeout: 3000
            }).show();
            success_callback();
            search();
        },
        error: function(result) {
            console.log(result);
            new Noty({
                type: 'error',
                theme: 'bootstrap-v4',
                text: error_text + ' Resposta do servidor: ' + result.responseJSON.msg,
                timeout: 3000
            }).show();
        }
    });
};

crud.read = function(code, success) {
        $.ajax({method: "POST",
        url: '/' + domain + '/get',
        data: {
            code: code,
        },
        success: success,
        error: function(result) {
            console.log(result);
            new Noty({
                type: 'error',
                theme: 'bootstrap-v4',
                text: 'Item não encontrado. Isto não deveria acontecer. Por favor, contacte o administrador.',
                timeout: 3000
            }).show();
        }
    });
};

crud.update = function(data) {
    $.ajax({method: "POST",
        url: '/' + domain + '/insert',
        data: data,
        success: function(result) {
            new Noty({
                type: 'success',
                theme: 'bootstrap-v4',
                text: 'Cadastro atualizado com sucesso.',
                timeout: 3000
            }).show();
            crud.cancel_edit();
            search();
        },
        error: function(result) {
            console.log(result);
            new Noty({
                type: 'error',
                theme: 'bootstrap-v4',
                text: 'Problemas na atualização dos dados.',
                timeout: 3000
            }).show();
        }
    });
};

crud.delete = function(code,
    success_text='Item excluído com sucesso.',
    error_text='Não foi possível excluir o item desejado.') {

    $.ajax({method: "POST",
        url: '/' + domain + '/delete',
        data: {
            code:  code,
        },
        success: function(result) {
            new Noty({
                type: 'success',
                theme: 'bootstrap-v4',
                text: success_text,
                timeout: 3000
            }).show();
            search();
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
};

crud.search = function(arbitrary_offset=offset,
    items_text="Itens cadastrados", extra="") {

    offset = arbitrary_offset - (arbitrary_offset % max_per_page);
    $.ajax({method: "POST",
        url: '/search/' + domain + '',
        data: { search_string: search_string, offset: offset, max_per_page: max_per_page, extra: extra},
        success: function(result) {
            total = result.total;
            offset = result.offset;
            var items = result['items'];
            $('#entries').empty()
            var txtHeader;
            if (search_string == '') {
                txtHeader = $('<h3 class="my-4"></h3>').text(items_text);
            } else {
                txtHeader = $('<h3 class="my-4"></h3>').text("Resultados da busca '" + search_string + "'");
            }
            $('#entries').append(txtHeader);
            var n = items.length;
            if (!n) {
                var txtNothing = $('<h4 class="my-4"></h4>').html("<i>Nada foi encontrado.</i>");
                $('#entries').append(txtNothing);
            }
            else {
                $('#entries').append(pagination(total, offset));
                $('#entries').append(result.entries);
                $('#entries').append(pagination(total, offset));
                topFunction();
            }
        }
    });
};
