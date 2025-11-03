$(function () {
  showMessage();
  // filtering object by some id
  $(document).on('change', '#id_type_document', function () {
    let typeId = $(this).val();
    $('#id_sous_type').empty().trigger('change');
    if (typeId) {
      $.ajax({
        url: '/soustypes/',
        data: {
          type_id: typeId
        },
        success: function (data) {
          $('#id_sous_type').append('<option value="">---------</option>');
          data.forEach(function (item) {
            let newOption = new Option(item.text, item.id, false, false);
            $('#id_sous_type').append(newOption);
          });
          $('#id_sous_type').trigger('change');
        },
        error: function (xhr, status, error) {
          console.error('Error fetching sous types of documents :', error);
        }
      });
    }
  });
});
