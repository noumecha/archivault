// modules/users/users.controller.js

import { UserService } from './users.services.js';
import { UserUi } from './users.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../helpers/utils.js';

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
      res.current_page = parseInt(params.page) || 1;
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
      toggleBulkButton('.user-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.user-checkbox', function () {
      toggleBulkButton('.user-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#users-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = UserController.getCurrentParams();
      params.page = page;

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
    $('#refresh-button').on('click', () => {
      this.loadUsers();
      resetForm('#utilisateur-search-form');
      $('#clearSearch').trigger('click');
    });

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

    // activation/desaction groupée
    $(document).on('click', '#btn-bulk-toggle-status', function (e) {
      e.preventDefault();
      const ids = $('.user-checkbox:checked')
        .map(function () {
          return $(this).val();
        })
        .get();

      if (ids.length === 0) {
        return;
      }

      const modalElement = document.getElementById('bulk-toggle-status-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-bulk-toggle-status-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-bulk-toggle-status-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#bulk-toggle-status-loader');
            const res = await UserService.bulkToggleStatus(ids);
            UserUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = UserController.getCurrentParams();
            await UserController.loadUsers(currentParams);
          } catch (err) {
            console.error('Erreur activation/désactivation:', err);
            const message = err.data?.message || 'Erreur lors de la mise à jour du statut';
            UserUi.showError(message, '#bulk-toggle-status-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-toggle-status-loader');
          }
        });
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
        // on update the password is no required
        if (!rawData.password1) {
          delete rawData.password1;
          delete rawData.password2;
        }
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
          resetForm($form);
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
  }
};
