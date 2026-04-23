// modules/users/users.services.js

import { ApiClient } from '../../helpers/api-client.js';
import { UserUi } from './users.ui.js';

export const UserService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/users/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/users/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/users/create', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/users/${id}/update`, {
      method: 'PATCH', // PATCH = mise à jour partielle
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/users/${id}/delete`, {
      method: 'DELETE'
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    console.log('data : ', data);
    const errors = {};
    if (!data.username) errors.username = ["Le nom d'utilisateur est requis"];
    //if (!data.email) errors.email = ["L'email est requis"];
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.email = ["L'email n'est pas valide"];
    }
    if (!data.password1) errors.password = ['Le mot de passe est requis'];
    if (data.password1 && data.password1.length < 8) errors.password = ['Trop court (min 8)'];
    //if (data.password1 && !/[A-Z]/.test(data.password1))
    //  errors.password = ['Le mot de passe doit contenir au moins une lettre majuscule'];
    //if (data.password1 && !/[a-z]/.test(data.password1))
    //  errors.password = ['Le mot de passe doit contenir au moins une lettre minuscule'];
    //if (data.password1 && !/[0-9]/.test(data.password1))
    //  errors.password = ['Le mot de passe doit contenir au moins un chiffre'];
    //if (data.password1 && !/[!@#$%^&*]/.test(data.password1))
    //  errors.password = ['Le mot de passe doit contenir au moins un caractère spécial'];
    if (data.password1 && data.password1 !== data.password2)
      errors.confirm_password = ['Les mots de passe ne correspondent pas'];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  // ── Actions personnalisées ───────────────────────────────────────────────
  toggleStatus(id) {
    return ApiClient.request(`/api/users/${id}/toggle-status/`, {
      method: 'POST'
    });
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/users/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
