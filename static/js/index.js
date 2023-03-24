$(document).ready(function() {
   $('.inputClass').each(function() {
      $(this).click(function(){
          let hostid = $(this).attr('id');

          let del_template = 'del_';
          let mdf_template = 'mdf_';

          let method = 'POST';
          // Вычисляем select id например: #select_1234
          let selectName = '#select_'+hostid;
          console.log('selectName:', selectName);

          if (hostid.indexOf(del_template) >=0){
                hostid = hostid.replace(del_template,'')
                selectName = selectName.replace(del_template,'')
                method = 'DELETE';
                console.log(del_template, ':  ', hostid);
                console.log('OPERATION DELETE!');
          } else if (hostid.indexOf(mdf_template) >=0){
                hostid = hostid.replace(mdf_template,'')
                selectName = selectName.replace(mdf_template,'')
                method = 'PATCH';
                console.log(mdf_template, ': ', hostid);
                console.log('OPERATION MODIFY!');
          }
          let select_val = $(selectName).val();

          console.log('ID:', hostid);
          console.log('select_val:', select_val);

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
            console.log('SUCESS!!!');

          },
          /* ---------------------------- success end -------------------------------- */
            error: function(data){
                console.log('ERRORR!!!');
                $('#id_status').empty();
                console.log(data);
            }
          })
          /* ---------------------------- ajax end -------------------------------- */

      });
   });
});