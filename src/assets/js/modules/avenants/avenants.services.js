// modules/avenants/avenants.services.js
export const AvenantService = (function () {
  function fetchAll() {
    return $.get('/avenants/avenants/all/');
  }
  function save(formData) {
    return $.post('/avenants/avenants/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/avenants/avenants/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
