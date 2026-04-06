export const TypeDocumentService = (function () {
  function create(data) {
    return $.ajax({
      url: '/typedocument/typedocuments/create/',
      method: 'POST',
      data
    });
  }

  function update(id, data) {
    return $.ajax({
      url: `/typedocument/typedocuments/${id}/update/`,
      method: 'POST',
      data
    });
  }

  function deleteItem(id) {
    return $.ajax({
      url: `/typedocument/typedocuments/${id}/delete/`,
      method: 'POST'
    });
  }

  function fetchAll() {
    return $.ajax({
      url: '/typedocument/typedocuments/all/',
      method: 'GET'
    });
  }

  return { create, update, deleteItem, fetchAll };
})();
