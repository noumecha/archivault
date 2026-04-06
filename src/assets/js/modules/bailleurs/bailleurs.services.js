// modules/bailleurs/bailleurs.services.js
export const BailleurService = (function () {
  function fetchAll() {
    return $.get('/bailleurs/bailleurs/all/');
  }
  function save(formData) {
    return $.post('/bailleurs/bailleurs/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/bailleurs/bailleurs/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
