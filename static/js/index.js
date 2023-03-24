
$(document).ready(function() { show() });

 function show() {
  $.ajax ({
   url: "/settings",
   cache: false,
   success: function(html) {
    $("#settings").html(html);
   }
  });
}
