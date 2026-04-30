// modules/documents/documents.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../helpers/utils.js';
export const DocumentUi = {
  currentView: 'table', // 'table' ou 'grid'
  // pour le rendu de la liste
  render(response) {
    const documents = response.results || response;

    if (this.currentView === 'table') {
      this.renderTable(documents);
      $('#document-table-view').removeClass('d-none');
      $('#document-grid-view').addClass('d-none');
    } else {
      this.renderGrid(documents);
      $('#document-grid-view').removeClass('d-none');
      $('#document-table-view').addClass('d-none');
    }

    this.renderPagination(response);
  },

  renderGrid(response) {
    const documents = response.results || response;
    const container = $('#documents-grid-body');
    container.empty();
    if (!documents || documents.length === 0) {
      container.html('<div class="col-12 text-center my-5"><h5 class="text-white">Aucun document trouvé</h5></div>');
      return;
    }
    const cards = documents.map(doc => this.createDocumentCard(doc)).join('');
    container.html(cards);
    this.renderPagination(response);
    // Réinitialisation identique au mode tableau
    $('#check-all-documents-grid').prop('checked', false);
    $('#check-all-documents').prop('checked', false); // Désactive aussi l'autre au cas où
    $('#bulk-actions-container').addClass('d-none');
  },

  createDocumentCard(doc) {
    const etatBadge = this.getEtatBadge(doc);
    const fileExt = doc.fichier.split('.').pop().toLowerCase();
    const isImage = ['jpg', 'jpeg', 'png', 'gif'].includes(fileExt);
    const p = doc.user_actions;

    // Logique de l'aperçu
    const isPdf = fileExt === 'pdf';
    const isWord = ['doc', 'docx'].includes(fileExt);
    const isExcel = ['xls', 'xlsx'].includes(fileExt);

    const iconClass = isPdf
      ? 'ri-file-pdf-line'
      : isWord
        ? 'ri-file-word-line'
        : isExcel
          ? 'ri-file-excel-line'
          : 'ri-file-text-line';
    const bgClass = isPdf
      ? 'bg-label-danger'
      : isWord
        ? 'bg-label-primary'
        : isExcel
          ? 'bg-label-success'
          : 'bg-label-secondary';

    const preview = isImage
      ? `<img src="${doc.fichier}" class="card-img-top" style="height:150px; object-fit:cover;">`
      : `<div class="d-flex align-items-center justify-content-center bg-light position-relative" style="height:150px;">
           <div class="text-center">
             <i class="${iconClass} text-secondary" style="font-size:3rem;"></i><br>
             <strong class="text-uppercase">${fileExt}</strong>
           </div>
           <div class="avatar position-absolute bottom-0 end-0 m-2">
             <span class="avatar-initial rounded ${bgClass}">
               <i class="${iconClass} ri-24px"></i>
             </span>
           </div>
        </div>`;

    return `
      <div class="col-6 col-sm-4 col-md-3 mb-4">
        <div class="card h-100 shadow-sm border">
          <div class="position-absolute top-0 start-0 p-2" style="z-index: 10;">
            <input class="form-check-input document-checkbox" type="checkbox" value="${doc.id}">
          </div>
          <a href="#" data-action="view" data-id="${doc.id}">${preview}</a>
          <div class="card-body p-2">
            <h6 class="card-title mb-1 text-truncate">
              <a href="#" data-action="view" data-id="${doc.id}" class="text-decoration-none text-dark">${doc.titre}</a>
            </h6>
            <p class="mb-1 small text-muted">${doc.type_doc_display || '-'}</p>
            <div class="mb-2">${etatBadge}</div>
            <small class="text-muted d-block" style="font-size:0.7rem;">${new Date(doc.Date_creation).toLocaleDateString()}</small>
          </div>

          <div class="card-footer bg-transparent p-2">
            <div class="btn-group w-100 mb-1">
                <button title="Voir(détails)" class="btn btn-sm btn-outline-primary" data-action="view" data-id="${doc.id}"><i class="ri-eye-line"></i></button>

                <button title="Modifier" class="btn btn-sm btn-outline-primary ${!p.can_edit ? 'disabled' : ''}"
                        data-action="edit" data-id="${doc.id}">
                    <i class="ri-pencil-line"></i>
                </button>

                <a href="${doc.fichier}" title="Télécharger" target="_blank"
                   class="btn btn-sm btn-outline-secondary ${!p.can_print ? 'disabled' : ''}">
                    <i class="ri-download-line"></i>
                </a>
            </div>
            <div class="btn-group w-100">
                <button title="Ajouter une circulation" class="btn btn-sm btn-outline-info ${!p.can_share ? 'disabled' : ''}" data-action="add-circulation" data-id="${doc.id}">
                    <i class="ri-share-forward-line"></i>
                </button>
                ${
                  p.can_addTask
                    ? `<button title="Ajouter une tache" class="btn btn-sm btn-outline-info" id="add-documentTask-button" data-action="add-tache" data-id="${doc.id}"><i class="ri-task-line"></i></button>`
                    : ''
                }
                ${
                  p.can_delete
                    ? `
                    <button title="Supprimer" class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${doc.id}">
                        <i class="ri-delete-bin-6-line"></i>
                    </button>`
                    : ''
                }
            </div>
          </div>

        </div>
      </div>`;
  },

  // Mapper des couleurs par rôle
  etatColors: {
    'en attente': 'bg-warning',
    attente: 'bg-warning',
    'en traitement': 'bg-primary',
    valide: 'bg-success',
    archive: 'bg-secondary'
  },

  // Helper pour générer le badge de rôle
  getEtatBadge(document) {
    const colorClass = this.etatColors[document.etat] || 'bg-secondary';

    return `<span class="badge rounded-pill ${colorClass}">
              ${document.etat}
            </span>`;
  },

  // ─── Rendu de la table ───────────────────────────────────────────────────

  // Modifiez votre renderTable pour n'accepter que la liste
  renderTable(documents) {
    const tbody = $('#documents-tbody');
    tbody.empty();
    if (!documents || documents.length === 0) {
      tbody.html('<tr><td colspan="10" class="text-center">Aucun document trouvé</td></tr>');
      return;
    }
    const rows = documents.map(doc => this.createDocumentRow(doc)).join('');
    tbody.html(rows);
    // Réinitialiser la checkbox globale
    $('#check-all-documents').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  // Rendu d'une ligne document
  createDocumentRow(document) {
    const etatBadge = this.getEtatBadge(document);
    const p = document.user_actions;
    return `
      <tr data-document-id="${document.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input document-checkbox" type="checkbox" value="${document.id}">
          </div>
        </th>
        <td>${document.titre}</td>
        <td>${document.type_doc_display || '-'}</td>
        <td>${document.sous_type_display || '-'}</td>
        <td>${document.theme_display || '-'}</td>
        <td>${document.cellulle_display || '-'}</td>
        <td>${etatBadge}</td>
        <td>${document.cree_par_display || '-'}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="view" data-id="${document.id}">
                <i class="ri-eye-line me-1"></i>Détails
              </a>

              ${
                p.can_edit
                  ? `
                <a href="#" class="dropdown-item" data-action="edit" data-id="${document.id}">
                  <i class="ri-pencil-line me-1"></i>Modifier
                </a>`
                  : ''
              }

              ${
                p.can_share
                  ? `
                <a href="#" class="dropdown-item" data-action="add-circulation" data-id="${document.id}">
                  <i class="ri-share-forward-line me-1"></i>Ajouter une circulation
                </a>`
                  : ''
              }

              ${
                p.can_addTask
                  ? `
                <a href="#" class="dropdown-item" data-action="add-tache" data-id="${document.id}">
                  <i class="ri-task-line me-1"></i>Ajouter une tache
                </a>`
                  : ''
              }

              <a href="${document.fichier}" target="_blank" class="dropdown-item ${!p.can_print ? 'disabled' : ''}">
                <i class="ri-download-line me-1"></i>Télécharger
              </a>

              ${
                p.can_delete
                  ? `
                <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${document.id}">
                  <i class="ri-delete-bin-6-line me-1"></i>Supprimer
                </a>`
                  : ''
              }
            </div>
          </div>
        </td>
      </tr>
    `;
  },

  // Rendu de la pagination
  renderPagination(data) {
    renderPagination(data, '#documents-pagination', '#pagination-info');
  },

  // ─── Remplissage du formulaire ───────────────────────────────────────────
  renderForm(data = null) {
    const isEdit = !!data;
    const $form = $('#documentForm');

    // Reset complet du formulaire
    $form[0].reset();
    $('#update-id').val(isEdit ? data.id : '');
    $('#modal-title').text(isEdit ? 'Modifier le document' : 'Enregistrement multiple');
    $('#save-btn-text').text(isEdit ? 'Mettre à jour' : 'Enregistrer');

    if (isEdit) {
      // --- MODE ÉDITION ---
      $('#container-titre').removeClass('d-none'); // On montre le titre
      $('#container-fichier-unique').removeClass('d-none'); // On montre l'input file simple
      $('#container-dropzone').addClass('d-none'); // On cache la dropzone

      // Remplissage des données
      $('#titre').val(data.titre);
      $('#type_document').val(data.type_document).trigger('change');
      $('#sous_type').val(data.sous_type);
      $('#theme').val(data.theme);
      $('#cellule').val(data.cellule);
      $('#niveau_acces').val(data.niveau_acces);
      $('#profil_document').val(data.profil_document);
      $('#etat').val(data.etat);

      if (data.fichier) {
        $('#current-file-info').html(
          `<i class="ri-link"></i> Fichier actuel : <a href="${data.fichier}" target="_blank" class="text-decoration-underline text-primary">Consulter</a>`
        );
      }
    } else {
      // --- MODE CRÉATION ---
      $('#container-titre').addClass('d-none'); // On cache le titre (sera généré par le nom du fichier)
      $('#container-fichier-unique').addClass('d-none'); // On cache l'input file simple
      $('#container-dropzone').removeClass('d-none'); // On montre la dropzone

      $('#previews').empty();
      $('#current-file-info').empty();
      $('#file-input').val('');
    }
  },

  resetForm(formSelector) {
    $(formSelector)[0].reset();
  },

  showError(message, id = '#message-show-error', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  },

  showSuccess(message, id = '#message-show-success', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  },

  /**
   * Prépare le modal de création de la circualation avec un document pré-sélectionné
   * @param {string|number} documentId - L'ID du document
   */
  renderCirculatFormForDocument(documentId) {
    const $form = $('#documentCirculationForm');
    $form[0].reset();
    $('#etapes-container').empty();

    // On vide l'ID d'update pour être sûr d'être en mode création
    // $('#update-id').val('');
    const $documentSelect = $('#doc-select');
    console.log('document select : ', $documentSelect);
    if ($documentSelect.length) {
      $documentSelect.val(documentId).trigger('change');
      $documentSelect
        .css({
          'pointer-events': 'none',
          'background-color': '#e9ecef'
        })
        .attr('tabindex', '-1');
      $documentSelect.trigger('change');
    }

    $('#modal-title').text('Nouvelle Circulation pour un document');
    $('#save-btn-text').text('Initier la Circulation');
    $('#form-error, #form-success').hide();
  },

  /**
   * Prépare le modal de création de tâche avec un document pré-sélectionné
   * @param {string|number} documentId - L'ID du document
   */
  renderTacheFormForDocument(documentId) {
    const $form = $('#documentTacheForm');
    $form[0].reset();
    $('#update-id').val('');
    const $documentSelect = $('#document');
    if ($documentSelect.length) {
      $documentSelect.val(documentId).trigger('change');
      $documentSelect
        .css({
          'pointer-events': 'none',
          'background-color': '#e9ecef'
        })
        .attr('tabindex', '-1');
    }

    $('#modal-title').text('Nouvelle tâche pour ce document');
    $('#save-btn-text').text('Créer la tâche');

    // Nettoyage des alertes précédentes
    $('#form-error, #form-success').hide();
  }
};
