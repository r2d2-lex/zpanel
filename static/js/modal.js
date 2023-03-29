$(document).ready(function() {
    $('a[data-bs-toggle=modal], button[data-toggle=modal]').click(function () {
    let data_id = '';
    if (typeof $(this).data('id') !== 'undefined') {
      data_id = $(this).data('id');
    }

    $.ajax({
    type : 'POST',
    url: '/errors/',
    data: JSON.stringify({
        'hostid': data_id,
        'column': 1,
    }),
    cache: false,
    //Your server-side code returns HTML snippet with 200 OK status. jQuery was expecting valid JSON and therefore
    // fires the error callback complaining about parseerror
    // !!!! ----dataType: 'json',
    contentType: "application/json",
    success: function (html) {
        $("#modal_content").html(html);
        console.log('POST errors/ SUCESS!!!');
    },
    error: function(html){
        console.log('POST errors/ error!!!');
        console.log(html);
    }
    })


    });
});
