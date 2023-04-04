$("#js-file").change(function(){
	if (window.FormData === undefined) {
		alert('В вашем браузере FormData не поддерживается')
	} else {
		var formData = new FormData();
		formData.append('image', $("#js-file")[0].files[0]);

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
					$("#js-file").hide();
					$('#result').html(msg.success);
				} else {
					$('#result').html(msg.error);
				}
			}
		});
	}
});
