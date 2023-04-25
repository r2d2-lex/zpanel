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
          $('#items_id').val(host_id);
          $("#itemsModal").find('h5').empty();
          $("#itemsModal").find('h5').text('Данные для:' + host_id);
          reloadItems(host_id);
    });
});

class Item {
    constructor() {
        this.host_id;
        this.item_name;
        this.item_type;
    }
    getDataFromInput() {
        const id_host_id = '#items_id';
        const id_item_name = '#item_name';
        const id_item_type = '#item_type';
        this.host_id = $(id_host_id).val();
        this.item_name = $(id_item_name).val();
        this.item_type = $(id_item_type).val();
        return 1;
    }
}

// Modal button click!!!
$(document).on("click", "#item_add", function(event){
    console.log('------------ ADD ITEM!!!! -------------------');
    let item = new Item;
    host.getDataFromInput();
    crudItems(item.host_id, item.item_name, item.item_type, 'POST');
});

$(document).on("click", "#item_patch", function(event){
    console.log('------------  PATCH ITEM!!!! -------------------');
    let item = new Item;
    host.getDataFromInput();
    crudItems(item.host_id, item.item_name, item.item_type, 'PATCH');
});

$(document).on("click", "#item_delete", function(event){
    console.log('------------ DELETE ITEM!!!! -------------------');
    let item = new Item;
    host.getDataFromInput();
    crudItems(item.host_id, item.item_name, item.item_type, 'DELETE');
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
            url: '/data-items/'+host_id,
            cache: false,
            success: function (html) {
                $("#items_content").html(html);
                console.log('Success load items!');
            },
            error: function(html){
                console.log('Error load items!');
            }
          });
}
