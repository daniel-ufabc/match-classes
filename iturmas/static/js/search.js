// depends on pagination.js being loaded

function topFunction() {
  document.body.scrollTop = 0;              // For Safari
  document.documentElement.scrollTop = 0;   // For Chrome, Firefox, IE and Opera
}

function generic_search({ domain, offset, limit, items_text }) {
    if (items_text === undefined) {
        items_text = "Itens cadastrados"
    }
    limit = parseInt(limit)
    if (isNaN(limit) || limit < 1) {
        limit = 10
    }
    offset = parseInt(offset)
    if (isNaN(offset) || offset < 0) {
        offset = 0
    } else {
        offset = offset - (offset % limit);
    }
    search_string = $('#search_string').val();
    $.ajax({
        method: "GET",
        url: '/search/' + domain,
        data: { search_string, offset, limit },
        success: (result) => {
            // console.log(result);
            total = result.total;
            offset = result.offset;
            $('#entries').empty()
            var txtHeader;
            if (search_string == '') {
                txtHeader = $('<h3 class="my-4"></h3>').text(items_text);
            } else {
                txtHeader = $('<h3 class="my-4"></h3>').text("Resultados da busca '" + search_string + "'");
            }
            $('#entries').append(txtHeader);
            if (!total) {
                var txtNothing = $('<h4 class="my-4"></h4>').html("<i>Nada foi encontrado.</i>");
                $('#entries').append(txtNothing);
            }
            else {
                $('#entries').append(pagination({ total, offset, limit }));
                $('#entries').append(result.entries);
                $('#entries').append(pagination({ total, offset, limit }));
                topFunction();
            }
        },
        error: (result) => {
            // TODO: give feedback in case api call failed...

        }
    });
};
