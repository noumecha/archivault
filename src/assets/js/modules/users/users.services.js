export const UserService = (function () {
  function fetchAll() {
    return $.get('/users/users/all/');
  }
  function save(formData) {
    return $.post('/users/users/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/users/users/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
