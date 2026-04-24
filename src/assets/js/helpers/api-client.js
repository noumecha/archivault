// helpers/api-client.js
import { getCookie } from './utils.js';
export const ApiClient = {
  async request(url, options = {}) {
    const csrfToken = getCookie('csrftoken');

    // On ne met le JSON par défaut QUE si ce n'est pas du FormData
    const isFormData = options.body instanceof FormData;
    const headers = {
      ...(!isFormData && { 'Content-Type': 'application/json' }),
      ...options.headers
    };

    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }
    const config = {
      ...options,
      method: options.method || 'GET',
      headers: headers,
      credentials: 'same-origin'
    };
    const response = await fetch(url, config);
    let data = {};
    try {
      data = await response.json();
    } catch (e) {
      data = { error: 'Erreur de réponse serveur' };
    }

    if (!response.ok) {
      const errorPayload = {
        status: response.status,
        data: data
      };
      return Promise.reject(errorPayload);
    }

    return data;
  }
};
