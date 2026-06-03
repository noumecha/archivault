import { AvenantService } from '../services/avenant.service.js';
import { AvenantUi } from '../ui/avenant.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const AvenantController = {
  async init() {
    await this.loadData();
    this.bindEvents();
  },
  async loadData(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await AvenantService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      AvenantUi.renderTable(res);
    } catch (err) {
      AvenantUi.showError('Erreur chargement');
    } finally {
      closeLoader('#table-loader');
    }
  },
  bindEvents() {
    $(document).on('change', '#check-all-avenants', function () {
      $('.item-checkbox').prop('checked', $(this).is(':checked'));
      toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container');
    });
    $(document).on('change', '.item-checkbox', () =>
      toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container')
    );

    // Recherche & filtres
    let searchTimer;
    $('#avenant-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(this.getCurrentParams()), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadData();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadData();
      resetForm('#avenant-search-form');
      $('#clearSearch').trigger('click');
    });

    $('#add-button').on('click', () => AvenantUi.renderForm(null));

    $(document).on('click', '[data-action="edit"]', async e => {
      const id = $(e.currentTarget).data('id');
      try {
        const res = await AvenantService.fetchOne(id);
        new bootstrap.Modal(document.getElementById('create-avenant-modal')).show();
        AvenantUi.renderForm(res.data);
      } catch (err) {
        AvenantUi.showError('Erreur');
      }
    });

    $('#avenantForm').on('submit', async e => {
      e.preventDefault();
      const id = $('#update-id').val();
      const data = Object.fromEntries(new FormData(e.target));
      try {
        await AvenantService.validate(data);
        const res = id ? await AvenantService.update(id, data) : await AvenantService.create(data);
        AvenantUi.showSuccess(res.message, '#form-success');
        setTimeout(() => {
          bootstrap.Modal.getInstance(document.getElementById('create-avenant-modal')).hide();
          this.loadData();
        }, 1500);
      } catch (err) {
        AvenantUi.showError(err.data?.errors || 'Erreur', '#form-error');
      }
    });

    $(document).on('click', '[data-action="delete"]', e => {
      const id = $(e.currentTarget).data('id');
      const modal = new bootstrap.Modal(document.getElementById('delete-avenant-modal'));
      modal.show();
      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          try {
            await AvenantService.remove(id);
            modal.hide();
            this.loadData();
          } catch (err) {
            AvenantUi.showError('Erreur', '#delete-form-error');
          }
        });
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.item-checkbox:checked')
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
            const res = await AvenantService.bulkDelete(ids);
            AvenantUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = AvenantController.getCurrentParams();
            await AvenantController.loadData(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            AvenantUi.showError(message, '#bulk-delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-delete-loader');
          }
        });
    });
  },

  handleSearch() {
    const params = Object.fromEntries(
      $('#avenant-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadData(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#avenant-search-form')
        .serializeArray()
        .filter(i => i.value)
        .map(i => [i.name, i.value])
    );
  }
};
AvenantController.init();
