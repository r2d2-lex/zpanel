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

        const data_id = $('#Host-Id').val();
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
					showMessage('#result_upload', 'Успешная сохранено: '+msg.success, 'alert-success');
					console.log('SUCCESS',msg.success)
				} else {
					showMessage('#result_upload', 'Неудачная операция: '+msg.error, 'alert-warning');
					console.log('ERROR',msg.error)
				}
			}
		});
	}
});

$('#exampleModal').on('hide.bs.modal', function (e) {
  console.log('CLOSE MODAL WINDOW');
  show();
})
