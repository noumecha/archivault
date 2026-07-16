// modules/divisions/divisions.controller.js

import { DivisionService } from '../services/division.service.js';
import { DivisionUi } from '../ui/division.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const DivisionController = {
  async init() {
    await this.loadDatas();
    this.bindEvents();
  },

  // ─── Chargement des utilisateurs ────────────────────────────────────────

  async loadDatas(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await DivisionService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      DivisionUi.renderTable(res);

      $('.division-checkbox').prop('checked', false);
      toggleBulkButton('.division-checkbox:checked', '#bulk-actions-container', '#check-all-divisions');
    } catch (err) {
      console.error('Erreur:', err);
      DivisionUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-divisions', function () {
      const isChecked = $(this).is(':checked');
      $('.division-checkbox').prop('checked', isChecked);
      toggleBulkButton('.division-checkbox:checked', '#bulk-actions-container', '#check-all-divisions');
    });

    $(document).on('change', '.division-checkbox', function () {
      toggleBulkButton('.division-checkbox:checked', '#bulk-actions-container', '#check-all-divisions');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#divisions-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = DivisionController.getCurrentParams();
      params.page = page;

      await DivisionController.loadDatas(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#division-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadDatas();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadDatas();
      // reset filter forms
      resetForm('#division-search-form');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => DivisionUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await DivisionService.fetchOne(id);
        new bootstrap.Modal(document.getElementById('create-division-modal')).show();
        DivisionUi.renderForm(res.data);
      } catch (err) {
        DivisionUi.showError('Erreur chargement division');
      }
    });

    // activation/desaction groupée
    $(document).on('click', '#btn-bulk-toggle-status', function (e) {
      e.preventDefault();
      const ids = $('.division-checkbox:checked')
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
            const res = await DivisionService.bulkToggleStatus(ids);
            DivisionUi.showSuccess(res.message);
            modalInstance.hide();

            $('.division-checkbox').prop('checked', false);
            toggleBulkButton('.division-checkbox:checked', '#bulk-actions-container', '#check-all-divisions');

            const currentParams = DivisionController.getCurrentParams();
            await DivisionController.loadDatas(currentParams);
          } catch (err) {
            console.error('Erreur activation/désactivation:', err);
            const message = err.data?.message || 'Erreur lors de la mise à jour du statut';
            DivisionUi.showError(message, '#bulk-toggle-status-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-toggle-status-loader');
          }
        });
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.division-checkbox:checked')
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
            const res = await DivisionService.bulkDelete(ids);
            DivisionUi.showSuccess(res.message);
            modalInstance.hide();

            $('.division-checkbox').prop('checked', false);
            toggleBulkButton('.division-checkbox:checked', '#bulk-actions-container', '#check-all-divisions');

            const currentParams = DivisionController.getCurrentParams();
            await DivisionController.loadDatas(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            DivisionUi.showError(message, '#bulk-delete-form-error');
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
        await DivisionService.toggleStatus(id);
        DivisionUi.showSuccess('Statut mis à jour');
        await this.loadDatas(this.getCurrentParams());
      } catch (err) {
        DivisionUi.showError(err.data?.message || 'Erreur');
      }
    });

    // Supprimer
    $(document).on('click', '[data-action="delete"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      const modalElement = document.getElementById('delete-division-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await DivisionService.remove(id);

            modalInstance.hide();
            DivisionUi.showSuccess('Division supprimé avec succès');

            await this.loadDatas(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer cette division';
            DivisionUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#divisionForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#divisionForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());

      try {
        const id = $('#update-id').val();
        let response;
        if (id) {
          response = await DivisionService.update(id, rawData);
        } else {
          response = await DivisionService.create(rawData);
        }
        DivisionUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-division-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadDatas(this.getCurrentParams());
          resetForm($form);
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        DivisionUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#division-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadDatas(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#division-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};
DivisionController.init();
