// src/assets/js/modules/users/auth.controller.js
import { AuthService } from './auth.services.js';
import { showAlertMessage, startLoader, closeLoader } from '../../helpers/utils.js';

export const AuthController = {
  init() {
    $('#formAuthentication').on('submit', async e => {
      e.preventDefault();
      e.stopPropagation();
      startLoader('#login-loader');
      const data = {
        username: $('#username').val(),
        password: $('#password').val()
      };

      try {
        const res = await AuthService.login(data);
        window.location.href = '/';
      } catch (err) {
        const errorMessage = err.data?.error || err.data?.message || 'Identifiants incorrects';
        showAlertMessage(errorMessage, '#message-show', $('#login-loader'));
      } finally {
        closeLoader('#login-loader');
      }
    });
  }
};

AuthController.init();
