 function show() {
  $.ajax ({
   url: "/panel",
   cache: false,
   success: function(html) {
    $("#content").html(html);
   }
  });
}

 $(document).ready(function() {
  show();
  setInterval ('show()',5000);
 });
