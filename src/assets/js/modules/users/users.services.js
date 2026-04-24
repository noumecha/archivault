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

  updateUserAvatar(formData) {
    return ApiClient.request('/api/users/profile/update/', {
      method: 'PATCH',
      body: formData
    });
  },

  updateUserProfil(data) {
    return ApiClient.request('/api/users/profile/update/', {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  changeUserPassword(data) {
    return ApiClient.request('/api/users/profile/change-password/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // methode pour valider les données du formulaire
  validate(data) {
    const errors = {};
    if (data.username && data.username.length <= 0) errors.username = ["Le nom d'utilisateur est requis"];
    if (data.first_name && data.first_name.length <= 0) errors.first_name = ['Le prénom est requis'];
    if (data.last_name && data.last_name.length <= 0) errors.last_name = ['Le nom est requis'];
    //if (!data.email) errors.email = ["L'email est requis"];
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.email = ["L'email n'est pas valide"];
    }
    if (data.password1 && data.password1.length <= 0) errors.password = ['Le mot de passe est requis'];
    if (data.password1 && data.password1.length < 8) errors.password = ['Trop court (minimum 8 caractères)'];
    // if the role is set to responsable or superviseur or gestionnaire, the cellule field is required
    if (['responsable', 'superviseur', 'gestionnaire'].includes(data.role) && !data.cellule) {
      errors.cellule = ['La cellule est requise pour ce rôle'];
    }
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

  passwordValidate(data) {
    const errors = {};
    if (!data.old_password) errors.old_password = ['Le mot de passe actuel est requis'];
    if (!data.new_password) errors.new_password = ['Le nouveau mot de passe est requis'];
    if (data.new_password && data.new_password.length < 8) errors.new_password = ['Trop court (minimum 8 caractères)'];
    if (data.new_password && data.new_password === data.old_password)
      errors.new_password = ["Le nouveau mot de passe doit être différent de l'ancien"];
    if (data.new_password && data.confirm_password && data.new_password !== data.confirm_password)
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

  bulkToggleStatus(ids) {
    return ApiClient.request('/api/users/bulk-toggle-status/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  },

  bulkDelete(ids) {
    return ApiClient.request('/api/users/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  }
};
