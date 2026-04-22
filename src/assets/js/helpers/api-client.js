// helpers/api-client.js
import { getCookie } from './utils.js';
export const ApiClient = {
  async request(url, options = {}) {
    const defaults = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      }
    };

    const config = { ...defaults, ...options };

    const response = await fetch(url, config);
    let data = {};
    try {
      data = await response.json();
    } catch (e) {
      data = { error: 'Erreur de réponse serveur' };
    }

    if (!response.ok) {
      return Promise.reject(data);
    }

    return data;
  }
};
