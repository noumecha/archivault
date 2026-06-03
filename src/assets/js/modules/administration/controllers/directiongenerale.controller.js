// modules/administration/controllers/directiongenerales.controller.js
import { DirectionGeneraleService } from '../services/directiongenerale.service.js';
import { DirectionGeneraleUi } from '../ui/directiongenerale.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const DirectionGeneraleController = {
  async init() {
    await this.loadDatas();
    this.bindEvents();
  },

  // ─── Chargement des directions générales ────────────────────────────────────────

  async loadDatas(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await DirectionGeneraleService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      DirectionGeneraleUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      DirectionGeneraleUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-directiongenerales', function () {
      const isChecked = $(this).is(':checked');
      $('.directiongenerale-checkbox').prop('checked', isChecked);
      toggleBulkButton('.directiongenerale-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.directiongenerale-checkbox', function () {
      toggleBulkButton('.directiongenerale-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#directiongenerales-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = DirectionGeneraleController.getCurrentParams();
      params.page = page;

      await DirectionGeneraleController.loadDatas(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#directiongenerale-search-form').on('input change', 'input, select', () => {
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
      resetForm('#directiongenerale-search-form');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => DirectionGeneraleUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await DirectionGeneraleService.fetchOne(id);
        DirectionGeneraleUi.renderForm(res.data);
        new bootstrap.Modal(document.getElementById('create-directiongenerale-modal')).show();
      } catch (err) {
        DirectionGeneraleUi.showError('Erreur chargement de la direction générale');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.directiongenerale-checkbox:checked')
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
            const res = await DirectionGeneraleService.bulkDelete(ids);
            DirectionGeneraleUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = DirectionGeneraleController.getCurrentParams();
            await DirectionGeneraleController.loadDatas(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            DirectionGeneraleUi.showError(message, '#bulk-delete-form-error');
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
      const modalElement = document.getElementById('delete-directiongenerale-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await DirectionGeneraleService.remove(id);

            modalInstance.hide();
            DirectionGeneraleUi.showSuccess('Direction Générale supprimé avec succès');

            await this.loadDatas(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer cette direction générale';
            DirectionGeneraleUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#directiongeneraleForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#directiongeneraleForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());

      try {
        const id = $('#update-id').val();
        let response;
        if (id) {
          response = await DirectionGeneraleService.update(id, rawData);
        } else {
          response = await DirectionGeneraleService.create(rawData);
        }
        DirectionGeneraleUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-directiongenerale-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadDatas(this.getCurrentParams());
          resetForm($form);
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        DirectionGeneraleUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#directiongenerale-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadDatas(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#directiongenerale-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};
DirectionGeneraleController.init();
