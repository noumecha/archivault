// modules/circulations/controllers/taches.controller.js
import { TacheService } from '../services/taches.services.js';
import { TacheUi } from '../ui/taches.ui.js';
import { startLoader, closeLoader, toggleBulkButton } from '../../../helpers/utils.js';

export const TacheController = {
  docCelluleMap: {},

  /**
   * Initialisation du module :
    - Chargement de la map document-cellule depuis le DOM
    - Chargement initial des tâches si on est sur la page de liste
    - Liaison de tous les événements (liste et détail)
   */
  async init() {
    const mapData = document.getElementById('doc-cellule-tache-data');
    if (mapData) {
      this.docCelluleMap = JSON.parse(mapData.textContent);
    }

    const detailContext = document.getElementById('detail-tache-context');
    if (detailContext) {
      const context = JSON.parse(detailContext.textContent);
      if (context.document_id) {
        this.docCelluleMap[context.document_id] = context.cellule_id;
      }
    }

    if ($('#taches-tbody').length) {
      await this.loadTaches();
    }
    this.bindEvents();
    this.bindDetailEvents();
    this.bindDocumentFilter();
  },

  /**
   * chargement des taches
   * @param {*} params
   */
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

  /**
   * gestion du formulaire de création/édition de tâche
    - Si id est fourni => mode édition/traitement (Jira style)
    - Sinon => mode création pure
   * @param {*} id
   */
  async openTacheForm(id = null, modalId = '#create-tache-modal', formSelector = '#tacheForm') {
    const currentUserId = window.CURRENT_USER_ID;
    const currentUserRole = window.CURRENT_USER_ROLE;
    const modalElement = document.querySelector(modalId);
    if (!modalElement) return;
    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);

    if (id) {
      try {
        startLoader('#form-loader');
        const res = await TacheService.fetchOne(id);
        const tache = res.data;
        TacheUi.setupDynamicForm(tache, currentUserId, currentUserRole, formSelector);
        const docId = tache.document;
        const celluleId = this.docCelluleMap[docId] || null;
        console.log('Cellule ID pour le document:', celluleId);
        console.log('user role : ', currentUserRole);
        TacheUi.filterAssigneeList(celluleId, currentUserRole);
        modalInstance.show();
      } catch (err) {
        console.error(err);
        TacheUi.showError('Erreur de chargement de la tâche');
      } finally {
        closeLoader('#form-loader');
      }
    } else {
      TacheUi.setupCreateForm();
      TacheUi.filterAssigneeList(null, currentUserRole);
      modalInstance.show();
    }
  },

  /**
   * Gestion du filtrage dynamique des destinataires en fonction du document sélectionné dans le formulaire de tâche
   */
  bindDocumentFilter() {
    $(document).on('change', '#document', e => {
      const currentUserRole = window.CURRENT_USER_ROLE;
      const docId = e.target.value;
      const celluleId = this.docCelluleMap[docId] || null;
      TacheUi.filterAssigneeList(celluleId, currentUserRole);
    });
  },

  /**
   * Gestion de tous les événements liés à la liste des tâches (sélection, pagination, recherche, actions sur les tâches, etc.)
    - Sélection multiple + activation du bouton d'action groupée
    - Pagination avec maintien des filtres
    - Recherche avec délai de frappe (debounce)
    - Clic sur les actions (voir, éditer, supprimer, basculer statut)
   */
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
    // Ajouter une nouvelle tâche
    $('#add-button').on('click', () => {
      this.openTacheForm(null);
    });

    // Voir (Détail)
    $(document).on('click', '[data-action="view"]', function (e) {
      e.preventDefault();
      const id = $(this).data('id');
      window.location.href = `/taches/detail/${id}/`;
    });

    // Éditer / Traiter une tâche existante (Délégation d'événement)
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      this.openTacheForm(id);
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

      // Captures TOUT (Inputs texte, selects, ET le fichier de version s'il y en a un)
      const formData = new FormData($form[0]);
      const id = $('#update-id').val();

      try {
        let response;
        if (id) {
          response = await TacheService.update(id, formData);
        } else {
          // Pour la création pure, un JSON ou FormData classique convient
          const rawData = Object.fromEntries(formData.entries());
          response = await TacheService.create(rawData);
        }

        TacheUi.showSuccess(response.message || 'Opération réussie', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-tache-modal'));
          if (modalInstance) modalInstance.hide();
          await this.loadTaches(this.getCurrentParams());
          $form[0].reset();
          window.location.reload();
        }, 3000);
      } catch (err) {
        console.error('Erreur capturée:', err);
        const errorData =
          err.data?.errors ||
          err.data?.message ||
          err.data?.error ||
          'Une erreur est survenue lors de la soumission du formulaire. Veuillez réessayer.';
        TacheUi.showError(errorData, '#form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  /**
   * Gestion de tous les événements liés à la page de détail d'une tâche (ajout de commentaire, édition dans le modal, etc.)
    - Soumission du formulaire de commentaire
    - Mise à jour de la tâche depuis le modal d'édition sur la page détail
   */
  bindDetailEvents() {
    const taskId = $('#update-id-detail').val() || '{{ tache.id }}';
    // 1. Clic sur le bouton "Mettre à jour"
    $(document).on('click', '[data-action="edit-task"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      this.openTacheForm(id, '#editTaskModal', '#editTaskForm');
    });

    $(document).on('submit', '#editTaskForm', async e => {
      e.preventDefault();
      const $form = $('#editTaskForm');
      const $saveBtn = $('#save-btn');
      const taskId = $form.find('#update-id').val();
      if (!taskId) return;
      $saveBtn.prop('disabled', true);

      const formData = new FormData($form[0]);

      try {
        $saveBtn.prop('disabled', true);
        startLoader('#form-loader');
        const res = await TacheService.update(taskId, formData);
        TacheUi.showSuccess(res.message || 'Tâche mise à jour avec succès');
        setTimeout(() => window.location.reload(), 1000);
      } catch (err) {
        const errorData = err.data?.errors || err.data?.message || 'Erreur de mise à jour';
        TacheUi.showError(errorData, '#edit-task-error');
      } finally {
        $saveBtn.prop('disabled', false);
        closeLoader('#form-loader');
      }
    });
  },

  /**
   * fonction de recherche avec maintien des filtres et pagination
    - Récupère les valeurs du formulaire de recherche
    - Construit un objet de paramètres à partir de ces valeurs
    - Appelle loadTaches avec ces paramètres pour rafraîchir la liste
   */
  handleSearch() {
    const params = Object.fromEntries(
      $('#tache-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadTaches(params);
  },

  /**
   * Récupère les paramètres de recherche actuels à partir du formulaire de recherche
   */
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
