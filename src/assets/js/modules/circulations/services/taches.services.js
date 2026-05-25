// modules/circulations/services/taches.services.js

import { ApiClient } from '../../../helpers/api-client.js';

export const TacheService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/taches/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/taches/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/taches/create/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, formData) {
    return ApiClient.request(`/api/taches/${id}/update/`, {
      method: 'PATCH',
      body: formData
    });
  },

  logConsultation(id) {
    return ApiClient.request(`/api/taches/${id}/log-consultation/`, {
      method: 'POST'
    });
  },

  remove(id) {
    return ApiClient.request(`/api/taches/${id}/delete/`, {
      method: 'DELETE'
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    const errors = {};

    if (!data.titre || data.titre.trim().length === 0) errors.titre = ['Le titre est requis'];
    if (!data.document) errors.document = ['Le document associé est requis'];
    if (!data.assignee_a) errors.assigne_a = ['Le destinataire est requis'];
    if (!data.priorite) errors.priorite = ['La priorité est requise'];
    if (!data.statut) errors.statut = ['Le statut est requis'];
    if (!data.date_echeance) errors.date_echeance = ["La date d'échéance est requise"];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  // ── Actions personnalisées ───────────────────────────────────────────────
  bulkDelete(ids) {
    return ApiClient.request('/api/taches/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  },

  updateStatus(id, status) {
    return ApiClient.request(`/api/taches/${id}/update-status/`, {
      method: 'PATCH',
      body: JSON.stringify({ statut: status })
    });
  }
};
