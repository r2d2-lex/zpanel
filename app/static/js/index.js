
$(document).ready(function() { show() });

 function show() {
  $.ajax({
   url: "/settings/",
   cache: false,
   success: function(html) {
    $("#settings").html(html);
   }
  });
}

function showMessage(id, message, classAlert) {
    $(id).empty();
    let div = document.createElement('div');
    div.classList.add("alert");
    div.classList.add(classAlert);
    div.setAttribute("role", "alert");
    div.innerHTML = message;
    $(id).append(div);
}
