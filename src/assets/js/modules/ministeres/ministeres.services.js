// modules/ministeres/ministeres.services.js
export const MinistereService = (function () {
  function fetchAll() {
    return $.get('/ministeres/ministeres/all/');
  }
  function save(formData) {
    return $.post('/ministeres/ministeres/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/ministeres/ministeres/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
