// modules/documents/controllers/typedocument.controller.js
import { TypeDocumentService } from '../services/typedocument.service.js';
import { TypeDocumentUi } from '../ui/typedocument.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const TypeDocumentController = {
  async init() {
    await this.loadTypes();
    this.bindEvents();
  },

  async loadTypes(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await TypeDocumentService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      TypeDocumentUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      TypeDocumentUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-types', function () {
      const isChecked = $(this).is(':checked');
      $('.type-checkbox').prop('checked', isChecked);
      toggleBulkButton('.type-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.type-checkbox', function () {
      toggleBulkButton('.type-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#typedocuments-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = TypeDocumentController.getCurrentParams();
      params.page = page;

      await TypeDocumentController.loadTypes(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#typedocument-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadTypes();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadTypes();
      resetForm('#typedocument-search-form');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => TypeDocumentUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await TypeDocumentService.fetchOne(id);
        TypeDocumentUi.renderForm(res.data);
        new bootstrap.Modal(document.getElementById('create-typedocument-modal')).show();
      } catch (err) {
        console.error('Error : ', err);
        TypeDocumentUi.showError('Erreur chargement type de document');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.type-checkbox:checked')
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
            const res = await TypeDocumentService.bulkDelete(ids);
            TypeDocumentUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = TypeDocumentController.getCurrentParams();
            await TypeDocumentController.loadTypes(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            TypeDocumentUi.showError(message, '#bulk-delete-form-error');
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
      const modalElement = document.getElementById('delete-typedocument-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await TypeDocumentService.remove(id);

            modalInstance.hide();
            TypeDocumentUi.showSuccess('Type de document supprimé avec succès');

            await this.loadTypes(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer ce type de document';
            TypeDocumentUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#typedocumentForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#typedocumentForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());
      try {
        const id = $('#update-id').val();
        await TypeDocumentService.validate(rawData);
        let response;
        if (id) {
          response = await TypeDocumentService.update(id, rawData);
        } else {
          response = await TypeDocumentService.create(rawData);
        }
        TypeDocumentUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-typedocument-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadTypes(this.getCurrentParams());
          resetForm($form);
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        TypeDocumentUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#typedocument-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadTypes(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#typedocument-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};

TypeDocumentController.init();
