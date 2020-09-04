var csrftoken = Cookies.get('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function fetch_search_input_proposal(request, response) {
    $.ajax({
        type: 'GET',
        url: search_url,
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: { 'search_string': request.term },
        success: function (data) {
            console.log('success', data.length);
            response(data);
        },
        error: function (data) {
            console.log('error', data)
        }
    });
}
$(document).ready(function () {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#search_input").autocomplete({
        source: function (request, response) {
            fetch_search_input_proposal(request, response);
        },
        minlength: 0,
        focus: function (event, ui) {
            $("#search_input").val(ui.item.label);
            return false;
        },
        select: function (event, ui) {
            $("#search_input").val(ui.item.label);
            if (ui.item.slug !== '' && ui.item.slug !== null) {
                //saved
                var url_m = movie_detail_url;
                url_m = url_m.replace('0', ui.item.slug);
                $(location).attr('href', url_m);
            } else {
                $.ajax({
                    type: 'POST',
                    url: movie_save_url,
                    contentType: 'application/json; charset=utf-8',
                    dataType: 'json',
                    data: JSON.stringify({ 'imdbid': ui.item.imdbid }),
                    success: function (response) {
                        var response_obj = JSON.parse(response);
                        var url_m = movie_detail_url;
                        url_m = url_m.replace('0', response_obj.slug);
                        $(location).attr('href', url_m);

                    },
                    error: function (response) {
                        // alert the error if any error occured
                        console.log('error', response)
                    }
                });
            }
            // return false;
        }
    }).data('ui-autocomplete')._renderItem = function (ul, item) {
        return $("<li class='ui-autocomplete-row'></li>")
            .data("item.autocomplete", item)
            .append("<img src=" + item.img + "width='50' height='70' style='margin: auto;' />")
            .append('<b>' + item.label + '</b> <span>(' + item.year + ')</span>')
            .appendTo(ul);
    };
    // .autocomplete( "instance" )._renderItem = function( ul, item ) {
    //   return $( "<li>" )
    //     .append("<div class='container'><div class='row'><div class='col col-sm-1 col-md-1 col-lg-1'>")
    //     .append("<img src="+ item.img + " width='50px' height='70px' ></div>")
    //     .append("<div class='col col-sm-4 col-md-4 col-lg-4'><p><b>" + item.label + "</b>")
    //     .append(""+ item.year + ")" + "</p></div></div></div>" )
    //     .appendTo( ul );
    // };

    $('#search_form').on('submit', function (e) {
        $('.loader').prop('hidden', false);
    });
});