// documents.services.js
import { ApiClient } from '../../helpers/api-client.js';

export const DocumentService = {
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/documents/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/documents/${id}/`);
  },

  remove(id) {
    return ApiClient.request(`/api/documents/${id}/delete/`, {
      method: 'DELETE'
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/documents/${id}/update/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  checkConflict(file) {
    return ApiClient.request(`/api/documents/check-conflict/?filename=${encodeURIComponent(file.name)}`);
  },

  upload(formData, onProgress) {
    // On utilise ApiClient.request mais on doit gérer le XHR pour la progression
    // Note: Dans une version plus avancée, ApiClient pourrait supporter les callbacks de progression
    return $.ajax({
      url: '/api/documents/upload-multiple/',
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
      },
      xhr: function () {
        const xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener('progress', e => {
          if (e.lengthComputable) onProgress((e.loaded / e.total) * 100);
        });
        return xhr;
      }
    });
  },

  validate(data) {
    const errors = {};
    if (!data.titre) errors.titre = ['Le titre est requis'];
    if (!data.type_document) errors.type_document = ['Le type de document est requis'];
    if (Object.keys(errors).length > 0) throw { data: { errors } };
    return true;
  }
};
