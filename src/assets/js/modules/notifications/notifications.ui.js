export const NotificationUI = {
  renderBadge(count) {
    const badgeElement = document.getElementById('notification-badge');
    badgeElement.textContent = count;
  },

  renderList(notifications) {}
};
