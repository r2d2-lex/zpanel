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

          $('#itemsModal').modal('show');
          // Устанавливаем значение input в модальной форме
          $("#itemsModal").find('input[name="items_id"]').val(host_id);

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

// Modal button click!!!
$(document).on("click", "#item_add", function(event){
    console.log('------------ NEW!!!! -------------------');
//    let val2 = $('.modal-body input[name=items_id]').val();
    let host_id = $('#itemsModal').find('input[name="items_id"]').val();
    let item_name = $('#item_name').val();
    let item_type = $('#item_type').val();

    console.log('Host id: ' + host_id + ' Item_Name: ' +  item_name + ' Item_Type: ' + item_type);
});
