import { NotificationService } from './notifications.service.js';
import { NotificationUI } from './notifications.ui.js';

export const NotificationController = {
  init() {
    this.fetchNotifications();
    // Polling toutes les 60 secondes (ou utiliser WebSockets/Channels si besoin)
    setInterval(() => this.fetchNotifications(), 60000);
  },

  async fetchNotifications() {
    try {
      const data = await NotificationService.getUnread();
      NotificationUI.renderBadge(data.count);
      NotificationUI.renderList(data.notifications);
    } catch (error) {
      console.error('Erreur notifications:', error);
    }
  }
};
