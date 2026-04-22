// src/assets/js/modules/users/auth.services.js
import { ApiClient } from '../../helpers/api-client.js';

export const AuthService = {
  login(credentials) {
    return ApiClient.request('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
  },
  logout() {
    return ApiClient.request('/api/auth/logout/', { method: 'POST' });
  }
};
