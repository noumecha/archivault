// documents.controller.js
import { DocumentState } from './documents.states.js';
import { DocumentUI } from './documents.ui.js';
import { DocumentService } from './documents.services.js';
import { startLoader, closeLoader, showAlertMessage } from '../../helpers/utils.js';

export const DocumentController = {
  async init() {
    await this.loadDocuments();
    this.bindEvents();
  },

  async loadDocuments(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await DocumentService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      DocumentUI.renderTable(res);
    } catch (err) {
      console.error('Erreur chargement documents:', err);
      showAlertMessage('Erreur lors du chargement des documents', '#message-show');
    } finally {
      closeLoader('#table-loader');
    }
  },

  bindEvents() {
    // Recherche et Filtres
    let searchTimer;
    $('#document-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        const params = Object.fromEntries(new FormData($('#document-search-form')[0]));
        this.loadDocuments(params);
      }, 400);
    });

    // Pagination
    $(document).on('click', '#documents-pagination .page-link', e => {
      e.preventDefault();
      const page = $(e.currentTarget).data('page');
      if (page) {
        const params = Object.fromEntries(new FormData($('#document-search-form')[0]));
        params.page = page;
        this.loadDocuments(params);
      }
    });

    // Upload Multiple & Gestion Conflits
    $('#upload-form').on('submit', e => this.handleSubmit(e));
    $('#btn-version').on('click', () => this.handleVersion());
    $('#btn-overwrite').on('click', () => this.handleOverwrite());
    $('#btn-skip').on('click', () => this.showNextConflict());

    // Suppression
    $(document).on('click', '[data-action="delete"]', async e => {
      const id = $(e.currentTarget).data('id');
      if (confirm('Supprimer ce document ?')) {
        try {
          await DocumentService.remove(id);
          this.loadDocuments();
        } catch (err) {
          alert('Erreur lors de la suppression');
        }
      }
    });
  },

  handleSubmit(e) {
    e.preventDefault();
    const files = [...($('#file-input')[0]?.files || [])];
    if (!files.length) {
      showAlertMessage('Veuillez sélectionner au moins un fichier', '#form-error');
      return;
    }

    DocumentState.reset();
    const state = DocumentState.get();

    Promise.all(files.map(f => DocumentService.checkConflict(f))).then(results => {
      results.forEach((res, i) => {
        if (res.exists) state.conflictQueue.push({ file: files[i], existing: res });
        else state.uploadQueue.push(files[i]);
      });
      state.conflictQueue.length ? this.showNextConflict() : this.submitUpload();
    });
  },

  showNextConflict() {
    const state = DocumentState.get();
    if (!state.conflictQueue.length) return this.submitUpload();

    state.currentConflict = state.conflictQueue.shift();
    $('#dup-text').text(`"${state.currentConflict.existing.titre}" existe déjà.`);
    const modal = new bootstrap.Modal(document.getElementById('duplicateDocumentModal'));
    modal.show();
  },

  handleVersion() {
    const state = DocumentState.get();
    state.actions.push({
      file: state.currentConflict.file,
      action: 'version',
      id: state.currentConflict.existing.document_id
    });
    bootstrap.Modal.getInstance(document.getElementById('duplicateDocumentModal')).hide();
    this.showNextConflict();
  },

  handleOverwrite() {
    const state = DocumentState.get();
    state.actions.push({
      file: state.currentConflict.file,
      action: 'overwrite',
      id: state.currentConflict.existing.document_id
    });
    bootstrap.Modal.getInstance(document.getElementById('duplicateDocumentModal')).hide();
    this.showNextConflict();
  },

  async submitUpload() {
    const state = DocumentState.get();
    const formData = new FormData($('#upload-form')[0]);
    formData.delete('fichiers');
    state.uploadQueue.forEach(f => formData.append('fichiers', f));
    state.actions.forEach(a => {
      formData.append('fichiers', a.file);
      formData.append('actions[]', JSON.stringify(a));
    });

    try {
      const res = await DocumentService.upload(formData, DocumentUI.updateProgress);
      showAlertMessage(res.message || 'Upload terminé', '#form-success');
      DocumentUI.resetForm();
      this.loadDocuments();
    } catch (err) {
      showAlertMessage('Erreur lors du transfert', '#form-error');
    }
  }
};
