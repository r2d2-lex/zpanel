$(document).ready(function(){
    $('a[data-bs-toggle=modal], button[data-toggle=modal]').click(function () {
    var data_id = '';
    if (typeof $(this).data('id') !== 'undefined') {
      data_id = $(this).data('id');
    }

    $('#exampleModalLabel').empty();
    $('#exampleModalLabel').text('Загрузить изображение для Host-ID: '+data_id);
    $('#Host-Id').val(data_id);
    });
});


$("#upload_id").change(function(){
	if (window.FormData === undefined) {
		alert('В вашем браузере FormData не поддерживается')
	} else {
		var formData = new FormData();
		formData.append('image', $("#upload_id")[0].files[0]);

        let data_id = $('#Host-Id').val();
        console.log('DATA ID inside upload: ', data_id);
        formData.append('host-id', data_id);

		$.ajax({
			type: "POST",
			url: '/upload/',
			cache: false,
			contentType: false,
			processData: false,
			data: formData,
			dataType : 'json',
			success: function(msg){
			    console.log(msg);
				if (msg.error == '') {
					$("#upload_id").hide();
					$('#result').html(msg.success);
					console.log('SUCCESS',msg.success)
				} else {
					$('#result').html(msg.error);
					console.log('ERROR',msg.error)
				}
			}
		});
	}
});

$('#exampleModalLabel').on('hide.bs.modal', function (e) {
  console.log('CLOSE MODAL WINDOW');
  show();
})

function show() {
  $.ajax({
   url: "/settings/",
   cache: false,
   success: function(html) {
    $("#settings").html(html);
   }
  });
}
