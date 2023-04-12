var items = $(".item_class");
$(items).filter(function() {
    $(this).click(function(){
          console.log('-----------N e x t r e q u e s t------------');
          let button_id = $(this).attr('id');
          let item_template = 'item_';
          console.log(button_id);

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
                console.log('Success!');
                //$("#items_content").html(html);
            },
            error: function(html){
                console.log('Error!');
            }
          });

    });

});
