// assumes that all_domains.js has already been executed...

var domain = "pref";

//max_per_page = 5;
//max_pages = 8;

$("#search_string_input").keydown(function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        search_string = $('#search_string_input').val();
        search(0); // must be defined in specific domain js file
    }
});

var save2proceed = function() {
    var sortable = document.getElementById("sortable");
    var n = sortable.children.length;
    if (n < 1 && $("#courseCode").val().trim()) {
        new Noty({
            type: 'error',
            theme: 'bootstrap-v4',
            text: "Selecione pelo menos uma turma para que as preferências sejam salvas.",
            timeout: 3000
        }).show();
        return;
    }
    var sortedIDs = [];
    for (var i = 0; i < n; i ++) { sortedIDs.push(sortable.children[i].id); }
    // for debugging purposes
    // console.log(sortedIDs);
    // return;
    $("#sequence").val(JSON.stringify(sortedIDs));
    document.getElementById("pref_save_form").submit();
}

var toss = function() {
    var f = document.pref_save_form;
    f.action = "/pref/give_up";
    f.submit();
}

var search = function(any_offset=0) {
    max_per_page = 10
    extra = $("#courseCode").val().trim();
    offset = any_offset - (any_offset % max_per_page);
    console.log("Hey! (offset = " + offset + ") extra = " + extra + "; SS = " + search_string);

    $.ajax({method: "POST",
        url: '/pref/search',
        data: { search_string: search_string, offset: offset, max_per_page: max_per_page, extra: extra},
        success: function(result) {
            total = result.total;
            offset = result.offset;
            var items = result['items'];
            $('#entries').empty()
            var txtHeader;
            if (search_string == '') {
                txtHeader = $('<h3 class="my-4"></h3>').text("Todos os itens");
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
                $('#entries').append(pagination({ total, offset, limit: max_per_page }));
                $('#entries').append(result.entries);
                $('#entries').append(pagination({ total, offset, limit: max_per_page }));
                topFunction();
            }
        }
    });
};

function delete_item(ID) {
    var elementExists = document.getElementById(ID);
    if (elementExists === null) {
        // Never happens, because this function is triggered
        //     by a button click inside the element!
        return;
    }

    elementExists.remove();
}

function blink(elem, times, speed) {
    // clearTimeout(timeout);

    if (times <= 0) {
        if ($(elem).hasClass("blink")) { $(elem).removeClass("blink"); }
        return;
    }

    if ($(elem).hasClass("blink")) { $(elem).removeClass("blink"); }
    else { $(elem).addClass("blink"); }

    setTimeout(function () {
        blink(elem, times - 0.5, speed);
    }, speed);
}

// TODO: change this according to https://makandracards.com/makandra/40629-ui-sortable-on-table-rows-with-dynamic-height
function add_item(ID, text) {
    // Perhaps get text from origin...
    var elementExists = document.getElementById(ID);
    if (elementExists === null) {
        var li = document.createElement("li");
        li.className = "ui-state-default";
        li.id = ID;
        li.setAttribute("data-id", ID);
        var img = document.createElement("img");
        img.src = handle_png_url;
        img.setAttribute("draggable", "false");
        li.appendChild(img);
        li.appendChild(document.createTextNode(text));
        li.setAttribute("draggable", "true");
        // li.style.height = "auto";
        var i = document.createElement("i");
        i.className = "material-icons btn-link no-underline";
        i.style.float = "right";
        i.style.cursor = "pointer";
        i.onclick = function() { delete_item(ID); };
        i.appendChild(document.createTextNode("delete"));
        li.appendChild(i);

        var ul = document.getElementById("sortable");
        ul.appendChild(li);
        $("#sortable").sortable('refresh');

        new Noty({
            type: 'success',
            theme: 'bootstrap-v4',
            text: "Item adicionado com sucesso.",
            timeout: 3000
        }).show();

        return;
    }

    // notify the user that the item is already there!!!
    blink(elementExists, 3, 150);
    new Noty({
        type: "error",
        theme: "bootstrap-v4",
        text: "Item já selecionado!",
        timeout: 3000
    }).show();
}
