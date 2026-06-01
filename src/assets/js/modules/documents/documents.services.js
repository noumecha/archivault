// documents.services.js
import { ApiClient } from '../../helpers/api-client.js';

export const DocumentService = {
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/documents/?${query}`);
  },

  checkExists(filename) {
    return ApiClient.request(`/api/documents/check-exists/?filename=${encodeURIComponent(filename)}`);
  },

  bulkCreate(formData) {
    return ApiClient.request('/api/documents/upload-multiple/', {
      method: 'POST',
      body: formData
    });
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/documents/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  },

  create(formData) {
    return ApiClient.request('/api/documents/create/', {
      method: 'POST',
      body: formData
    });
  },

  fetchOne(id) {
    return ApiClient.request(`/api/documents/${id}/`);
  },

  remove(id) {
    return ApiClient.request(`/api/documents/${id}/delete/`, {
      method: 'DELETE'
    });
  },

  update(id, formData) {
    return ApiClient.request(`/api/documents/${id}/update/`, {
      method: 'PATCH',
      body: formData
    });
  },

  checkConflict(filename) {
    return ApiClient.request(`/api/documents/check-conflict/?filename=${encodeURIComponent(filename)}`);
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

  validate(formData) {
    const errors = {};

    // Utilisation obligatoire de .get() pour FormData
    if (!formData.get('titre')) errors.titre = ['Le titre est requis'];
    if (!formData.get('type_document')) errors.type_document = ['Le type de document est requis'];

    // Pour le fichier, on vérifie s'il existe et s'il n'est pas vide
    const fichier = formData.get('fichier');
    if (!fichier || (fichier instanceof File && fichier.size === 0)) {
      // Optionnel : Ne valider le fichier que si on est en mode création (pas d'ID)
      if (!document.getElementById('update-id').value) {
        errors.fichier = ['Le fichier du document est requis'];
      }
    }

    //if (!formData.get('sous_type')) errors.sous_type = ['Le sous type du document est requis'];
    if (!formData.get('cellule')) errors.cellule = ["L'unité de traitement du document est requise"];
    if (!formData.get('etat')) errors.etat = ["L'état du document est requis"];

    if (Object.keys(errors).length > 0) throw { data: { errors } };
    return true;
  }
};
