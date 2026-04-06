// documents.controllers.js
import { DocumentState } from './documents.states.js';
import { DocumentUI } from './documents.ui.js';
import { DocumentService } from './documents.services.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const DocumentController = (function (State, UI, Service) {
  function init() {
    initCRUD({
      moduleName: 'document',
      baseUrl: '/document/documents/',
      fetchUrl: '/document/documents/all/',
      formSelector: '#documentForm',
      modalSelector: '#create-document-modal',
      formContainerSelector: '#document-form-content',
      tableContainerSelector: '#document-table-container',
      searchFormSelector: '#document-search-form',
      searchInputSelector:
        '#search,#id_type_document,#id_sous_type,#id_etat,#id_profil_document,#id_theme,#id_bailleur',
      clearBtnSelector: '#clearSearch'
    });
    bindEvents();
  }

  function bindEvents() {
    const $dropArea = $('#drop-area');
    const $fileInput = $('#file-input');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => $dropArea.on(evt, UI.preventDefaults));

    $dropArea.on('dragenter dragover', () => UI.highlight($dropArea));
    $dropArea.on('dragleave drop', () => UI.unhighlight($dropArea));

    $dropArea.on('drop', function (e) {
      const dt = new DataTransfer();
      Array.from(e.originalEvent.dataTransfer.files).forEach(f => dt.items.add(f));
      $fileInput[0].files = dt.files;
      UI.renderPreviews([...dt.files], $('#previews'));
    });

    $('#browse-btn').on('click', () => $fileInput.click());

    $fileInput.on('change', function () {
      UI.renderPreviews([...this.files], $('#previews'));
    });

    $(document).on('file:remove', function (_, index) {
      const dt = new DataTransfer();
      Array.from($fileInput[0].files).forEach((f, i) => {
        if (i !== index) dt.items.add(f);
      });
      $fileInput[0].files = dt.files;
      UI.renderPreviews([...dt.files], $('#previews'));
    });

    $('#upload-form').on('submit', handleSubmit);

    $('#btn-version').on('click', handleVersion);
    $('#btn-overwrite').on('click', handleOverwrite);
  }

  function handleSubmit(e) {
    e.preventDefault();

    const files = [...$('#file-input')[0].files];
    if (!files.length) {
      showAlertMessage('Ajoutez au moins un fichier', '#form-error');
      return;
    }

    State.reset();

    const state = State.get();

    Promise.all(files.map(f => Service.checkConflict(f))).then(results => {
      results.forEach((data, i) => {
        if (data.exists) {
          state.conflictQueue.push({ file: files[i], existing: data });
        } else {
          state.uploadQueue.push(files[i]);
        }
      });

      if (!state.conflictQueue.length) {
        submit();
      } else {
        showNextConflict();
      }
    });
  }

  function showNextConflict() {
    const state = State.get();

    if (!state.conflictQueue.length) {
      submit();
      return;
    }

    state.currentConflict = state.conflictQueue.shift();

    $('#dup-text').text(`Le document "${state.currentConflict.existing.titre}" existe déjà.`);
    $('#duplicateDocumentModal').modal('show');
  }

  function handleVersion() {
    const state = State.get();

    state.actions.push({
      file: state.currentConflict.file,
      action: 'version',
      documentId: state.currentConflict.existing.document_id
    });

    $('#duplicateDocumentModal').modal('hide');
    showNextConflict();
  }

  function handleOverwrite() {
    const state = State.get();

    state.actions.push({
      file: state.currentConflict.file,
      action: 'overwrite',
      documentId: state.currentConflict.existing.document_id
    });

    $('#duplicateDocumentModal').modal('hide');
    showNextConflict();
  }

  function submit() {
    const state = State.get();
    const formData = new FormData($('#upload-form')[0]);

    formData.delete('fichiers');

    state.uploadQueue.forEach(f => formData.append('fichiers', f));

    state.actions.forEach(a => {
      formData.append('fichiers', a.file);
      formData.append('actions[]', JSON.stringify(a));
    });

    Service.upload(formData, UI.updateProgress)
      .done(res => {
        showAlertMessage(res.message, '#form-success');
        UI.resetForm();
        State.reset();
      })
      .fail(() => {
        showAlertMessage('Erreur upload', '#form-error');
      });
  }

  return { init };
})(DocumentState, DocumentUI, DocumentService);
