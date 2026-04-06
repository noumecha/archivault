// modules/directiongenerales/directiongenerales.services.js
export const DirectionGeneraleService = (function () {
  function fetchAll() {
    return $.get('/directiongenerales/directiongenerales/all/');
  }
  function save(formData) {
    return $.post('/directiongenerales/directiongenerales/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/directiongenerales/directiongenerales/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
