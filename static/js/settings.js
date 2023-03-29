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
          console.log('selectName:', selectName);

          if (hostid.indexOf(del_template) >=0){
                hostid = hostid.replace(del_template,'')
                selectName = selectName.replace(del_template,'')
                method = 'DELETE';
                operation = 'УДАЛЕН: '+hostid;
                console.log(del_template, ':  ', hostid);
                console.log('OPERATION DELETE!');
          } else if (hostid.indexOf(mdf_template) >=0){
                hostid = hostid.replace(mdf_template,'')
                selectName = selectName.replace(mdf_template,'')
                method = 'PATCH';
                operation = 'ИЗМЕНЕН: '+hostid;
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
            showMessage('Успешная операция: '+operation, 'alert-success');
            console.log('SUCESS!!!');
            show();
          },
          /* ---------------------------- success end -------------------------------- */
            error: function(data){
                showMessage('Неудачная операция: '+operation, 'alert-warning');
                console.log('ERRORR!!!');
                console.log(data);
            }
          })
          /* ---------------------------- ajax end -------------------------------- */

      });
   });
});

function showMessage(message, classAlert) {
    $('#id_status').empty();
    let div = document.createElement('div');
    div.classList.add("alert");
    div.classList.add(classAlert);
    div.setAttribute("role", "alert");
    div.innerHTML = message;
    $('#id_status').append(div);
}

 function show() {
  $.ajax ({
   url: "/settings",
   cache: false,
   success: function(html) {
    $("#settings").html(html);
   }
  });
}
