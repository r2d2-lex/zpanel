$(document).ready(function() {
   $('.inputClass').each(function() {
      $(this).click(function(){
          console.log('-----------N e x t r e q u e s t------------');
          let hostid = $(this).attr('id');

          let del_template = 'del_';
          let mdf_template = 'mdf_';

          let method = 'POST';
          let operation = 'СОХРАНЕН: '+hostid;
          // Вычисляем select id например: #select_1234
          let selectName = '#select_'+hostid;

          if (hostid.indexOf(del_template) >=0){
                hostid = hostid.replace(del_template,'')
                selectName = selectName.replace(del_template,'')
                method = 'DELETE';
                operation = 'УДАЛЕН: '+hostid;
          } else if (hostid.indexOf(mdf_template) >=0){
                hostid = hostid.replace(mdf_template,'')
                selectName = selectName.replace(mdf_template,'')
                method = 'PATCH';
                operation = 'ИЗМЕНЕН: '+hostid;
          }
          let select_val = $(selectName).val();

          //console.log('ID:', hostid);
          //console.log('select_val:', select_val);

          $.ajax({
            type : method,
            url: '/monitor/hosts/',
            data: JSON.stringify({
                'hostid': hostid,
                'column': select_val,
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

