export const SousTypeDocumentSerivce = (function () {
  function create(data) {
    return $.ajax({
      url: '/typedocument/soustypedocuments/create/',
      method: 'POST',
      data
    });
  }

  function update(id, data) {
    return $.ajax({
      url: `/typedocument/soustypedocuments/${id}/update/`,
      method: 'POST',
      data
    });
  }

  function deleteItem(id) {
    return $.ajax({
      url: `/typedocument/soustypedocuments/${id}/delete/`,
      method: 'POST'
    });
  }

  function fetchAll() {
    return $.ajax({
      url: '/typedocument/soustypedocuments/all/',
      method: 'GET'
    });
  }

  return { create, update, deleteItem, fetchAll };
})();
