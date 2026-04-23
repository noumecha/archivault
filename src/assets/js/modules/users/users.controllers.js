// modules/users/users.controller.js

import { UserService } from './users.services.js';
import { UserUi } from './users.ui.js';
import { startLoader, closeLoader } from '../../helpers/utils.js';

export const UserController = {
  async init() {
    await this.loadUsers();
    this.bindEvents();
  },

  // ─── Chargement des utilisateurs ────────────────────────────────────────

  async loadUsers(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await UserService.fetchAll(params);
      console.log('Utilisateurs chargés:', res);
      UserUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      UserUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-users', function () {
      const isChecked = $(this).is(':checked');
      $('.user-checkbox').prop('checked', isChecked);
      this.toggleBulkButton();
    });

    $(document).on('change', '.user-checkbox', function () {
      this.toggleBulkButton();
    });

    // Gestion des clics de pagination
    $(document).on('click', '#users-pagination .page-link', async function (e) {
      e.preventDefault();
      const page = $(this).data('page');
      const pageUrl = $(this).data('page-url');

      let params = UserController.getCurrentParams();
      if (page) params.page = page;

      // Si vous utilisez l'URL complète de DRF (pageUrl), il faut parser le numéro de page
      await UserController.loadUsers(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#utilisateur-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadUsers();
    });

    // Refresh
    $('#refresh-button').on('click', () => this.loadUsers());

    // Ajouter
    $('#add-button').on('click', () => UserUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await UserService.fetchOne(id);
        UserUi.renderForm(res.data);
        new bootstrap.Modal(document.getElementById('create-utilisateur-modal')).show();
      } catch (err) {
        UserUi.showError('Erreur chargement utilisateur');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.user-checkbox:checked')
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
            const res = await UserService.bulkDelete(ids);
            UserUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = UserController.getCurrentParams();
            await UserController.loadUsers(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            UserUi.showError(message, '#bulk-delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-delete-loader');
          }
        });
    });

    // Basculer statut
    $(document).on('click', '[data-action="toggle-status"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        await UserService.toggleStatus(id);
        UserUi.showSuccess('Statut mis à jour');
        await this.loadUsers(this.getCurrentParams());
      } catch (err) {
        UserUi.showError(err.data?.message || 'Erreur');
      }
    });

    // Supprimer
    $(document).on('click', '[data-action="delete"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      const modalElement = document.getElementById('delete-utilisateur-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await UserService.remove(id);

            modalInstance.hide();
            UserUi.showSuccess('Utilisateur supprimé avec succès');

            await this.loadUsers(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer cet utilisateur';
            UserUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#utilisateurForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#utilisateurForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());

      try {
        const id = $('#update-id').val();
        await UserService.validate(rawData);
        const data = {
          ...rawData,
          password: rawData.password1,
          is_active: rawData.is_active === 'on'
        };
        delete data.password1;
        delete data.password2;
        let response;
        if (id) {
          response = await UserService.update(id, data);
        } else {
          response = await UserService.create(data);
        }
        UserUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-utilisateur-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadUsers(this.getCurrentParams());
          $form[0].reset();
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        UserUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#utilisateur-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadUsers(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#utilisateur-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  },

  toggleBulkButton() {
    const selectedCount = $('.user-checkbox:checked').length;
    if (selectedCount > 0) {
      $('#bulk-actions-container').removeClass('d-none');
      $('#selected-count').text(selectedCount);
    } else {
      $('#bulk-actions-container').addClass('d-none');
    }
  }
};
