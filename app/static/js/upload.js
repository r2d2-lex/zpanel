var img_items = $(".img_class");
$(img_items).filter(function() {
    const $that = $(this);
    $that.click(function(){
          $("#upload_id").show();
          $('#result_upload').empty();

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

        const host_id = $('#Host-Id').val();
        formData.append('host-id', host_id);

        const img_id = 'img_src_' + host_id;
        const page_url = window.location.href;
        const img_location = 'static/images/';
        const img_path = page_url + img_location;

		$.ajax({
			type: "POST",
			url: '/image/upload/',
			cache: false,
			contentType: false,
			processData: false,
			data: formData,
			dataType : 'json',
			success: function(msg){
				if (msg.error == '') {
					$("#upload_id").hide();
					showMessage('#result_upload', 'Успешная сохранено: '+msg.success, 'alert-success');
					console.log('success: upload ', msg.success);
					// Меняем изображение элемента без перезагрузки страницы
					$('#' + img_id).attr({
					        src: img_path + msg.success,
					        width: 85,
					        height: 85,
					    });
				} else {
					showMessage('#result_upload', 'Неудачная операция: '+msg.error, 'alert-warning');
					console.log('error: upload',msg.error)
				}
			}
		});
	}
});
