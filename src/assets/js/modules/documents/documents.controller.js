// modules/documents/documents.controller.js
import { DocumentState } from './documents.states.js';
import { DocumentUi } from './documents.ui.js';
import { DocumentService } from './documents.services.js';
import { startLoader, closeLoader, showAlertMessage, toggleBulkButton } from '../../helpers/utils.js';

export const DocumentController = {
  conflictQueue: [],
  uploadQueue: [],
  currentConflict: null,
  actions: [],
  allFiles: new DataTransfer(),

  async init() {
    // Récupérer le mode stocké ou 'table' par défaut
    const savedView = localStorage.getItem('document_view_mode') || 'table';
    this.switchView(savedView);
    await this.loadDatas();
    this.bindEvents();
    // Toggle View Management
    $('#view-table-btn').on('click', () => this.switchView('table'));
    $('#view-grid-btn').on('click', () => this.switchView('grid'));
  },

  switchView(viewType) {
    DocumentUi.currentView = viewType;
    localStorage.setItem('document_view_mode', viewType); // Sauvegarde

    // Mise à jour visuelle des boutons
    $('.view-btn').removeClass('active'); // Ajoutez une classe .view-btn à vos boutons
    $(`#view-${viewType}-btn`).addClass('active');

    // On recharge les données avec les paramètres actuels pour rafraîchir l'affichage
    this.loadDatas(this.getCurrentParams());
  },

  // ─── Chargement des utilisateurs ────────────────────────────────────────
  async loadDatas(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await DocumentService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      DocumentUi.render(res);
    } catch (err) {
      console.error('Erreur:', err);
      DocumentUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────
  bindEvents() {
    // 1. Initialiser le Drag & Drop
    this.initDragAndDrop();

    $('#documentForm').on('submit', async e => {
      e.preventDefault();
      const id = $('#update-id').val();

      if (id) {
        await this.handleUpdate(id);
      } else {
        await this.handleMultipleUpload();
      }
    });

    // Gestion de la sélection multiple (Tableau)
    $(document).on('change', '#check-all-documents', function () {
      const isChecked = $(this).is(':checked');
      $('.document-checkbox').prop('checked', isChecked);
      toggleBulkButton('.document-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion de la sélection multiple (Grille)
    $(document).on('change', '#check-all-documents-grid', function () {
      const isChecked = $(this).is(':checked');
      $('.document-checkbox').prop('checked', isChecked); // Cible les checkboxes des cartes
      toggleBulkButton('.document-checkbox:checked', '#bulk-actions-container');
    });

    $(document).on('change', '.document-checkbox', function () {
      toggleBulkButton('.document-checkbox:checked', '#bulk-actions-container');
    });

    // Gestion des clics de pagination
    $(document).on('click', '#documents-pagination .page-link', async function (e) {
      e.preventDefault();
      const $this = $(this);
      const page = $this.data('page');

      if (!page || $this.parent().hasClass('disabled') || $this.parent().hasClass('active')) {
        return;
      }

      // On récupère les filtres actuels ET on ajoute la page
      let params = DocumentController.getCurrentParams();
      params.page = page;

      await DocumentController.loadDatas(params);
    });

    // Recherche & filtres
    let searchTimer;
    $('#document-search-form').on('input change', 'input, select', () => {
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
      // reset filter forms
      $('#document-search-form').trigger('reset');
      $('#clearSearch').trigger('click');
    });

    // Ajouter
    $('#add-button').on('click', () => DocumentUi.renderForm(null));

    // Voir (Détail)
    $(document).on('click', '[data-action="view"]', function (e) {
      e.preventDefault();
      const id = $(this).data('id');
      window.location.href = `/document/details/${id}/`;
    });

    // Ajouter une circulation
    $(document).on('click', '[data-action="circulation"]', function (e) {
      e.preventDefault();
      const id = $(this).data('id');
      window.location.href = `/circulation/circulations/create/?document_id=${id}`;
    });

    // Ajouter une tache
    $(document).on('click', '[data-action="tache"]', function (e) {
      e.preventDefault();
      const id = $(this).data('id');
      window.location.href = `/circulation/taches/create/?document_id=${id}`;
    });

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');

      try {
        const res = await DocumentService.fetchOne(id);
        DocumentUi.renderForm(res.data?.document);
        new bootstrap.Modal(document.getElementById('create-document-modal')).show();
      } catch (err) {
        DocumentUi.showError('Erreur chargement document');
      }
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.document-checkbox:checked')
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
            const res = await DocumentService.bulkDelete(ids);
            DocumentUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = DocumentController.getCurrentParams();
            await DocumentController.loadDatas(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            DocumentUi.showError(message, '#bulk-delete-form-error');
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
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer ce document';
            DocumentUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  async handleUpdate(id) {
    const $form = $('#documentForm');
    const $saveBtn = $('#save-btn');
    const formData = new FormData($form[0]);

    try {
      $saveBtn.prop('disabled', true);
      startLoader('#form-loader');

      // Nettoyage si aucun nouveau fichier n'est sélectionné
      const fileField = formData.get('fichier');
      if (!fileField || fileField.size === 0) {
        formData.delete('fichier');
      }

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

  async handleMultipleUpload() {
    const files = [...this.allFiles.files];
    if (files.length === 0) {
      return DocumentUi.showError('Sélectionnez au moins un fichier', '#form-error');
    }

    // Réinitialisation des files d'attente
    this.conflictQueue = [];
    this.uploadQueue = [];
    this.actions = [];

    try {
      startLoader('#form-loader');

      // Étape 1 : Vérification des doublons sur le serveur
      await Promise.all(files.map(file => this.checkFileConflict(file)));

      // Étape 2 : Si conflits, on gère la modale, sinon on envoie tout
      if (this.conflictQueue.length > 0) {
        this.showNextConflict();
      } else {
        await this.submitFinalForm();
      }
    } catch (err) {
      this.handleError(err);
    } finally {
      closeLoader('#form-loader');
    }
  },

  async checkFileConflict(file) {
    if (!file || !file.name) return;
    try {
      const res = await DocumentService.checkConflict(file.name);
      if (res.exists) {
        this.conflictQueue.push({ file: file, existing: res });
      } else {
        this.uploadQueue.push(file);
      }
    } catch (err) {
      console.error(`Erreur de check pour ${file.name}:`, err);
      11;
      this.uploadQueue.push(file);
    }
  },

  showNextConflict() {
    if (this.conflictQueue.length === 0) {
      this.submitFinalForm();
      return;
    }

    this.currentConflict = this.conflictQueue.shift();
    const modalEl = document.getElementById('duplicateDocumentModal');

    // Vérification de sécurité
    if (!modalEl) {
      console.error('La modale #duplicateDocumentModal est introuvable dans le HTML');
      return;
    }

    // On met à jour le texte AVANT d'afficher
    const fileName = this.currentConflict.file.name;
    $('#dup-text').html(`Le fichier <strong>${fileName}</strong> existe déjà.<br>Que souhaitez-vous faire ?`);

    this.bindConflictButtons();

    // On récupère l'instance (créée dans bindConflictButtons si besoin) et on affiche
    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
    modalInstance.show();
  },

  bindConflictButtons() {
    const self = this;
    const modalEl = document.getElementById('duplicateDocumentModal');

    // SÉCURITÉ : Récupérer l'instance existante OU en créer une nouvelle si elle n'existe pas
    let modalInstance = bootstrap.Modal.getInstance(modalEl);
    if (!modalInstance) {
      modalInstance = new bootstrap.Modal(modalEl);
    }

    // On nettoie les anciens événements pour éviter les exécutions multiples
    $('#btn-version, #btn-overwrite, #btn-skip').off('click');

    // Gestionnaire commun pour enregistrer l'action et fermer
    const handleAction = actionType => {
      this.actions.push({
        file: this.currentConflict.file,
        name: this.currentConflict.file.name,
        action: actionType,
        documentId: this.currentConflict.existing.document_id
      });

      this.uploadQueue.push(this.currentConflict.file);

      // On utilise l'instance qu'on est sûr d'avoir récupérée
      modalInstance.hide();
    };

    $('#btn-version').on('click', () => handleAction('version'));
    $('#btn-overwrite').on('click', () => handleAction('overwrite'));

    $('#btn-skip').on('click', () => {
      this.actions.push({ name: this.currentConflict.file.name, action: 'skip' });
      modalInstance.hide();
    });

    // Événement de fermeture pour enchaîner sur le conflit suivant
    $(modalEl)
      .off('hidden.bs.modal')
      .on('hidden.bs.modal', function () {
        self.showNextConflict();
      });
  },

  async submitFinalForm() {
    const $form = $('#documentForm');
    const formData = new FormData($form[0]);

    // Nettoyage des champs qui pourraient interférer
    formData.delete('fichiers');
    formData.delete('actions[]');
    formData.delete('fichier'); // Supprime le champ simple "fichier" s'il existe

    // 1. Ajout des fichiers SANS conflit
    this.uploadQueue.forEach(file => {
      if (file) formData.append('fichiers', file);
    });

    // 2. Ajout des fichiers AVEC résolution de conflit
    this.actions.forEach(a => {
      // On utilise "a.file" qu'on a bien ajouté dans bindConflictButtons
      if (a && a.file) {
        formData.append('fichiers', a.file);

        // Très important : on envoie le JSON de l'action
        formData.append(
          'actions[]',
          JSON.stringify({
            name: a.name,
            action: a.action,
            documentId: a.documentId
          })
        );
      }
    });

    // Debug réel pour vérifier le contenu du FormData avant envoi
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + (pair[1] instanceof File ? pair[1].name : pair[1]));
    }

    try {
      startLoader('#form-loader');
      console.log('Données envoyées au service bulkCreate:', Object.fromEntries(formData.entries()));
      const response = await DocumentService.bulkCreate(formData);

      DocumentUi.showSuccess(response.message || 'Upload terminé', '#form-success');

      // Reset
      this.allFiles = new DataTransfer();
      this.uploadQueue = [];
      this.actions = [];

      this.finalizeSubmission($form);
    } catch (err) {
      this.handleError(err);
    } finally {
      closeLoader('#form-loader');
    }
  },

  initDragAndDrop() {
    const dropArea = $('#drop-area');
    const fileInput = $('#file-input');

    dropArea.on('click', e => {
      if (e.target !== fileInput[0]) fileInput.click();
    });

    // Empêcher la propagation du clic sur l'input pour éviter la boucle infinie
    fileInput.on('click', e => e.stopPropagation());

    dropArea.on('dragover', e => {
      e.preventDefault();
      dropArea.addClass('bg-light border-primary');
    });

    dropArea.on('dragleave drop', () => dropArea.removeClass('bg-light border-primary'));

    dropArea.on('drop', e => {
      e.preventDefault();
      const newFiles = e.originalEvent.dataTransfer.files;
      this.handleFileSelection(newFiles);
    });

    fileInput.on('change', e => {
      this.handleFileSelection(e.target.files);
      // On vide l'input pour permettre de sélectionner à nouveau le même fichier si besoin
      fileInput.val('');
    });
  },

  // Nouvelle méthode pour centraliser l'ajout
  handleFileSelection(files) {
    Array.from(files).forEach(file => {
      // Optionnel : éviter les doublons exacts dans la liste visuelle
      const exists = Array.from(this.allFiles.files).some(f => f.name === file.name && f.size === file.size);
      if (!exists) {
        this.allFiles.items.add(file);
      }
    });
    this.renderPreviews(this.allFiles.files);
  },

  renderPreviews(files) {
    const container = $('#previews');
    container.empty();

    Array.from(files).forEach((file, index) => {
      const isImg = file.type.startsWith('image/');
      const reader = new FileReader();

      const cardHtml = `
      <div class="col-md-3 col-sm-6 mb-2" id="preview-${index}">
        <div class="card p-1 border shadow-none text-center h-100 position-relative">
          <button type="button"
                  class="btn btn-danger btn-xs position-absolute top-0 end-0 m-1 remove-file-btn"
                  data-index="${index}"
                  style="padding: 2px 5px; z-index: 10;">
            <i class="ri-close-line"></i>
          </button>
          <div style="height: 80px;" class="d-flex align-items-center justify-content-center bg-light rounded">
            ${isImg ? `<img id="img-${index}" class="img-fluid" style="max-height: 70px;">` : `<i class="ri-file-line ri-2x"></i>`}
          </div>
          <div class="small text-truncate mt-1 px-1" title="${file.name}" style="font-size: 10px;">
            ${file.name}
          </div>
        </div>
      </div>`;

      container.append(cardHtml);

      if (isImg) {
        reader.onload = e => $(`#img-${index}`).attr('src', e.target.result);
        reader.readAsDataURL(file);
      }
    });

    // Binder l'événement de suppression
    $('.remove-file-btn')
      .off()
      .on('click', e => {
        e.stopPropagation(); // Éviter de déclencher le clic sur la dropzone parent
        const idx = $(e.currentTarget).data('index');
        this.removeFile(idx);
      });
  },

  removeFile(index) {
    const newDataTransfer = new DataTransfer();
    const files = this.allFiles.files;

    for (let i = 0; i < files.length; i++) {
      if (i !== index) newDataTransfer.items.add(files[i]);
    }

    this.allFiles = newDataTransfer;
    this.renderPreviews(this.allFiles.files);
  },

  // Nettoyage après succès
  finalizeSubmission($form) {
    setTimeout(async () => {
      const modalElement = document.getElementById('create-document-modal');
      const modalInstance = bootstrap.Modal.getInstance(modalElement);
      if (modalInstance) modalInstance.hide();

      await this.loadDatas(this.getCurrentParams());
      $form[0].reset();
      this.allFiles = new DataTransfer(); // Vider le panier
      $('#previews').empty(); // Nettoyer les vignettes
    }, 2500);
  },

  // Centralisation des erreurs
  handleError(err) {
    console.error('Erreur:', err);
    const errorData = err.data?.errors || err.data?.message || err.data?.error || 'Erreur inconnue';
    DocumentUi.showError(errorData, '#form-error');
  },

  handleSearch() {
    const params = this.getCurrentParams();
    this.loadDatas(params);
  },

  getCurrentParams(formId = '#document-search-form') {
    return Object.fromEntries(
      $(formId)
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};
DocumentController.init();
