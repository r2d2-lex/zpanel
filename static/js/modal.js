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
    contentType: "application/json",
    success: function (html) {
        $("#modal_content").html(html);
    },
    error: function(html){
    }
    })


    });
});
