// src/assets/js/modules/users/auth.controller.js
import { AuthService } from './auth.services.js';
import { showAlertMessage, startLoader, closeLoader } from '../../helpers/utils.js';

export const AuthController = {
  init() {
    $('#formAuthentication').on('submit', async e => {
      startLoader('#login-loader');
      e.preventDefault();
      const data = {
        username: $('#username').val(),
        password: $('#password').val()
      };

      try {
        const res = await AuthService.login(data);
        window.location.href = '/';
      } catch (err) {
        console.error('Erreur capturée:', err);
        const message = err.error || 'Erreur serveur';
        showAlertMessage(message, '#message-show', $('#login-loader'));
      }
    });
  }
};

AuthController.init();
