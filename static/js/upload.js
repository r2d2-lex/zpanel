var img_items = $(".img_class");
$(img_items).filter(function() {
    const $that = $(this);
    $that.click(function(){
          const button_id = $that.attr('id');
          const img_template = 'img_';
          const host_id = button_id.replace(img_template,'');

          $('#uploadModal').modal('show');
          $('#Host-Id').val(host_id);
          $("#uploadModal").find('h5').empty();
          $("#uploadModal").find('h5').text('Загрузка изображения для: ' + host_id);
    });
});

$("#upload_id").change(function(){
	if (window.FormData === undefined) {
		alert('В вашем браузере FormData не поддерживается')
	} else {
		var formData = new FormData();
		formData.append('image', $("#upload_id")[0].files[0]);

        const data_id = $('#Host-Id').val();
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
					console.log('success: upload',msg.success)
				} else {
					showMessage('#result_upload', 'Неудачная операция: '+msg.error, 'alert-warning');
					console.log('error: upload',msg.error)
				}
			}
		});
	}
});

$('#uploadModal').on('hide.bs.modal', function (e) {
  show();
})
