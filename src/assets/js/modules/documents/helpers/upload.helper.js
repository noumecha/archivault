// modules/documents/helpers/upload.helper.js
import { DocumentService } from '../documents.services.js';
import { DocumentUi } from '../documents.ui.js';
import { startLoader, closeLoader } from '../../../helpers/utils.js';

export const UploadHelper = {
  async handleMultipleUpload(controller) {
    const files = [...controller.allFiles.files];
    if (files.length === 0) {
      return DocumentUi.showError('Sélectionnez au moins un fichier', '#form-error');
    }

    controller.conflictQueue = [];
    controller.uploadQueue = [];
    controller.actions = [];

    try {
      startLoader('#form-loader');

      // Étape 1 : Vérification des doublons sur le serveur
      await Promise.all(files.map(file => this.checkFileConflict(file, controller)));

      // Étape 2 : Si conflits, on gère la modale, sinon on envoie tout
      if (controller.conflictQueue.length > 0) {
        this.showNextConflict(controller);
      } else {
        await this.submitFinalForm(controller);
      }
    } catch (err) {
      controller.handleError(err);
    } finally {
      closeLoader('#form-loader');
    }
  },

  async checkFileConflict(file, controller) {
    if (!file || !file.name) return;
    try {
      const res = await DocumentService.checkConflict(file.name);
      if (res.exists) {
        controller.conflictQueue.push({ file: file, existing: res });
      } else {
        controller.uploadQueue.push(file);
      }
    } catch (err) {
      console.error(`Erreur de check pour ${file.name}:`, err);
      controller.uploadQueue.push(file);
    }
  },

  showNextConflict(controller) {
    if (controller.conflictQueue.length === 0) {
      this.submitFinalForm(controller);
      return;
    }

    controller.currentConflict = controller.conflictQueue.shift();
    const modalEl = document.getElementById('duplicateDocumentModal');

    if (!modalEl) {
      console.error('La modale #duplicateDocumentModal est introuvable dans le HTML');
      return;
    }

    const fileName = controller.currentConflict.file.name;
    $('#dup-text').html(`Le fichier <strong>${fileName}</strong> existe déjà.<br>Que souhaitez-vous faire ?`);

    this.bindConflictButtons(controller);

    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
    modalInstance.show();
  },

  bindConflictButtons(controller) {
    const modalEl = document.getElementById('duplicateDocumentModal');

    let modalInstance = bootstrap.Modal.getInstance(modalEl);
    if (!modalInstance) {
      modalInstance = new bootstrap.Modal(modalEl);
    }

    $('#btn-version, #btn-overwrite, #btn-skip').off('click');

    const handleAction = actionType => {
      controller.actions.push({
        file: controller.currentConflict.file,
        name: controller.currentConflict.file.name,
        action: actionType,
        documentId: controller.currentConflict.existing.document_id
      });

      controller.uploadQueue.push(controller.currentConflict.file);
      modalInstance.hide();
    };

    $('#btn-version').on('click', () => handleAction('version'));
    $('#btn-overwrite').on('click', () => handleAction('overwrite'));

    $('#btn-skip').on('click', () => {
      controller.actions.push({ name: controller.currentConflict.file.name, action: 'skip' });
      modalInstance.hide();
    });

    $(modalEl)
      .off('hidden.bs.modal')
      .on('hidden.bs.modal', () => {
        this.showNextConflict(controller);
      });
  },

  async submitFinalForm(controller) {
    const $form = $('#documentForm');
    const formData = new FormData($form[0]);

    formData.delete('fichiers');
    formData.delete('actions[]');
    formData.delete('fichier');

    controller.uploadQueue.forEach(file => {
      if (file) formData.append('fichiers', file);
    });

    controller.actions.forEach(a => {
      if (a && a.file) {
        formData.append('fichiers', a.file);
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

    try {
      startLoader('#form-loader');
      const response = await DocumentService.bulkCreate(formData);

      DocumentUi.showSuccess(response.message || 'Upload terminé', '#form-success');

      controller.allFiles = new DataTransfer();
      controller.uploadQueue = [];
      controller.actions = [];

      controller.finalizeSubmission($form);
    } catch (err) {
      controller.handleError(err);
    } finally {
      closeLoader('#form-loader');
    }
  }
};
