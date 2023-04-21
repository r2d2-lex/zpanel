$(document).ready(function() {
   $('.inputClass').each(function() {
      $(this).click(function(){
          console.log('-----------N e x t r e q u e s t------------');
          let host_id = $(this).attr('id');

          let del_template = 'del_';
          let mdf_template = 'mdf_';
          let host_extract_template = 'name_';

          let method = 'POST';
          let operation = 'СОХРАНЕН: '+host_id;
          // Вычисляем select id например: #select_1234
          let selectName = '#select_'+host_id;

          if (host_id.indexOf(del_template) >=0){
                host_id = host_id.replace(del_template,'')
                selectName = selectName.replace(del_template,'')
                method = 'DELETE';
                operation = 'УДАЛЕН: '+host_id;
          } else if (host_id.indexOf(mdf_template) >=0){
                host_id = host_id.replace(mdf_template,'')
                selectName = selectName.replace(mdf_template,'')
                method = 'PATCH';
                operation = 'ИЗМЕНЕН: '+host_id;
          }
          let select_val = $(selectName).val();

          let host_name = $('#name_'+host_id).attr('name');
          host_name = host_name.replace(host_extract_template,'')
          console.log('HOSTNAME:', host_name);
          //console.log('select_val:', select_val);

          $.ajax({
            type : method,
            url: '/monitor/hosts/',
            data: JSON.stringify({
                'host_id': host_id,
                'column': select_val,
                'name': host_name,
            }),
            dataType: 'json',
            contentType: "application/json",
            /* ---------------------------- success begin -------------------------------- */
            success: function (data) {
            showMessage('#id_status', 'Успешная операция: '+operation, 'alert-success');
            console.log('SUCESS!!!');
            show();
          },
          /* ---------------------------- success end -------------------------------- */
            error: function(data){
                showMessage('#id_status', 'Неудачная операция: '+operation, 'alert-warning');
                console.log('ERRORR!!!');
            }
          })
          /* ---------------------------- ajax end -------------------------------- */

      });
   });
});

