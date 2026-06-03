// modules/documents/controllers/theme.controller.js
import { ThemeService } from '../services/theme.service.js';
import { ThemeUi } from '../ui/theme.ui.js';
import { startLoader, closeLoader, toggleBulkButton, resetForm } from '../../../helpers/utils.js';

export const ThemeController = {
  async init() {
    await this.loadThemes();
    this.bindEvents();
  },

  async loadThemes(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await ThemeService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      ThemeUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      ThemeUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-themes', function () {
      const isChecked = $(this).is(':checked');
      $('.theme-checkbox').prop('checked', isChecked);
      toggleBulkButton('.theme-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.theme-checkbox', function () {
      toggleBulkButton('.theme-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#themes-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = ThemeController.getCurrentParams();
      params.page = page;

      await ThemeController.loadThemes(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#theme-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadThemes();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadThemes();
      resetForm('#theme-search-form');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => ThemeUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await ThemeService.fetchOne(id);
        new bootstrap.Modal(document.getElementById('create-theme-modal')).show();
        ThemeUi.renderForm(res.data);
      } catch (err) {
        console.error('Error : ', err);
        ThemeUi.showError('Erreur chargement thème');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.theme-checkbox:checked')
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
            const res = await ThemeService.bulkDelete(ids);
            ThemeUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = ThemeController.getCurrentParams();
            await ThemeController.loadThemes(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            ThemeUi.showError(message, '#bulk-delete-form-error');
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
      const modalElement = document.getElementById('delete-theme-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await ThemeService.remove(id);

            modalInstance.hide();
            ThemeUi.showSuccess('Thème supprimé avec succès');

            await this.loadThemes(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer ce thème';
            ThemeUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#themeForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#themeForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());
      try {
        const id = $('#update-id').val();
        await ThemeService.validate(rawData);
        let response;
        if (id) {
          response = await ThemeService.update(id, rawData);
        } else {
          response = await ThemeService.create(rawData);
        }
        ThemeUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-theme-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadThemes(this.getCurrentParams());
          resetForm($form);
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        ThemeUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#theme-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadThemes(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#theme-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};

ThemeController.init();
