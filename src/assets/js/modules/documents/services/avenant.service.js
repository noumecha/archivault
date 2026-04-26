import { ApiClient } from '../../../helpers/api-client.js';

export const AvenantService = {
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/avenants/?${query}`);
  },
  fetchOne(id) {
    return ApiClient.request(`/api/avenants/${id}/`);
  },
  create(data) {
    return ApiClient.request('/api/avenants/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  update(id, data) {
    return ApiClient.request(`/api/avenants/${id}/update`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },
  remove(id) {
    return ApiClient.request(`/api/avenants/${id}/delete`, { method: 'DELETE' });
  },
  validate(data) {
    const errors = {};
    if (!data.libelle) errors.libelle = ['Le libellé est requis'];
    if (!data.numero) errors.numero = ['Le numéro est requis'];
    if (!data.bailleur) errors.bailleur = ['Le bailleur est requis'];
    if (Object.keys(errors).length > 0) throw { data: { errors } };
    return true;
  },
  bulkDelete(ids) {
    return ApiClient.request('/api/avenants/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
