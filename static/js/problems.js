$(document).ready(function() {
    $('a[data-bs-toggle=modal], button[data-toggle=modal]').click(function () {
    let data_id = '';
    if (typeof $(this).data('id') !== 'undefined') {
      data_id = $(this).data('id');
    }

    $('#exampleModalLabel').empty();

    $.ajax({
    url: '/monitor/hosts/'+data_id,
    cache: false,
    dataType: 'json',
    contentType: "application/json",
    success: function (data) {
            $('#exampleModalLabel').text('Host name: '+ data.name + ' host id: ' + data.host_id);
    },
    error: function(data){
        console.log('/monitor/hosts/ error');
        $('#exampleModalLabel').text('Host ID: '+data_id);
    }
    });

    $.ajax({
    url: '/errors/'+data_id,
    cache: false,
    success: function (html) {
        $("#modal_content").html(html);
    },
    error: function(html){
    }
    });


    });
});
