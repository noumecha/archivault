// modules/administration/services/ministere.service.js

import { ApiClient } from '../../../helpers/api-client.js';
import { MinistereUi } from '../ui/ministere.ui.js';

export const MinistereService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/ministeres/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/ministeres/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/ministeres/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/ministeres/${id}/update`, {
      method: 'PATCH', // PATCH = mise à jour partielle
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/ministeres/${id}/delete`, {
      method: 'DELETE'
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    const errors = {};
    if (!data.nom || data.nom.length <= 0) errors.nom = ['Le nom est requis'];
    if (!data.code || data.code.length <= 0) errors.code = ['Le code est requis'];
    if (!data.abrevation || data.abrevation.length <= 0) errors.abrevation = ["L'abréviation est requise"];
    if (!data.description_ministere || data.description_ministere.length <= 0)
      errors.description_ministere = ['La description du ministere est requise'];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  // ── Actions personnalisées ───────────────────────────────────────────────
  bulkDelete(ids) {
    return ApiClient.request('/api/ministeres/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
