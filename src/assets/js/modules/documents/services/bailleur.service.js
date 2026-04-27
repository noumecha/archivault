// modules/documents/services/bailleur.service.js
import { ApiClient } from '../../../helpers/api-client.js';

export const BailleurService = {
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/bailleurs/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/bailleurs/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/bailleurs/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/bailleurs/${id}/update`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/bailleurs/${id}/delete`, {
      method: 'DELETE'
    });
  },

  validate(data) {
    const errors = {};
    if (!data.libelle) errors.libelle = ['Le libellé est requis'];
    if (!data.abrevation) errors.abrevation = ["L'abbréviation est requise"];
    if (!data.cellule) errors.cellule = ["L'unité de traitement est requise"];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/bailleurs/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
