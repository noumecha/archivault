export const NotificationService = {
  async getUnread() {
    const response = await fetch('/api/notifications/unread/');
    return await response.json();
  },
  async markAsRead(id) {
    return await fetch(`/api/notifications/${id}/read/`, { method: 'POST' });
  }
};
