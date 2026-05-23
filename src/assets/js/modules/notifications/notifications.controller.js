// modules/notifications/notifications.controller.js
import { NotificationService } from './notifications.service.js';
import { NotificationUi } from './notifications.ui.js';
import { startLoader, closeLoader, toggleBulkButton } from '../../helpers/utils.js';

export const NotificationController = {
  async init() {
    // 1. Initialisation de la Navbar (présente partout)
    await this.refreshNavbar();

    // 2. Initialisation de la page de gestion (si présente dans le DOM)
    if ($('#notifications-tbody').length) {
      await this.loadNotifications();
    }

    this.bindEvents();

    // 3. Optionnel : Polling léger pour rafraîchir les notifs toutes les 2 min
    setInterval(() => this.refreshNavbar(), 120000);
  },

  // ─── Chargement des données ──────────────────────────────────────────

  async loadNotifications(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await NotificationService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      NotificationUi.renderTable(res);
    } catch (err) {
      console.error('Erreur chargement notifications:', err);
      NotificationUi.showError('Erreur lors du chargement de la liste');
    } finally {
      closeLoader('#table-loader');
    }
  },

  async refreshNavbar() {
    try {
      // On récupère le compte et les 5 dernières notifications
      const [countRes, listRes] = await Promise.all([
        NotificationService.fetchUnreadCount(),
        NotificationService.fetchAll({ limit: 5, is_read: false })
      ]);

      NotificationUi.renderBadge(countRes.unread_count);
      NotificationUi.renderDropdownList(listRes.results || listRes);
    } catch (err) {
      console.error('Erreur rafraîchissement navbar:', err);
    }
  },

  // ─── Événements ────────────────────────────────────────────────────────

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-notifications', function () {
      const isChecked = $(this).is(':checked');
      $('.notification-checkbox').prop('checked', isChecked);
      toggleBulkButton('.notification-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.notification-checkbox', function () {
      toggleBulkButton('.notification-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#notifications-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = NotificationController.getCurrentParams();
      params.page = page;

      await NotificationController.loadNotifications(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#notification-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadNotifications();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadNotifications();
      // reset filter forms
      $('#notification-search-form').trigger('reset');
      $('#clearSearch').trigger('click');
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.notification-checkbox:checked')
        .map(function () {
          return $(this).val();
        })
        .get();
      if (ids.length === 0) {
        return;
      }

      const modalElement = document.getElementById('bulk-delete-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-bulk-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-bulk-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#bulk-delete-loader');

            console.log('ids : ', ids);
            const res = await NotificationService.bulkDelete(ids);
            NotificationUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = NotificationController.getCurrentParams();
            await NotificationController.loadNotifications(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            NotificationUi.showError(message, '#bulk-delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-delete-loader');
          }
        });
    });

    // Supprimer
    $(document).on('click', '[data-action="delete-notification"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      const modalElement = document.getElementById('delete-notification-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await NotificationService.remove(id);

            modalInstance.hide();
            NotificationUi.showSuccess('Notification supprimé avec succès');

            await this.loadNotifications(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer cet notification';
            NotificationUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // 1. Marquer comme lu (Unitaire) - Gère aussi le clic sur l'item du dropdown
    $(document).on(
      'click',
      '.mark-as-read-btn, .mark-as-read-link, .dropdown-notifications-item, [data-action="view"]',
      async e => {
        const $target = $(e.currentTarget);
        const id = $target.closest('[data-id]').data('id');

        try {
          await NotificationService.markAsRead(id);
          await this.refreshNavbar();
          if ($('#notifications-tbody').length) {
            await this.loadNotifications(this.getCurrentParams());
          }
        } catch (err) {
          console.error('Erreur lecture notification:', err);
        }
      }
    );

    // 2. Tout marquer comme lu
    $(document).on('click', '#mark-all-read-btn, #mark-all-read-navbar', async e => {
      e.preventDefault();
      try {
        let res = await NotificationService.markAllAsRead();
        NotificationUi.showSuccess(
          res.message || 'Toutes les notifications ont été marquées comme lues',
          '#message-show-success'
        );
        await this.refreshNavbar();
        if ($('#notifications-tbody').length) {
          await this.loadNotifications();
        }
      } catch (err) {
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        NotificationUi.showError("Erreur lors de l'opération : ", errorData, '#message-show-error');
      }
    });

    // 4. Pagination (Page de gestion)
    $(document).on('click', '#notifications-pagination .page-link', async e => {
      e.preventDefault();
      const page = $(e.currentTarget).data('page');
      if (!page) return;

      let params = this.getCurrentParams();
      params.page = page;
      await this.loadNotifications(params);
    });
  },

  // ─── Utilitaires ───────────────────────────────────────────────────────

  handleSearch() {
    const params = this.getCurrentParams();
    this.loadNotifications(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#notification-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};

// Lancement automatique
// NotificationController.init();
