// modules/documents/services/typedocument.service.js
import { ApiClient } from '../../../helpers/api-client.js';

export const TypeDocumentService = {
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/typedocuments/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/typedocuments/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/typedocuments/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/typedocuments/${id}/update`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/typedocuments/${id}/delete`, {
      method: 'DELETE'
    });
  },

  validate(data) {
    const errors = {};
    if (!data.libelle) errors.libelle = ['Le libellé est requis'];
    if (!data.cellule) errors.cellule = ["L'unité de traitement est requise"];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/typedocuments/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
