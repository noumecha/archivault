// modules/documents/services/theme.service.js
import { ApiClient } from '../../../helpers/api-client.js';

export const ThemeService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/themes/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/themes/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/themes/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/themes/${id}/update`, {
      method: 'PATCH', // PATCH = mise à jour partielle
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/themes/${id}/delete`, {
      method: 'DELETE'
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    const errors = {};
    if (data.libelle && data.libelle.length <= 0) errors.libelle = ['Le libelle du thème est requis'];
    if (data.description_theme && data.description_theme.length <= 0)
      errors.description_theme = ['La description_theme est requise'];
    if (data.cellule && data.cellule.length <= 0) errors.cellule = ['La cellule est requise'];
    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/themes/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
