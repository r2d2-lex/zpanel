var items = $(".item_class");
$(items).filter(function() {
    $(this).click(function(){
          $('#items_content').empty();
          $('#items_status').empty();
          $('#item_name').val('');
          $('#item_type').val('');

          let button_id = $(this).attr('id');
          let item_template = 'item_';
          let host_id = button_id.replace(item_template,'');

          $('#itemsModal').modal('show');
          // Устанавливаем значение input в модальной форме
          $("#itemsModal").find('input[name="items_id"]').val(host_id);
          $("#itemsModal").find('h5').empty();
          $("#itemsModal").find('h5').text('Данные для:' + host_id);
          reloadItems(host_id);
    });
});

// Modal button click!!!
$(document).on("click", "#item_add", function(event){
    console.log('------------ ADD ITEM!!!! -------------------');
    let host_id = $('#itemsModal').find('input[name="items_id"]').val();
    let item_name = $('#item_name').val();
    let item_type = $('#item_type').val();

    console.log('Host id: ' + host_id + ' Item_Name: ' +  item_name + ' Item_Type: ' + item_type);
    crudItems(host_id, item_name, item_type, 'POST');
});

$(document).on("click", "#item_patch", function(event){
    console.log('------------  PATCH ITEM!!!! -------------------');
    let host_id = $('#itemsModal').find('input[name="items_id"]').val();
    let item_name = $('#item_name').val();
    let item_type = $('#item_type').val();
    crudItems(host_id, item_name, item_type, 'PATCH');
    console.log('PATCH Host id: ' + host_id + ' Item_Name: ' +  item_name + ' Item_Type: ' + item_type);
});

$(document).on("click", "#item_delete", function(event){
    console.log('------------ DELETE ITEM!!!! -------------------');
    let host_id = $('#itemsModal').find('input[name="items_id"]').val();
    let item_name = $('#item_name').val();
    let item_type = ' ';
    crudItems(host_id, item_name, item_type, 'DELETE');
    console.log('DELETE Host id: ' + host_id + ' Item_Name: ' +  item_name + ' Item_Type: ' + item_type);
});

function crudItems(host_id, item_name, item_type, method) {
        $.ajax({
        type : method,
        url: '/items/',
        data: JSON.stringify({
            'host_id': host_id,
            'name': item_name,
            'value_type': item_type,
        }),
        dataType: 'json',
        contentType: "application/json",
        success: function(data){
            showMessage('#items_status', 'Успешная операция. Метод : '+ method + ' для хоста:' + host_id, 'alert-success');
            console.log('CRUD: Success method: ' + method);
            reloadItems(host_id);
        },
        error: function(data){
            showMessage('#items_status', 'Неудачная операция: '+ host_id + ' Name: ' + item_name, 'alert-danger');
            console.log('CRUD: Error method: ' + method);
        }
    });
}

function reloadItems(host_id) {
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
                console.log('Success load items!');
            },
            error: function(html){
                console.log('Error load items!');
            }
          });
}

function addSelectRecord(item_name, item_type) {
    $('#select_items').append($('<option>', { value: item_name,
        text : 'Элемент: ' + item_name + '; Тип данных:' + item_type,
    }));
}
