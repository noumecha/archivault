// modules/users/profile.controller.js
import { ApiClient } from '../../helpers/api-client.js';
import { UserService } from './users.services.js';
import { showToast } from '../../helpers/utils.js';
import { UserUi } from './users.ui.js';
export const ProfileController = {
  init() {
    this.handleAvatarUpload();
    this.handleProfileUpdate();
    this.handlePasswordUpdate();
  },

  // 1. Upload Avatar
  handleAvatarUpload() {
    $('#upload').on('change', async e => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = e => $('#uploadedAvatar').attr('src', e.target.result);
      reader.readAsDataURL(file);

      const formData = new FormData();
      formData.append('avatar', file);

      try {
        const res = await UserService.updateUserAvatar(formData);
        showToast(res.message || 'Photo de profil mise à jour', 'success');
      } catch (err) {
        console.error("Erreur lors de l'upload:", err);
        showToast(err.data?.message || "Erreur lors de l'upload", 'danger');
      }
    });
  },

  // 2. Mise à jour Infos (Nom, Email, etc.)
  handleProfileUpdate() {
    $('#formAccountSettings').on('submit', async e => {
      e.preventDefault();
      const $form = $(e.target);
      const data = {
        first_name: $form.find('#firstName').val(),
        last_name: $form.find('#lastName').val(),
        email: $form.find('#email').val()
      };

      try {
        const res = await UserService.updateUserProfil(data);
        UserUi.showSuccess(res.message || 'Profil mis à jour avec succès', '#form-success');
      } catch (err) {
        console.error('Erreur lors de la mise à jour:', err);
        UserUi.showError(err.data?.message || 'Erreur lors de la mise à jour', '#form-error');
      }
    });
  },

  // 3. Mise à jour Mot de Passe
  handlePasswordUpdate() {
    $('#formPasswordSettings').on('submit', async e => {
      e.preventDefault();
      const data = {
        old_password: $('#old_password').val(),
        new_password: $('#new_password').val(),
        confirm_password: $('#confirm_password').val()
      };

      try {
        const res = await UserService.changeUserPassword(data);
        UserUi.showSuccess(res.message || 'Mot de passe modifié', '#form-success');
      } catch (err) {
        console.error('Erreur lors de la mise à jour:', err);
        e.target.reset();
        const msg = err.data?.non_field_errors || err.data?.old_password || 'Erreur de validation';
        UserUi.showError(msg, '#form-error');
      }
    });
  }
};

ProfileController.init();
