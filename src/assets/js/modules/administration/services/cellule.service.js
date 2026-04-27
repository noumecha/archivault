// modules/cellules/cellules.services.js

import { ApiClient } from '../../../helpers/api-client.js';

export const CelluleService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/cellules/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/cellules/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/cellules/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/cellules/${id}/update`, {
      method: 'PATCH', // PATCH = mise à jour partielle
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/cellules/${id}/delete`, {
      method: 'DELETE'
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    const errors = {};
    if (!data.nom) errors.nom = ["Le nom de l'unité de traitement est requis"];
    if (data.description_cellule && data.description_cellule.length <= 0)
      errors.description_cellule = ["La description de l'unité de traitement est requise"];
    if (!data.division) errors.division = ['La division est requise'];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  // ── Actions personnalisées ───────────────────────────────────────────────
  toggleStatusBailleur(id) {
    return ApiClient.request(`/api/cellules/${id}/toggle-accepte-bailleurs/`, {
      method: 'POST'
    });
  },

  bulkToggleStatusBailleur(ids) {
    return ApiClient.request('/api/cellules/toggle-accepte-bailleurs/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/cellules/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
