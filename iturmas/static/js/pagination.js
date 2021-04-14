function pagination({ total, offset, limit, max_pages }) {
    max_pages = parseInt(max_pages)
    if (isNaN(max_pages) || max_pages < 1) {
        max_pages = 10
    }
    offset = offset - (offset % limit);

    /*

    <!--                                               PAGINATION SCHEME                                         -->
    <nav aria-label="Page navigation">
      <ul class="pagination">
        <li class="page-item disabled"><a class="page-link" href="#">Previous</a></li>
        <li class="page-item"><a class="page-link" href="#">1</a></li>
        <li class="page-item active"><a class="page-link" href="#">2 <span class="sr-only">(current)</span></a></li>
        <li class="page-item"><a class="page-link" href="#">3</a></li>
        <li class="page-item"><a class="page-link" href="#">Next</a></li>
      </ul>
    </nav>

    */

    // returns the quotient of a divided by b
    var int_div = (a, b) => (a - (a % b)) / b;

    var curr_page = 1 + int_div(offset, limit);
    var curr_first_page = 1 + (curr_page - 1) - (curr_page - 1) % max_pages;
    var total_pages = 1 + int_div(total - 1, limit);
    var curr_last_page = total_pages >= curr_first_page + max_pages - 1 ? curr_first_page + max_pages - 1 : total_pages;

    if (total_pages == 1) {
        return null;
    }

    var pagination_nav = $('<nav aria-label="Page navigation"></nav>');
    var pagination_ul = $('<ul class="pagination">');
    var pagination_prev;
    if (curr_page == 1) {
        pagination_prev = $('<li class="page-item disabled"></li>');
    } else {
        pagination_prev = $('<li class="page-item"></li>');
    }
    var pagination_prev_a = $('<a class="page-link" href="#"></a>').text('Anterior');
    pagination_prev_a.attr("href", "javascript:search(" + ((curr_page - 2) * limit) + ');');
    pagination_prev.append(pagination_prev_a);
    pagination_ul.append(pagination_prev);

    for (var p = curr_first_page; p <= curr_last_page; p ++) {
        var pagination_li = $('<li class="page-item"></li>');
        var pagination_li_a = $('<a class="page-link" href="#"></a>').text(p);
        if (p == curr_page) {
            pagination_li.addClass("active");
            var text_current = $('<span class="sr-only"></span>').text('(current)');
            pagination_li_a.append(text_current);
        }
        pagination_li_a.attr("href", "javascript:search(" + ((p - 1) * limit) + ');');
        pagination_li.append(pagination_li_a);
        pagination_ul.append(pagination_li);
    }

    var pagination_next = $('<li class="page-item"></li>');;
    var pagination_next_a;
    // console.log("curr_page = " + curr_page + ", total_pages = " + total_pages);
    if (curr_page == total_pages) {
        pagination_next.addClass('disabled');
        pagination_next_a = $('<span class="page-link"></span>').text('Próxima');
    }
    else {
        pagination_next_a = $('<a class="page-link" href="#"></a>').text('Próxima');
        pagination_next_a.attr("href", "javascript:search(" + ((curr_page) * limit) + ');');
    }
    pagination_next.append(pagination_next_a);
    pagination_ul.append(pagination_next);
    pagination_nav.append(pagination_ul);

    return pagination_nav;
}
