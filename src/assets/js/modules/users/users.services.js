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

  // methode pour valider les données du formulare
  validate(data) {
    const errors = {};
    try {
      if (!data.username) errors.username = "Le nom d'utilisateur est requis";
      if (!data.email) errors.email = "L'email est requis";
      if (data.password && data.password.length < 8)
        errors.password = 'Le mot de passe doit contenir au moins 8 caractères';
      if (data.password && !/[A-Z]/.test(data.password))
        errors.password = 'Le mot de passe doit contenir au moins une lettre majuscule';
      if (data.password && !/[a-z]/.test(data.password))
        errors.password = 'Le mot de passe doit contenir au moins une lettre minuscule';
      if (data.password && !/[0-9]/.test(data.password))
        errors.password = 'Le mot de passe doit contenir au moins un chiffre';
      if (data.password && !/[!@#$%^&*]/.test(data.password))
        errors.password = 'Le mot de passe doit contenir au moins un caractère spécial';
      if (data.password && data.password !== data.confirm_password)
        errors.confirm_password = 'Les mots de passe ne correspondent pas';
      if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) errors.email = "L'email n'est pas valide";

      if (Object.keys(errors).length) {
        UserUi.showError(Object.values(errors).flat().join(' | '), '#form-error');
        return;
      }
      UserUi.showError(err.data?.message || 'Erreur de validation', '#form-error');
      return;
    } catch (err) {
      UserUi.showError(err.data?.message || 'Erreur de validation', '#form-error');
      return;
    }
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
