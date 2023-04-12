var items = $(".item_class");
$(items).filter(function() {
    $(this).click(function(){
          $('#items_content').empty();
          $('#items_status').empty();

          let button_id = $(this).attr('id');
          console.log(button_id);

          let item_template = 'item_';
          let host_id = button_id.replace(item_template,'');
          console.log(host_id);

          $('#Item-Id').val(host_id);
          $('#itemsModal').modal('show');

          $.ajax({
            type : 'POST',
            url: '/data-items/',
            data: JSON.stringify({
            'host_id': host_id,
             }),
            cache: false,
            contentType: "application/json",
            success: function (html) {
                $("#items_content").html(html);
                console.log('Success!');
            },
            error: function(html){
                console.log('Error!');
            }
          });

    });

});
