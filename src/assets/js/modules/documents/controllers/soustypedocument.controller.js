// modules/documents/controllers/soustypedocument.controller.js
import { SousTypeDocumentService } from '../services/soustypedocument.service.js';
import { SousTypeDocumentUi } from '../ui/soustypedocument.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const SousTypeDocumentController = {
  async init() {
    await this.loadData();
    this.bindEvents();
  },

  async loadData(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await SousTypeDocumentService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      SousTypeDocumentUi.renderTable(res);
      $('.item-checkbox').prop('checked', false);
      toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container', '#check-all-soustypes');
    } catch (err) {
      SousTypeDocumentUi.showError('Erreur chargement des données');
    } finally {
      closeLoader('#table-loader');
    }
  },

  bindEvents() {
    // Bulk actions
    $(document).on('change', '#check-all-soustypes', function () {
      const isChecked = $(this).is(':checked');
      $('.item-checkbox').prop('checked', isChecked);
      toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container', '#check-all-soustypes');
    });

    $(document).on('change', '.item-checkbox', () =>
      toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container', '#check-all-soustypes')
    );

    // Pagination
    $(document).on('click', '#soustypedocuments-pagination .page-link', async e => {
      e.preventDefault();
      const page = $(e.currentTarget).data('page');
      if (page) await this.loadData({ ...this.getCurrentParams(), page });
    });

    // Search & filters
    let timer;
    $('#soustypedocument-search-form').on('input change', 'input, select', () => {
      clearTimeout(timer);
      timer = setTimeout(() => this.loadData(this.getCurrentParams()), 300);
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadData();
      // reset filter forms
      resetForm('#soustypedocument-search-form');
      $('#clearSearch').trigger('click');
    });

    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadData();
    });

    $('#refresh-button').on('click', () => this.loadData());

    // Actions Modal
    $('#add-button').on('click', () => SousTypeDocumentUi.renderForm(null));

    $(document).on('click', '[data-action="edit"]', async e => {
      const id = $(e.currentTarget).data('id');
      try {
        const res = await SousTypeDocumentService.fetchOne(id);
        new bootstrap.Modal(document.getElementById('create-soustypedocument-modal')).show();
        SousTypeDocumentUi.renderForm(res.data);
      } catch (err) {
        SousTypeDocumentUi.showError('Erreur de chargement');
      }
    });

    // Bulk Delete
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
            await SousTypeDocumentService.bulkDelete(ids);
            modal.hide();

            $('.item-checkbox').prop('checked', false);
            toggleBulkButton('.item-checkbox:checked', '#bulk-actions-container', '#check-all-soustypes');
            this.loadData();
            SousTypeDocumentUi.showSuccess('Sous-types supprimés');
          } catch (err) {
            SousTypeDocumentUi.showError('Erreur suppression groupée', '#bulk-delete-form-error');
          } finally {
            closeLoader('#bulk-delete-loader');
          }
        });
    });

    // Single Delete
    $(document).on('click', '[data-action="delete"]', e => {
      const id = $(e.currentTarget).data('id');
      const modal = new bootstrap.Modal(document.getElementById('delete-soustypedocument-modal'));
      modal.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          try {
            startLoader('#delete-loader');
            await SousTypeDocumentService.remove(id);
            modal.hide();
            this.loadData();
            SousTypeDocumentUi.showSuccess('Sous-type supprimé');
          } catch (err) {
            SousTypeDocumentUi.showError('Erreur suppression', '#delete-form-error');
          } finally {
            closeLoader('#delete-loader');
          }
        });
    });

    // Form Submit
    $('#soustypedocumentForm').on('submit', async e => {
      e.preventDefault();
      const id = $('#update-id').val();
      const data = Object.fromEntries(new FormData(e.target));

      try {
        await SousTypeDocumentService.validate(data);
        const res = id ? await SousTypeDocumentService.update(id, data) : await SousTypeDocumentService.create(data);

        SousTypeDocumentUi.showSuccess(res.message || 'Succès', '#form-success');
        setTimeout(() => {
          bootstrap.Modal.getInstance(document.getElementById('create-soustypedocument-modal')).hide();
          this.loadData(this.getCurrentParams());
        }, 1500);
      } catch (err) {
        const errors = err.data?.errors || err.data?.message || 'Erreur inconnue';
        SousTypeDocumentUi.showError(errors, '#form-error');
      }
    });
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#soustypedocument-search-form')
        .serializeArray()
        .filter(item => item.value)
        .map(item => [item.name, item.value])
    );
  }
};

SousTypeDocumentController.init();
