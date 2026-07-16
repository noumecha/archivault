// modules/administration/controllers/ministere.controller.js
import { MinistereService } from '../services/ministere.service.js';
import { MinistereUi } from '../ui/ministere.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const MinistereController = {
  // ─── Initialisation ─────────────────────────────────────────────────────
  async init() {
    await this.loadDatas();
    this.bindEvents();
  },

  // ─── Chargement des ministères ────────────────────────────────────────

  async loadDatas(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await MinistereService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      MinistereUi.renderTable(res);

      $('.ministere-checkbox').prop('checked', false);
      toggleBulkButton('.ministere-checkbox:checked', '#bulk-actions-container', '#check-all-ministeres');
    } catch (err) {
      console.error('Erreur:', err);
      MinistereUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-ministeres', function () {
      const isChecked = $(this).is(':checked');
      $('.ministere-checkbox').prop('checked', isChecked);
      toggleBulkButton('.ministere-checkbox:checked', '#bulk-actions-container', '#check-all-ministeres');
    });

    $(document).on('change', '.ministere-checkbox', function () {
      toggleBulkButton('.ministeres-checkbox:checked', '#bulk-actions-container', '#check-all-ministeres');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#ministeres-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = MinistereController.getCurrentParams();
      params.page = page;

      await MinistereController.loadDatas(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#ministere-search-form').on('input change', 'input, select', () => {
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
      resetForm('#ministere-search-form');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => MinistereUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await MinistereService.fetchOne(id);
        new bootstrap.Modal(document.getElementById('create-ministere-modal')).show();
        MinistereUi.renderForm(res.data);
      } catch (err) {
        MinistereUi.showError('Erreur chargement ministere');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.ministere-checkbox:checked')
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
            const res = await MinistereService.bulkDelete(ids);
            MinistereUi.showSuccess(res.message);
            modalInstance.hide();

            $('.ministere-checkbox').prop('checked', false);
            toggleBulkButton('.ministere-checkbox:checked', '#bulk-actions-container', '#check-all-ministeres');

            const currentParams = MinistereController.getCurrentParams();
            await MinistereController.loadDatas(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            MinistereUi.showError(message, '#bulk-delete-form-error');
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
      const modalElement = document.getElementById('delete-ministere-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await MinistereService.remove(id);

            modalInstance.hide();
            MinistereUi.showSuccess('Ministère supprimé avec succès');

            await this.loadDatas(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer ce ministere';
            MinistereUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#ministereForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#ministereForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());

      try {
        await MinistereService.validate(rawData);
        let response;
        if (id) {
          response = await MinistereService.update(id, data);
        } else {
          response = await MinistereService.create(data);
        }
        MinistereUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-ministere-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadDatas(this.getCurrentParams());
          resetForm($form);
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        MinistereUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#ministere-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadDatas(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#ministere-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};
MinistereController.init();
