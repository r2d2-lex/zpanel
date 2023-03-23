$(document).ready(function() {
   $('.inputClass').each(function() {
      $(this).click(function(){
          let hostid = $(this).attr('id');

          let del_template = 'del_';
          let mdf_template = 'mdf_';

          let selectName = '#select_'+hostid;
          console.log('selectName:', selectName);

          let del_result = hostid.search(del_template);
          console.log('del_:', del_result);
          let mdf_result = hostid.search(mdf_template);
          console.log('mdf_:', mdf_result);

          let select_val = $(selectName).val();

          console.log('ID:', hostid);
          console.log('select_val:', select_val);

          $.ajax({
            type : 'post',
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