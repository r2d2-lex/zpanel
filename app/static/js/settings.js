$(document).ready(function() {
   $('.inputClass').each(function() {
      $(this).click(function(){
          console.log('-----------N e x t r e q u e s t------------');
          let host_id = $(this).attr('id');

          const del_template = 'del_';
          const mdf_template = 'mdf_';
          const host_extract_template = 'name_';

          let method = 'POST';
          let operation = ' Сохранение: ' + host_id;
          let selectName = '#select_' + host_id;
          let url_api_prefix = ''

          if (host_id.indexOf(del_template) >=0) {
                host_id = host_id.replace(del_template, '')
                selectName = selectName.replace(del_template, '')
                method = 'DELETE';
                operation = ' Удаление: ' + host_id;
                url_api_prefix = host_id;
          } else if (host_id.indexOf(mdf_template) >=0) {
                host_id = host_id.replace(mdf_template, '')
                selectName = selectName.replace(mdf_template, '')
                method = 'PATCH';
                operation = ' Изменение: ' + host_id;
                url_api_prefix = host_id;
          }

          const host_name = $('#name_' + host_id).attr('name').replace(host_extract_template,'');
          const select_val = $(selectName).val();

          $.ajax({
            type : method,
            url: '/monitor/hosts/' + url_api_prefix,
            data: JSON.stringify({
                'host_id': host_id,
                'column': select_val,
                'name': host_name,
            }),
            dataType: 'json',
            contentType: "application/json",
            /* ---------------------------- success begin -------------------------------- */
            success: function (data) {
            showMessage('#id_status', 'Успешная операция: ' + operation, 'alert-success');
            console.log('/monitor/hosts/: success!'  + operation);
            show();
          },
          /* ---------------------------- success end -------------------------------- */
            error: function(data){
                showMessage('#id_status', 'Неудачная операция: '+ operation, 'alert-warning');
                console.log('/monitor/hosts/: error! ' + operation);
            }
          })
          /* ---------------------------- ajax end -------------------------------- */

      });
   });
});
