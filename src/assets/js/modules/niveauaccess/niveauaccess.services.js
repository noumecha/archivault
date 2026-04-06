export const NiveauAccessService = (function () {
  function fetchAll() {
    return $.get('/niveauaccess/niveauaccesss/all/');
  }
  function save(formData) {
    return $.post('/niveauaccess/niveauaccesss/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/niveauaccess/niveauaccesss/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
