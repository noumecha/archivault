// modules/notifications/notifications.service.js

import { ApiClient } from '../../helpers/api-client.js';

export const NotificationService = {
  // ── Récupération des données ─────────────────────────────────────────────

  /**
   * Récupère la liste des notifications (gère la pagination et les filtres via params)
   */
  fetchAll(params = {}) {
    // Conversion explicite des booléens en 0/1 pour Django
    if (params.hasOwnProperty('is_read')) {
      params.is_read = params.is_read ? 1 : 0;
    }
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/notifications/?${query}`);
  },

  /**
   * Récupère uniquement le nombre de notifications non lues
   * Utile pour mettre à jour le badge de la navbar sans recharger toute la liste
   */
  fetchUnreadCount() {
    return ApiClient.request('/api/notifications/unread-count/');
  },

  // ── Actions unitaires ───────────────────────────────────────────────────

  /**
   * Marque une notification spécifique comme lue
   */
  markAsRead(id) {
    return ApiClient.request(`/api/notifications/${id}/read/`, {
      method: 'PATCH'
    });
  },

  /**
   * Supprime une notification définitivement
   */
  remove(id) {
    return ApiClient.request(`/api/notifications/${id}/delete/`, {
      method: 'DELETE'
    });
  },

  /**
   * supression de masse
   */
  bulkDelete(ids) {
    return ApiClient.request('/api/notifications/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  },

  // ── Actions de masse ─────────────────────────────────────────────────────

  /**
   * Marque l'ensemble des notifications de l'utilisateur comme lues
   */
  markAllAsRead() {
    return ApiClient.request('/api/notifications/read-all/', {
      method: 'POST'
    });
  },

  // ── Utilitaires ──────────────────────────────────────────────────────────

  /**
   * Formate les données pour l'affichage (optionnel, peut être fait dans l'UI)
   * Permet par exemple de mapper les catégories à des icônes RemixIcon
   */
  getCategoryIcon(category) {
    const icons = {
      tache: 'ri-checkbox-line',
      circulation: 'ri-node-tree',
      systeme: 'ri-settings-4-line'
    };
    return icons[category] || 'ri-notification-3-line';
  },

  /**
   * Validation locale (si tu prévois un formulaire de création manuelle de notification,
   * bien que ce soit géré par les signaux côté serveur)
   */
  validate(data) {
    const errors = {};
    if (!data.titre) errors.titre = ['Le titre est requis'];
    if (!data.message) errors.message = ['Le message est requis'];

    if (Object.keys(errors).length > 0) {
      throw { data: { errors, message: 'Validation locale échouée' } };
    }
    return true;
  }
};
