// modules/administration/controllers/cellule.controller.js
import { CelluleService } from '../services/cellule.service.js';
import { CelluleUi } from '../ui/cellule.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const CelluleController = {
  async init() {
    await this.loadDatas();
    this.bindEvents();
  },

  // ─── Chargement des utilisateurs ────────────────────────────────────────
  async loadDatas(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await CelluleService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      CelluleUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      CelluleUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────
  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-cellules', function () {
      const isChecked = $(this).is(':checked');
      $('.cellule-checkbox').prop('checked', isChecked);
      toggleBulkButton('.cellule-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.cellule-checkbox', function () {
      toggleBulkButton('.cellule-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#cellules-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = CelluleController.getCurrentParams();
      params.page = page;

      await CelluleController.loadDatas(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#cellule-search-form').on('input change', 'input, select', () => {
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
      resetForm('#cellule-search-form');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => CelluleUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await CelluleService.fetchOne(id);
        new bootstrap.Modal(document.getElementById('create-cellule-modal')).show();
        CelluleUi.renderForm(res.data);
      } catch (err) {
        CelluleUi.showError('Erreur chargement unité de traitement');
      }
    });

    // activation/desaction groupée
    $(document).on('click', '#btn-bulk-toggle-acceptebailleurs', function (e) {
      e.preventDefault();
      const ids = $('.cellule-checkbox:checked')
        .map(function () {
          return $(this).val();
        })
        .get();

      if (ids.length === 0) {
        return;
      }

      const modalElement = document.getElementById('bulk-toggle-acceptebailleurs-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-bulk-toggle-acceptebailleurs-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-bulk-toggle-acceptebailleurs-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#bulk-toggle-acceptebailleurs-loader');
            const res = await CelluleService.bulkToggleStatusBailleur(ids);
            CelluleUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = CelluleController.getCurrentParams();
            await CelluleController.loadDatas(currentParams);
          } catch (err) {
            console.error('Erreur activation/désactivation:', err);
            const message = err.data?.message || 'Erreur lors de la mise à jour du statut';
            CelluleUi.showError(message, '#bulk-toggle-acceptebailleurs-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-toggle-acceptebailleurs-loader');
          }
        });
    });

    // Basculer statut
    $(document).on('click', '[data-action="toggle-acceptebailleurs"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        await CelluleService.toggleStatusBailleur(id);
        CelluleUi.showSuccess('Statut mis à jour');
        await this.loadDatas(this.getCurrentParams());
      } catch (err) {
        CelluleUi.showError(err.data?.message || 'Erreur');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.cellule-checkbox:checked')
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
            const res = await CelluleService.bulkDelete(ids);
            CelluleUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = CelluleController.getCurrentParams();
            await CelluleController.loadDatas(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            CelluleUi.showError(message, '#bulk-delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-delete-loader');
          }
        });
    });

    // Supprimer
    $(document).on('click', '[data-action="delete"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      const modalElement = document.getElementById('delete-cellule-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await CelluleService.remove(id);

            modalInstance.hide();
            CelluleUi.showSuccess('Unité de traitement supprimée avec succès');

            await this.loadDatas(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer cette unité de traitement';
            CelluleUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#celluleForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#celluleForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());

      try {
        const id = $('#update-id').val();
        let response;
        if (id) {
          response = await CelluleService.update(id, rawData);
        } else {
          response = await CelluleService.create(rawData);
        }
        CelluleUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-cellule-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadDatas(this.getCurrentParams());
          resetForm($form);
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        CelluleUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#cellule-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadDatas(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#cellule-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};
CelluleController.init();
