// modules/documents/documents.controller.js
import { DocumentState } from './documents.states.js';
import { DocumentUi } from './documents.ui.js';
import { DocumentService } from './documents.services.js';
import { TacheService } from '../circulations/services/taches.services.js';
import { CirculationService } from '../circulations/circulations.service.js';
import { CirculationUi } from '../circulations/circulations.ui.js';
import { CirculationController } from '../circulations/circulations.controller.js';
import { TacheUi } from '../circulations/ui/taches.ui.js';
import { resetForm } from '../../helpers/utils.js';
import { UploadHelper } from './helpers/upload.helper.js';
import { DragDropHelper } from './helpers/drag-drop.helper.js';
import { FilterHelper } from './helpers/filter.helper.js';

import {
  startLoader,
  closeLoader,
  showAlertMessage,
  toggleBulkButton,
  disableElement,
  enableElement
} from '../../helpers/utils.js';

export const DocumentController = {
  conflictQueue: [],
  uploadQueue: [],
  currentConflict: null,
  actions: [],
  allFiles: new DataTransfer(),
  etapeIndex: 0,
  docCelluleMap: {},

  async init() {
    const mapData = document.getElementById('doc-cellule-data');
    if (mapData) {
      this.docCelluleMap = JSON.parse(mapData.textContent);
    }
    FilterHelper.init();
    const savedView = localStorage.getItem('document_view_mode') || 'folder';
    this.switchView(savedView);
    await this.loadDatas();
    this.bindEvents();
    this.bindFolderEvents();
    this.bindTacheEvents();
    this.bindCirculationEvents();
    this.bindCascadedFilterEvents();

    $('#view-folder-btn').on('click', () => this.switchView('folder'));
    $('#view-table-btn').on('click', () => this.switchView('table'));
    $('#view-grid-btn').on('click', () => this.switchView('grid'));
  },

  switchView(viewType) {
    DocumentUi.currentView = viewType;
    localStorage.setItem('document_view_mode', viewType);
    $('.view-btn').removeClass('active');
    $(`#view-${viewType}-btn`).addClass('active');
    // On synchronise les états visuels des variables UI globales
    DocumentUi.currentType = $('#id_type_document').val() || null;
    DocumentUi.currentSubtype = $('#id_sous_type').val() || null;
    this.loadDatas(this.getCurrentParams());
  },

  async loadDatas(params = {}) {
    try {
      startLoader('#table-loader');
      // Si aucun paramètre n'est fourni, récupérer l'état actuel des filtres
      const queryParams = Object.keys(params).length ? params : this.getCurrentParams();
      const res = await DocumentService.fetchAll(queryParams);
      res.current_page = parseInt(queryParams.page) || 1;
      DocumentUi.render(res);

      $('.document-checkbox').prop('checked', false);
      toggleBulkButton(
        '.document-checkbox:checked',
        '#bulk-actions-container',
        '#check-all-documents, #check-all-documents-grid'
      );
    } catch (err) {
      DocumentUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  /**
   * Gestion de la navigation dans les dossiers (Types et Sous-types)
   * - Clic sur un dossier : filtre les documents et met à jour le fil d'Ariane
   * - Clic sur le fil d'Ariane : remonte dans la hiérarchie et met à jour les filtres
   * - Synchronisation bidirectionnelle avec les selects natifs du formulaire de recherche
   * - Maintien de l'état de navigation dans DocumentUi pour une cohérence globale
   */
  bindFolderEvents() {
    const self = this;

    // 1. Double-clic ou Clic sur un Dossier (Type ou Sous-type)
    $(document).on('click', '.folder-item', function () {
      const $folder = $(this);
      const id = $folder.data('id');
      const level = $folder.data('level');

      if (level === 'type') {
        DocumentUi.currentType = id;
        DocumentUi.currentSubtype = null;
        // Liaison descendante avec les selects natifs de ton filtre existant
        $('#id_type_document').val(id).trigger('change');
      } else if (level === 'subtype') {
        DocumentUi.currentSubtype = id;
        $('#id_sous_type').val(id).trigger('change');
      }
      self.loadDatas(self.getCurrentParams());
      //self.handleSearch();
    });

    // Clic sur les éléments du fil d'Ariane (Breadcrumb) pour remonter
    $(document)
      .off('click', '#directory-breadcrumb .breadcrumb-item')
      .on('click', '#directory-breadcrumb .breadcrumb-item', function () {
        const level = $(this).data('level');

        if (level === 'root') {
          DocumentUi.currentType = null;
          DocumentUi.currentSubtype = null;
          $('#id_type_document').val('').trigger('change');
          $('#id_sous_type').val('').trigger('change');
        } else if (level === 'type') {
          DocumentUi.currentSubtype = null;
          $('#id_sous_type').val('').trigger('change');
        } else {
          return; // Niveau terminal
        }

        self.loadDatas(self.getCurrentParams());
      });

    // Capture des clics sur les fichiers affichés à l'intérieur du mode dossier
    $(document).on('click', '.file-item-click', function (e) {
      e.preventDefault();
      const docId = $(this).data('id');
      window.location.href = `/document/details/${docId}/`;
    });

    // 3. Sécurité de synchronisation bidirectionnelle : si l'utilisateur change les select natifs
    $('#id_type_document').on('change', function () {
      const val = $(this).val();
      if (DocumentUi.currentType !== val) {
        DocumentUi.currentType = val || null;
        DocumentUi.currentSubtype = null;
      }
    });

    $('#id_sous_type').on('change', function () {
      const val = $(this).val();
      if (DocumentUi.currentSubtype !== val) {
        DocumentUi.currentSubtype = val || null;
      }
    });
  },

  bindEvents() {
    // Initialisation du Drag & Drop via le helper
    DragDropHelper.init(this);

    $('#documentForm').on('submit', async e => {
      e.preventDefault();
      const id = $('#update-id').val();

      if (id) {
        await this.handleUpdate(id);
      } else {
        // Traitement de l'upload via le helper
        await UploadHelper.handleMultipleUpload(this);
      }
    });

    // Sélection globale & unitaire (Tableau & Grille)
    $(document).on('change', '#check-all-documents, #check-all-documents-grid', function () {
      const isChecked = $(this).is(':checked');
      $('.document-checkbox').prop('checked', isChecked);
      toggleBulkButton(
        '.document-checkbox:checked',
        '#bulk-actions-container',
        '#check-all-documents, #check-all-documents-grid'
      );
    });

    $(document).on('change', '.document-checkbox', function () {
      toggleBulkButton(
        '.document-checkbox:checked',
        '#bulk-actions-container',
        '#check-all-documents, #check-all-documents-grid'
      );
      const totalCheckboxes = $('.document-checkbox').length;
      const checkedCheckboxes = $('.document-checkbox:checked').length;
      const allChecked = totalCheckboxes === checkedCheckboxes;
      $('#check-all-documents, #check-all-documents-grid').prop('checked', allChecked);
    });

    // Pagination
    $(document).on('click', '#documents-pagination .page-link', async function (e) {
      e.preventDefault();
      const page = $(this).data('page');
      if (!page || $(this).parent().hasClass('disabled') || $(this).parent().hasClass('active')) return;

      let params = DocumentController.getCurrentParams();
      params.page = page;
      await DocumentController.loadDatas(params);
    });

    // Recherche & Filtres
    let searchTimer;
    $('#document-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    $('#clearSearch').on('click', () => {
      $('#search').val('');
      DocumentUi.currentType = null;
      DocumentUi.currentSubtype = null;
      this.loadDatas();
    });

    $('#refresh-button').on('click', () => {
      this.loadDatas();
      resetForm('#document-search-form');
      FilterHelper.resetFilters('#document-search-form');
      $('#clearSearch').trigger('click');
    });

    // Actions unitaires
    $('#add-button').on('click', () => DocumentUi.renderForm(null));

    $(document).on('click', '[data-action="view"]', function (e) {
      e.preventDefault();
      window.location.href = `/document/details/${$(this).data('id')}/`;
    });

    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await DocumentService.fetchOne(id);
        new bootstrap.Modal(document.getElementById('create-document-modal')).show();
        DocumentUi.renderForm(res.data);
      } catch (err) {
        DocumentUi.showError('Erreur chargement document');
      }
    });

    // Suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.document-checkbox:checked')
        .map(function () {
          return $(this).val();
        })
        .get();
      if (ids.length === 0) return;

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
            const res = await DocumentService.bulkDelete(ids);
            DocumentUi.showSuccess(res.message);
            modalInstance.hide();
            $('.document-checkbox').prop('checked', false);
            toggleBulkButton(
              '.document-checkbox:checked',
              '#bulk-actions-container',
              '#check-all-documents, #check-all-documents-grid'
            );
            await DocumentController.loadDatas(DocumentController.getCurrentParams());
          } catch (err) {
            DocumentUi.showError(
              err.data?.message || 'Erreur lors de la suppression groupée',
              '#bulk-delete-form-error'
            );
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-delete-loader');
          }
        });
    });

    // Suppression simple
    $(document).on('click', '[data-action="delete"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      const modalElement = document.getElementById('delete-document-modal');
      const modalInstance = new bootstrap.Modal(modalElement);
      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');
          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');
            await DocumentService.remove(id);
            modalInstance.hide();
            DocumentUi.showSuccess('Document supprimé avec succès');
            await this.loadDatas(this.getCurrentParams());
          } catch (err) {
            DocumentUi.showError(err.data?.message || 'Impossible de supprimer ce document', '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Prévisualisation de documents
    $(document).on('click', '[data-action="preview-doc"]', function () {
      const url = $(this).data('url');
      const type = $(this).data('type');
      const title = $(this).data('title');
      const $body = $('#previewBody');

      $('#previewTitle').text(title);
      $body.html('<div class="spinner-border text-primary" role="status"></div>');

      let html = '';
      if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(type)) {
        html = `<img src="${url}" class="img-fluid" style="max-height: 90vh;">`;
      } else if (type === 'pdf') {
        html = `<iframe src="${url}" width="100%" height="100%" style="border:none;"></iframe>`;
      } else if (['mp4', 'webm'].includes(type)) {
        html = `<video controls autoplay class="w-75"><source src="${url}" type="video/${type}"></video>`;
      } else if (['mp3', 'wav', 'ogg'].includes(type)) {
        html = `<audio controls autoplay><source src="${url}" type="audio/${type}"></audio>`;
      } else if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(type)) {
        const officeUrl = `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(window.location.origin + url)}`;
        html = `<iframe src="${officeUrl}" width="100%" height="100%" frameborder="0"></iframe>`;
      } else if (['txt', 'sql', 'json'].includes(type)) {
        html = `<iframe src="${url}" width="100%" height="100%" style="background: white;"></iframe>`;
      } else {
        html = `<div class="text-white text-center">
                  <i class="ri-error-warning-line ri-4x"></i>
                  <p>Aperçu non disponible (.${type})</p>
                  <a href="${url}" class="btn btn-primary" download>Télécharger</a>
                </div>`;
      }
      $body.html(html);
      new bootstrap.Modal(document.getElementById('previewDocModal')).show();
    });
  },

  resetEtapeIndex() {
    this.etapeIndex = 0;
    $('#etapes-container').empty();
  },

  bindCirculationEvents() {
    $('#doc-select').on('change', e => {
      const docId = e.target.value;
      const celluleId = this.docCelluleMap[docId];
      CirculationUi.filterUserSelects(celluleId);
    });

    $('#btn-add-etape')
      .off('click')
      .on('click', () => {
        const currentDocId = $('#doc-select').val();
        const activeCelluleId = this.docCelluleMap[currentDocId] || null;
        const html = CirculationUi.renderEtapeRow(this.etapeIndex, activeCelluleId);
        $('#etapes-container').append(html);
        this.etapeIndex++;
      });

    $(document).on('click', '.remove-etape', function () {
      CirculationController.reindexEtapes();
      $(this).closest('.etape-item').remove();
    });

    $(document).on('click', '[data-action="add-circulation"]', e => {
      e.preventDefault();
      this.resetEtapeIndex();
      DocumentUi.renderCirculatFormForDocument($(e.currentTarget).data('id'));
      new bootstrap.Modal(document.getElementById('create-documentCirculation-modal')).show();
    });

    $('#documentCirculationForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#documentCirculationForm');
      const $saveBtn = $('#save-btn');
      const data = CirculationService.getFormData($form);
      try {
        $saveBtn.prop('disabled', true);
        CirculationService.validate(data);
        const response = await CirculationService.initierCircuit(data);
        DocumentUi.showSuccess(response.message || 'Circulation initiée avec succès', '#circulation-form-success');
        setTimeout(() => {
          const modalInstance = bootstrap.Modal.getInstance(
            document.getElementById('create-documentCirculation-modal')
          );
          if (modalInstance) modalInstance.hide();
          resetForm($form);
          enableElement('#document');
        }, 2000);
      } catch (err) {
        DocumentUi.showError(
          err.data?.errors || err.data?.message || 'Une erreur est survenue',
          '#circulation-form-error'
        );
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  bindTacheEvents() {
    $('#document').on('change', e => {
      const currentUserRole = window.CURRENT_USER_ROLE;
      const docId = e.target.value;
      const celluleId = this.docCelluleMap[docId] || null;
      const currentAssigneeId = $('#assignee_a').val();
      TacheUi.filterAssigneeList(celluleId, currentUserRole, currentAssigneeId);
      //TacheUi.filterAssigneeList(celluleId, currentUserRole);
    });

    $(document).on('click', '[data-action="add-tache"]', function (e) {
      e.preventDefault();
      TacheUi.setupCreateForm('#documentTacheForm');
      DocumentUi.renderTacheFormForDocument($(this).data('id'));
      new bootstrap.Modal(document.getElementById('create-documentTache-modal')).show();
    });

    $('#documentTacheForm').on('submit', async e => {
      e.preventDefault();
      const $form = $('#documentTacheForm');
      const $saveBtn = $('#save-btn');
      const rawData = Object.fromEntries(new FormData($form[0]).entries());

      try {
        $saveBtn.prop('disabled', true);
        TacheService.validate(rawData);
        const response = await TacheService.create(rawData);
        DocumentUi.showSuccess(response.message || 'Tâche créée avec succès', '#tache-form-success');
        setTimeout(() => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-documentTache-modal'));
          if (modalInstance) modalInstance.hide();
          TacheUi.setupCreateForm();
          enableElement('#document');
        }, 2000);
      } catch (err) {
        DocumentUi.showError(err.data?.errors || err.data?.message || 'Une erreur est survenue', '#tache-form-error');
      } finally {
        $saveBtn.prop('disabled', false);
      }
    });
  },

  bindCascadedFilterEvents() {
    // ── 1. GESTION DU FORMULAIRE DE RECHERCHE (LISTE) ───────────────────────

    // Changement de cellule dans les filtres
    // Ton template génère les IDs sous la forme #id_nomdufiltre (ex: #id_cellule, #id_type_document)
    $(document).on('change', '#id_cellule', function () {
      const celluleId = $(this).val();
      FilterHelper.filterByCellule(celluleId, '#id_type_document', '#id_theme');
    });

    // Changement de type de document dans les filtres
    $(document).on('change', '#id_type_document', function () {
      const typeId = $(this).val();
      FilterHelper.filterBySpecification(typeId, '#id_sous_type');
    });

    // ── 2. GESTION DU FORMULAIRE DE CRÉATION / ÉDITION (MODAL) ──────────────

    // Changement de cellule dans le formulaire du modal (#cellule)
    $(document).on('change', '#create-document-modal #cellule', function () {
      const celluleId = $(this).val();
      FilterHelper.filterByCellule(celluleId, '#create-document-modal #type_document', '#create-document-modal #theme');
    });

    // Changement de type dans le formulaire du modal (#type_document)
    $(document).on('change', '#create-document-modal #type_document', function () {
      const typeId = $(this).val();
      FilterHelper.filterBySpecification(typeId, '#create-document-modal #sous_type');
    });
  },

  async handleUpdate(id) {
    const $form = $('#documentForm');
    const $saveBtn = $('#save-btn');
    const formData = new FormData($form[0]);

    try {
      $saveBtn.prop('disabled', true);
      startLoader('#form-loader');

      const fileField = formData.get('fichier');
      if (!fileField || fileField.size === 0) formData.delete('fichier');

      await DocumentService.validate(formData);
      const response = await DocumentService.update(id, formData);

      DocumentUi.showSuccess(response.message || 'Document mis à jour', '#form-success');
      this.finalizeSubmission($form);
    } catch (err) {
      this.handleError(err);
    } finally {
      $saveBtn.prop('disabled', false);
      closeLoader('#form-loader');
    }
  },

  finalizeSubmission($form) {
    setTimeout(async () => {
      const modalInstance = bootstrap.Modal.getInstance(document.getElementById('create-document-modal'));
      if (modalInstance) modalInstance.hide();

      await this.loadDatas(this.getCurrentParams());
      resetForm($form);
      this.allFiles = new DataTransfer();
      $('#previews').empty();
    }, 2500);
  },

  handleError(err) {
    DocumentUi.showError(err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue', '#form-error');
  },

  handleSearch() {
    // Si on est en mode folder, la recherche filtre les dossiers visuels instantanément via renderFolders
    if (DocumentUi.currentView === 'folder') {
      // On recharge les données de l'API (pour actualiser les fichiers du dossier selon le pattern de recherche)
      this.loadDatas(this.getCurrentParams());
    } else {
      this.loadDatas(this.getCurrentParams());
    }
  },

  getCurrentParams(formId = '#document-search-form') {
    const params = Object.fromEntries(
      $(formId)
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    // Si on est en mode folder, on surcharge les paramètres d'envoi API avec la navigation UI
    if (DocumentUi.currentView === 'folder') {
      if (DocumentUi.currentType) params.type_document = DocumentUi.currentType;
      if (DocumentUi.currentSubtype) params.sous_type = DocumentUi.currentSubtype;
    }
    return params;
  }
};

DocumentController.init();
