// modules/divisions/divisions.services.js

import { ApiClient } from '../../../helpers/api-client.js';

export const DivisionService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/divisions/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/divisions/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/divisions/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/divisions/${id}/update`, {
      method: 'PATCH', // PATCH = mise à jour partielle
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/divisions/${id}/delete`, {
      method: 'DELETE'
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    const errors = {};
    if (data.nom && data.nom.length <= 0) errors.nom = ['Le nom de la division est requis'];
    if (!data.ministere) errors.ministere = ['Le ministère est requis'];
    if (!data.direction_generale) errors.direction_generale = ['Le nom de la direction générale est requis'];
    if (data.description_division && data.description_division.length <= 0)
      errors.description_division = ['La description de la division est requise'];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  // ── Actions personnalisées ───────────────────────────────────────────────
  toggleStatus(id) {
    return ApiClient.request(`/api/divisions/${id}/toggle-status/`, {
      method: 'POST'
    });
  },

  bulkToggleStatus(ids) {
    return ApiClient.request('/api/divisions/bulk-toggle-status/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/divisions/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
