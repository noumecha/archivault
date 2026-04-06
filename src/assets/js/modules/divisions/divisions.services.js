// modules/divisions/divisions.services.js
export const DivisionService = (function () {
  function fetchAll() {
    return $.get('/division/divisions/all/');
  }
  function save(formData) {
    return $.post('/division/divisions/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/division/divisions/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
