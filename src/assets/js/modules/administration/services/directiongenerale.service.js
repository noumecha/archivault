// modules/administration/services/directiongenerales.services.js
import { ApiClient } from '../../../helpers/api-client.js';
import { DirectionGeneraleUi } from '../ui/directiongenerale.ui.js';

export const DirectionGeneraleService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/directiongenerales/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/directiongenerales/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/directiongenerales/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/directiongenerales/${id}/update`, {
      method: 'PATCH', // PATCH = mise à jour partielle
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/directiongenerales/${id}/delete`, {
      method: 'DELETE'
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    const errors = {};
    if (data.username && data.username.length <= 0) errors.username = ["Le nom d'utilisateur est requis"];
    if (data.first_name && data.first_name.length <= 0) errors.first_name = ['Le prénom est requis'];
    if (data.last_name && data.last_name.length <= 0) errors.last_name = ['Le nom est requis'];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  // ── Actions personnalisées ───────────────────────────────────────────────
  bulkDelete(ids) {
    return ApiClient.request('/api/directiongenerales/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
