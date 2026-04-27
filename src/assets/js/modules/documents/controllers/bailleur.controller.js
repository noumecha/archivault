// modules/documents/controllers/bailleur.controller.js
import { BailleurService } from '../services/bailleur.service.js';
import { BailleurUi } from '../ui/bailleur.ui.js';
import { startLoader, closeLoader, toggleBulkButton } from '../../../helpers/utils.js';

export const BailleurController = {
  async init() {
    await this.loadData();
    this.bindEvents();
  },

  async loadData(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await BailleurService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      BailleurUi.renderTable(res);
    } catch (err) {
      BailleurUi.showError('Erreur lors du chargement des bailleurs');
    } finally {
      closeLoader('#table-loader');
    }
  },

  bindEvents() {
    // Sélection multiple
    $(document).on('change', '#check-all-bailleurs', function () {
      $('.item-checkbox').prop('checked', $(this).is(':checked'));
      toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.item-checkbox', () =>
      toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container')
    );

    // Pagination
    $(document).on('click', '#bailleurs-pagination .page-link', async e => {
      e.preventDefault();
      const page = $(e.currentTarget).data('page');
      if (page) await this.loadData({ ...this.getCurrentParams(), page });
    });

    // Recherche et filtres
    let searchTimer;
    $('#bailleur-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.loadData(this.getCurrentParams()), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadData();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadData();
      // reset filter forms
      $('#bailleur-search-form').trigger('reset');
      $('#clearSearch').trigger('click');
    });

    // Modal Création
    $('#add-button').on('click', () => BailleurUi.renderForm(null));

    // Modal Édition
    $(document).on('click', '[data-action="edit"]', async e => {
      const id = $(e.currentTarget).data('id');
      try {
        const res = await BailleurService.fetchOne(id);
        BailleurUi.renderForm(res.data);
        new bootstrap.Modal(document.getElementById('create-bailleur-modal')).show();
      } catch (err) {
        BailleurUi.showError('Erreur de chargement du bailleur');
      }
    });

    // Suppression groupée
    $(document).on('click', '#btn-bulk-delete', () => {
      const ids = $('.item-checkbox:checked')
        .map(function () {
          return $(this).val();
        })
        .get();
      if (!ids.length) return;

      const modal = new bootstrap.Modal(document.getElementById('bulk-delete-modal'));
      modal.show();

      $('#confirm-bulk-delete-btn')
        .off('click')
        .on('click', async () => {
          try {
            startLoader('#bulk-delete-loader');
            await BailleurService.bulkDelete(ids);
            modal.hide();
            this.loadData();
            BailleurUi.showSuccess('Bailleurs supprimés avec succès');
          } catch (err) {
            BailleurUi.showError('Erreur suppression groupée', '#bulk-delete-form-error');
          } finally {
            closeLoader('#bulk-delete-loader');
          }
        });
    });

    // Suppression unique
    $(document).on('click', '[data-action="delete"]', e => {
      const id = $(e.currentTarget).data('id');
      const modal = new bootstrap.Modal(document.getElementById('delete-bailleur-modal'));
      modal.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          try {
            startLoader('#delete-loader');
            await BailleurService.remove(id);
            modal.hide();
            this.loadData();
            BailleurUi.showSuccess('Bailleur supprimé avec succès');
          } catch (err) {
            BailleurUi.showError('Erreur suppression', '#delete-form-error');
          } finally {
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumission du formulaire
    $('#bailleurForm').on('submit', async e => {
      e.preventDefault();
      const id = $('#update-id').val();
      const data = Object.fromEntries(new FormData(e.target));

      try {
        await BailleurService.validate(data);
        const res = id ? await BailleurService.update(id, data) : await BailleurService.create(data);

        BailleurUi.showSuccess(res.message || 'Succès', '#form-success');
        setTimeout(() => {
          bootstrap.Modal.getInstance(document.getElementById('create-bailleur-modal')).hide();
          this.loadData(this.getCurrentParams());
        }, 1500);
      } catch (err) {
        const errors = err.data?.errors || err.data?.message || 'Erreur inconnue';
        BailleurUi.showError(errors, '#form-error');
      }
    });
  },

  handleSearch() {
    const params = Object.fromEntries(
      $('#bailleur-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadData(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#bailleur-search-form')
        .serializeArray()
        .filter(item => item.value)
        .map(item => [item.name, item.value])
    );
  }
};

BailleurController.init();
