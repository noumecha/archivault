// modules/documents/services/soustypedocument.service.js
import { ApiClient } from '../../../helpers/api-client.js';

export const SousTypeDocumentService = {
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/soustypedocuments/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/soustypedocuments/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/soustypedocuments/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/soustypedocuments/${id}/update`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/soustypedocuments/${id}/delete`, {
      method: 'DELETE'
    });
  },

  validate(data) {
    const errors = {};
    if (!data.libelle) errors.libelle = ['Le libellé est requis'];
    if (!data.type_document) errors.type_document = ['Le type de document est requis'];
    if (Object.keys(errors).length > 0) throw { data: { errors } };
    return true;
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/soustypedocuments/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
