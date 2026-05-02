// modules/circulations/controllers/taches.controller.js
import { TacheService } from '../services/taches.services.js';
import { TacheUi } from '../ui/taches.ui.js';
import { startLoader, closeLoader, toggleBulkButton } from '../../../helpers/utils.js';

export const TacheController = {
  docCelluleMap: {}, // Stockage du mapping

  async init() {
    // Récupération du mapping
    const mapData = document.getElementById('doc-cellule-tache-data');
    if (mapData) {
      this.docCelluleMap = JSON.parse(mapData.textContent);
    }

    if ($('#taches-tbody').length) {
      await this.loadTaches();
    }
    this.bindEvents();
    this.bindDetailEvents();
    this.bindDocumentFilter();
  },

  // ─── Chargement des tâches ────────────────────────────────────────

  async loadTaches(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await TacheService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      TacheUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      TacheUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindDocumentFilter() {
    // On utilise la délégation d'événement car le select est dans un modal
    $(document).on('change', '#document', e => {
      const docId = e.target.value;
      const celluleId = this.docCelluleMap[docId] || null;
      TacheUi.filterAssigneeList(celluleId);
    });
  },

  bindEvents() {
    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-taches', function () {
      const isChecked = $(this).is(':checked');
      $('.tache-checkbox').prop('checked', isChecked);
      toggleBulkButton('.tache-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.tache-checkbox', function () {
      toggleBulkButton('.tache-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#taches-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = TacheController.getCurrentParams();
      params.page = page;

      await TacheController.loadTaches(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#tache-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadTaches();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadTaches();
      // reset filter forms
      $('#tache-search-form').trigger('reset');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => TacheUi.renderForm(null));

    // Voir (Détail)
    $(document).on('click', '[data-action="view"]', function (e) {
      e.preventDefault();
      const id = $(this).data('id');
      window.location.href = `/taches/detail/${id}/`;
    });

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await TacheService.fetchOne(id);
        TacheUi.renderForm(res.data);
        const docId = res.data.document;
        const celluleId = this.docCelluleMap[docId];
        TacheUi.filterAssigneeList(celluleId);
        new bootstrap.Modal(document.getElementById('create-tache-modal')).show();
      } catch (err) {
        TacheUi.showError('Erreur chargement tâche');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.tache-checkbox:checked')
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
            const res = await TacheService.bulkDelete(ids);
            TacheUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = TacheController.getCurrentParams();
            await TacheController.loadTaches(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            TacheUi.showError(message, '#bulk-delete-form-error');
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
        await TacheService.toggleStatus(id);
        TacheUi.showSuccess('Statut mis à jour');
        await this.loadTaches(this.getCurrentParams());
      } catch (err) {
        TacheUi.showError(err.data?.message || 'Erreur');
      }
    });

    // Supprimer
    $(document).on('click', '[data-action="delete"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      const modalElement = document.getElementById('delete-tache-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await TacheService.remove(id);

            modalInstance.hide();
            TacheUi.showSuccess('Tache supprimée avec succès');

            await this.loadTaches(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer cette tache';
            TacheUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Soumettre formulaire (create & update)
    $('#tacheForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#tacheForm');
      const $saveBtn = $('#save-btn');
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);
      const rawData = Object.fromEntries(formData.entries());

      try {
        const id = $('#update-id').val();
        let response;
        if (id) {
          response = await TacheService.update(id, rawData);
        } else {
          response = await TacheService.create(rawData);
        }
        TacheUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-tache-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadTaches(this.getCurrentParams());
          $form[0].reset();
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
        TacheUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  // Evènements de la page détail
  bindDetailEvents() {
    const taskId = $('#update-id-detail').val() || '{{ tache.id }}'; // Récupéré du template

    // 1. Soumission du commentaire
    $('#commentForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#commentForm');
      const $btn = $form.find('button[type="submit"]');

      const data = {
        contenu: $form.find('textarea[name="contenu"]').val()
        //statut: $form.find('select[name="statut"]').val() // si tu l'ajoutes au modal
      };

      try {
        $btn.prop('disabled', true);

        const res = await TacheService.addComment(taskId, data);

        TacheUi.showSuccess(res.message || 'Commentaire ajouté', '#form-success');
        console.log('res : ', res);
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('commentModal'));
          if (modalInstance) modalInstance.hide();
          await this.loadTaches(this.getCurrentParams());
          $form[0].reset();
        }, 3000);
        setTimeout(() => window.location.reload(), 1000);
      } catch (err) {
        TacheUi.showError(err.data?.message || "Erreur lors de l'ajout du commentaire", '#form-error');
      } finally {
        $btn.prop('disabled', false);
      }
    });

    // 2. Mise à jour de la tâche (Modal Edit sur page détail)
    $('#editTaskForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#editTaskForm');
      const $btn = $form.find('button[type="submit"]');

      const formData = new FormData($form[0]);
      const data = Object.fromEntries(formData.entries());

      try {
        $btn.prop('disabled', true);
        startLoader('#form-loader');

        // On utilise la méthode update existante dans TacheService
        const res = await TacheService.update(taskId, data);

        TacheUi.showSuccess(res.message || 'Tâche mise à jour avec succès');
        setTimeout(() => window.location.reload(), 1000);
      } catch (err) {
        const errorData = err.data?.errors || err.data?.message || 'Erreur de mise à jour';
        TacheUi.showError(errorData, '#edit-task-error');
      } finally {
        $btn.prop('disabled', false);
        closeLoader('#form-loader');
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#tache-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadTaches(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#tache-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};
TacheController.init();
