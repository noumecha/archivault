// modules/themes/themes.services.js
export const ThemeService = (function () {
  function fetchAll() {
    return $.get('/theme/themes/all/');
  }
  function save(formData) {
    return $.post('/theme/themes/save/', formData);
  }
  function update(id, formData) {
    return $.post(`/theme/themes/update/${id}`, formData);
  }
  return { fetchAll, save, update };
})();
