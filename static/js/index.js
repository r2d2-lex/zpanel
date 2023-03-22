$(document).ready(function() {
   $('.inputClass').each(function() {
      $(this).click(function(){
          let hostid = $(this).attr('id');
          //Do whatever the edit function should do with the id
          let selectName = '#select_'+hostid;
          console.log('selectName:', selectName)

          let select_val = $(selectName).val();

          console.log('ID:', hostid)
          console.log('select_val:', select_val)

          $.ajax({
            method : "POST",
            url: '/monitor/hosts/',
            data: {
                'hostid': hostid,
                'colmn': select_val,
            },
            dataType: 'json',
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