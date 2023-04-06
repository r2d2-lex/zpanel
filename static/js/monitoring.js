 function show() {
  $.ajax ({
   url: "/panel/",
   cache: false,
   success: function(html) {
    $('#id_status').empty();
    $("#content").html(html);
   },
   error: function(html){
    showMessage('ошибка соединения с сервером', 'alert-danger');
   }
  });
}

 $(document).ready(function() {
  show();
  setInterval ('show()',5000);
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
