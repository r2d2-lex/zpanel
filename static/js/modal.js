$(document).ready(function() {
    $('a[data-bs-toggle=modal], button[data-toggle=modal]').click(function () {
    let data_id = '';
    if (typeof $(this).data('id') !== 'undefined') {
      data_id = $(this).data('id');
    }
    $('.modal-body #host_id').val(data_id);
    })
});
