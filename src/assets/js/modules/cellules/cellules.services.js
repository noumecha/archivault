// modules/cellules/cellules.services.js
export const CelluleService = (function () {
  function fetchAll() {
    return $.get('/cellule/cellules/all/');
  }
  function save(formData) {
    return $.post('/cellule/cellules/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/cellule/cellules/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
