// modules/notifications/ui/notifications.ui.js
import { showAlertMessage, renderPagination } from '../../helpers/utils.js';
import { NotificationService } from './notifications.service.js';

export const NotificationUi = {
  // Couleurs par catégorie
  categoryColors: {
    tache: 'bg-label-info',
    circulation: 'bg-label-warning',
    systeme: 'bg-label-secondary'
  },

  // ─── Gestion du Badge & Dropdown (Navbar) ───────────────────────────────

  /**
   * Met à jour le petit badge rouge sur l'icône de cloche
   */
  renderBadge(count) {
    const badge = $('#notif-badge');
    if (count > 0) {
      badge.text(count).removeClass('d-none');
    } else {
      badge.addClass('d-none');
    }
  },

  /**
   * Rendu de la liste simplifiée dans le dropdown de la navbar
   */
  renderDropdownList(notifications) {
    const container = $('#notif-list-container');
    container.empty();

    if (!notifications || notifications.length === 0) {
      container.html(`
        <li class="list-group-item text-center py-4">
          <small class="text-muted">Aucune nouvelle notification</small>
        </li>
      `);
      return;
    }

    const items = notifications.map(notif => this.createDropdownItem(notif)).join('');
    container.html(items);
  },

  createDropdownItem(notif) {
    const icon = NotificationService.getCategoryIcon(notif.categorie);
    const colorClass = this.categoryColors[notif.categorie] || 'bg-label-primary';
    const readClass = notif.is_read ? '' : 'bg-light border-start border-primary border-3';

    return `
      <li class="list-group-item list-group-item-action dropdown-notifications-item ${readClass}"
        data-id="${notif.id}" onclick="${notif.url_action ? `window.location.href='${notif.url_action}'` : ''}"
        style="${notif.url_action ? 'cursor: pointer;' : ''}">
        <div class="d-flex">
          <div class="flex-shrink-0 me-3">
            <div class="avatar">
              <span class="avatar-initial rounded-circle ${colorClass}">
                <i class="${icon}"></i>
              </span>
            </div>
          </div>
          <div class="flex-grow-1">
            <h6 class="mb-1 small fw-bold">${notif.titre}</h6>
            <small class="mb-1 d-block text-body text-truncate" style="max-width: 200px;">${notif.message}</small>
            <small class="text-muted">${notif.created_at_since} ago</small>
          </div>
          <div class="flex-shrink-0 dropdown-notifications-actions">
            ${notif.is_read ? '' : '<a href="javascript:void(0)" class="mark-as-read-btn"><span class="badge badge-dot bg-primary"></span></a>'}
          </div>
        </div>
      </li>`;
  },

  // ─── Rendu de la table (Page de gestion) ────────────────────────────────

  renderTable(response) {
    const tbody = $('#notifications-tbody'); // Assure-toi que cet ID existe dans ton template
    if (tbody.length === 0) return; // Si on n'est pas sur la page de gestion, on ignore

    tbody.empty();
    const notifications = response.results || response;

    if (!notifications || notifications.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucune notification trouvée</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = notifications.map(notif => this.createNotificationRow(notif)).join('');
    tbody.html(rows);
    this.renderPagination(response);
  },

  createNotificationRow(notif) {
    const icon = NotificationService.getCategoryIcon(notif.categorie);
    const colorClass = this.categoryColors[notif.categorie] || 'bg-label-primary';
    const readClass = notif.is_read ? '' : 'table-light border-start border-primary border-3';

    return `
      <tr class="${readClass}" data-id="${notif.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input notification-checkbox" type="checkbox" value="${notif.id}">
          </div>
        </th>
        <td>
          <div class="avatar avatar-sm me-2">
            <span class="avatar-initial rounded-circle ${colorClass}"><i class="${icon} ri-18px"></i></span>
          </div>
          <small class="text-muted">${notif.created_at_since} ago</small>
        </td>
        <td>
          <div class="d-flex flex-column">
            <span class="fw-bold">${notif.titre}</span>
            <small class="text-muted">${notif.message}</small>
          </div>
        </td>
        <td class="text-center">
            <span class="badge ${colorClass}">${notif.categorie_display}</span>
        </td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              ${
                notif.url_action
                  ? `<a href="${notif.url_action}" class="dropdown-item" data-action="view" data-id="${notif.id}">
                    <i class="ri-eye-line me-1"></i>Détails
                  </a>`
                  : ''
              }
              <a href="#" class="dropdown-item text-danger" data-action="delete-notification" data-id="${notif.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>
            </div>
          </div>
        </td>
      </tr>`;
  },

  renderPagination(data) {
    renderPagination(data, '#notifications-pagination', '#pagination-info');
  },

  // ─── Feedbacks ───────────────────────────────────────────────────────────
  showError(message, id = '#message-show-error', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  },

  showSuccess(message, id = '#message-show-success', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  }
};
