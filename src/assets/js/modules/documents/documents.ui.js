// modules/documents/documents.ui.js
import { showAlertMessage, resetForm, renderPagination, disableElement, enableElement } from '../../helpers/utils.js';
import { FilterHelper } from './helpers/filter.helper.js';
export const DocumentUi = {
  currentView: 'table', // 'folder', 'table', ou 'grid'

  currentType: null,
  currentSubtype: null,

  /**
   * Rendu de la vue des documents
   * @param {*} response - La réponse de l'API contenant les documents à afficher
   */
  render(response) {
    const documents = response.results || response;

    // Cache systématique de tous les layouts
    $('#document-folder-view, #document-table-view, #document-grid-view').addClass('d-none');

    if (this.currentView === 'folder') {
      // 1. Rendu graphique des répertoires virtuels et du fil d'Ariane
      this.renderFolders(documents);
      $('#document-folder-view').removeClass('d-none');
    } else if (this.currentView === 'table') {
      this.renderTable(documents);
      $('#document-table-view').removeClass('d-none');
    } else if (this.currentView === 'grid') {
      this.renderGrid(documents);
      $('#document-grid-view').removeClass('d-none');
    }

    this.renderPagination(response);
  },

  /**
   * Rendu de la grille de dossiers (fil d'Ariane et navigation par type/sous-type)
   * @param {Array} documents - La liste des documents à afficher
   */
  renderFolders(documents = []) {
    const $foldersGrid = $('#folders-grid');
    $foldersGrid.empty();

    const searchTerm = $('#search').val()?.toLowerCase().trim() || '';

    // NIVEAU 1 : Racine -> On liste tous les types de documents présents dans le select du filtre
    if (!this.currentType && !this.currentSubtype) {
      const typesList = [];
      $('#id_type_document option').each(function () {
        if ($(this).val()) {
          typesList.push({ id: $(this).val(), label: $(this).text() });
        }
      });

      // Filtrage local "Search-as-you-type" des types de dossiers
      const filteredTypes = typesList.filter(t => t.label.toLowerCase().includes(searchTerm));

      if (filteredTypes.length > 0) {
        const html = filteredTypes.map(t => this.createFolderHtml(t.id, t.label, 'type')).join('');
        $foldersGrid.html(html);
      } else {
        $foldersGrid.html(
          '<div class="col-lg-12 text-center text-muted small italic ps-2">Aucun dossier ne correspond à la recherche.</div>'
        );
      }
    }
    // NIVEAU 2 : Dans un Type -> On extrait et liste ses sous-types associés
    else if (this.currentType && !this.currentSubtype) {
      const subTypesList = [];
      $('#id_sous_type option').each(function () {
        const parentType = $(this).data('type') || $(this).attr('data-type');
        if ($(this).val() && (!parentType || String(parentType) === String(DocumentUi.currentType))) {
          subTypesList.push({ id: $(this).val(), label: $(this).text() });
        }
      });

      // Filtrage local des sous-types
      const filteredSubtypes = subTypesList.filter(st => st.label.toLowerCase().includes(searchTerm));
      let finalHtml = '';

      if (filteredSubtypes.length > 0) {
        finalHtml += filteredSubtypes.map(st => this.createFolderHtml(st.id, st.label, 'subtype')).join('');
      }

      // ─── CRUCIAL : Injection des Documents Orphelins de sous-type au même niveau ───
      if (documents && documents.length > 0) {
        finalHtml += documents.map(doc => this.createFileInlineHtml(doc)).join('');
      }

      if (filteredSubtypes.length === 0 && (!documents || documents.length === 0)) {
        finalHtml =
          '<div class="col-lg-12 text-center text-muted small italic ps-2">Au élément ne correspond à la recherche.</div>';
      }

      $foldersGrid.html(finalHtml);
    }
    // NIVEAU 3 : Dans un sous-type terminal -> La grille de dossier s'efface (la table s'affiche en dessous)
    else {
      if (documents && documents.length > 0) {
        const html = documents.map(doc => this.createFileInlineHtml(doc)).join('');
        $foldersGrid.html(html);
      } else {
        $foldersGrid.html(
          '<div class="col-lg-12 text-center text-muted small italic ps-2">Aucun document dans ce sous-dossier.</div>'
        );
      }
    }

    this.updateBreadcrumb();
  },

  // 🟢 AJOUT : Rendu d'un fichier au look "Explorateur OS"
  createFileInlineHtml(doc) {
    const fileExt = doc.extension || 'unknown';
    const isPdf = fileExt === 'pdf';
    const isWord = ['doc', 'docx'].includes(fileExt);
    const isExcel = ['xls', 'xlsx'].includes(fileExt);

    const iconClass = isPdf
      ? 'ri-file-pdf-fill text-danger'
      : isWord
        ? 'ri-file-word-fill text-primary'
        : isExcel
          ? 'ri-file-excel-fill text-success'
          : 'ri-file-text-fill text-secondary';

    return `
      <div class="col-12 col-sm-6 col-md-4 col-lg-3 mb-3">
        <div class="card h-100 border p-2 d-flex flex-row align-items-center file-item-click shadow-none"
            style="cursor: pointer; border-radius: 12px; transition: background 0.2s;"
            onmouseover="this.style.backgroundColor='#f8f9fa'"
            onmouseout="this.style.backgroundColor='transparent'"
            data-id="${doc.id}" data-action="view">
          <div class="me-3" style="font-size: 2.2rem;">
            <i class="${iconClass}"></i>
          </div>
          <div class="overflow-hidden flex-grow-1">
            <h6 class="mb-0 text-truncate font-weight-bold text-dark" style="font-size: 0.85rem;" title="${doc.titre}">${doc.titre}</h6>
            <small class="text-muted text-uppercase" style="font-size: 0.7rem;">${fileExt} • ${new Date(doc.Date_creation).toLocaleDateString()}</small>
          </div>
        </div>
      </div>
    `;
  },

  createFolderHtml(id, label, level) {
    return `
    <div class="col-3 mb-4">
      <div class="card h-100 border border-dashed text-center folder-item"
           style="cursor: pointer; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); border-radius: 16px; background: transparent;"
           onmouseover="this.style.backgroundColor='#ffffff'; this.style.borderStyle='solid'; this.style.borderColor='#ff9f43'; this.style.boxShadow='0 10px 20px rgba(255, 159, 67, 0.08)';"
           onmouseout="this.style.backgroundColor='transparent'; this.style.borderStyle='dashed'; this.style.borderColor='rgba(0,0,0,0.12)'; this.style.boxShadow='none';"
           data-id="${id}"
           data-level="${level}">

        <div class="card-body p-4 d-flex flex-column align-items-center justify-content-center">
          <div class="avatar mb-3" style="width: 56px; height: 56px;">
            <span class="avatar-initial rounded-circle d-flex align-items-center justify-content-center"
                  style="background: linear-gradient(135deg, rgba(255, 159, 67, 0.15) 0%, rgba(255, 159, 67, 0.05) 100%); color: #ff9f43; font-size: 2rem;">
              <i class="ri-folder-2-fill"></i>
            </span>
          </div>
          <h6 class="mb-1 text-wrap fw-bold text-heading text-truncate w-100" style="font-size: 0.88rem; letter-spacing: -0.2px;">${label}</h6>
        </div>

      </div>
    </div>
  `;
  },

  updateBreadcrumb() {
    const $breadcrumb = $('#directory-breadcrumb');
    $breadcrumb.html(`
      <li class="breadcrumb-item ${!this.currentType ? 'active' : ''}" data-level="root" style="cursor: pointer;">
        <i class="ri-home-4-line me-1"></i>Racine
      </li>
    `);

    if (this.currentType) {
      const typeLabel = $(`#id_type_document option[value="${this.currentType}"]`).text();
      $breadcrumb.append(`
        <li class="breadcrumb-item ${!this.currentSubtype ? 'active' : ''}" data-level="type" data-id="${this.currentType}" style="cursor: pointer;">
          ${typeLabel}
        </li>
      `);
    }

    if (this.currentSubtype) {
      const subtypeLabel = $(`#id_sous_type option[value="${this.currentSubtype}"]`).text();
      $breadcrumb.append(`
        <li class="breadcrumb-item active" data-level="subtype" data-id="${this.currentSubtype}">
          ${subtypeLabel}
        </li>
      `);
    }
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
    //const fileExt = doc.fichier.split('.').pop().toLowerCase();
    const fileExt = doc.extension || 'unknown';
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
    if (this.currentView === 'folder') {
      $('#documents-pagination, #pagination-info').addClass('d-none').empty();
      return;
    }

    $('#documents-pagination, #pagination-info').removeClass('d-none');
    renderPagination(data, '#documents-pagination', '#pagination-info');
  },

  /**
   * Prépare le formulaire de création ou d'édition de document
   * @param {Object|null} contextData - Le bloc complet renvoyé par l'API retrieve (contient document et options_formulaire)
   */
  renderForm(contextData = null) {
    const isEdit = !!contextData;
    const $form = $('#documentForm');

    // Reset complet du formulaire
    $form[0].reset();

    // Si on est en édition, on extrait l'objet document
    const data = isEdit ? contextData.document : null;

    $('#update-id').val(isEdit ? data.id : '');
    $('#modal-title').text(isEdit ? 'Modifier le document' : 'Enregistrement multiple');
    $('#save-btn-text').text(isEdit ? 'Mettre à jour' : 'Enregistrer');

    if (isEdit) {
      // --- MODE ÉDITION ---
      $('#container-titre').removeClass('d-none');
      $('#container-fichier-unique').removeClass('d-none');
      $('#container-dropzone').addClass('d-none');

      // 🟢 RECONSTRUCTION DYNAMIQUE DES SELECTS (Pour éviter le blocage transverse)
      if (contextData.options_formulaire) {
        this.rebuildSelectOptions('#cellule', contextData.options_formulaire.cellules, 'nom', data.cellule);
        this.rebuildSelectOptions(
          '#type_document',
          contextData.options_formulaire.types_documents,
          'libelle',
          data.type_document
        );
        this.rebuildSelectOptions('#theme', contextData.options_formulaire.themes, 'libelle', data.theme);
        this.rebuildSelectOptions('#sous_type', contextData.options_formulaire.sous_types, 'libelle', data.sous_type);
      }

      // Remplissage des données
      $('#titre').val(data.titre);
      $('#type_document').val(data.type_document).trigger('change');
      $('#sous_type').val(data.sous_type).trigger('change');
      $('#theme').val(data.theme).trigger('change');
      $('#cellule').val(data.cellule).trigger('change');
      $('#niveau_acces').val(data.niveau_acces).trigger('change');
      $('#profil_document').val(data.profil_document).trigger('change');
      $('#etat').val(data.etat).trigger('change');

      if (data.fichier) {
        $('#current-file-info').html(
          `<i class="ri-link"></i> Fichier actuel : <a href="#" data-action="view" data-id="${data.id}" target="_blank" class="text-decoration-underline text-primary">Consulter</a>`
        );
      }
    } else {
      // --- MODE CRÉATION ---
      $('#container-titre').addClass('d-none');
      $('#container-fichier-unique').addClass('d-none');
      $('#container-dropzone').removeClass('d-none');
      FilterHelper.resetFilters('#documentForm');
      $('#previews').empty();
      $('#current-file-info').empty();
      $('#file-input').val('');
    }
  },

  /**
   * Fonction utilitaire pour reconstruire proprement un Select avec les options autorisées
   */
  rebuildSelectOptions(selector, items, textProperty, selectedId) {
    const $select = $(selector);
    $select.empty().append('<option value="">-- Sélectionner --</option>');

    if (!items) return;

    items.forEach(item => {
      const isSelected = String(item.id) === String(selectedId) ? 'selected' : '';
      // Ajout de data-attributes si besoin (ex: type_document_id pour le chaînage des sous-types)
      const dataAttr = item.type_document_id ? `data-type="${item.type_document_id}"` : '';

      $select.append(`<option value="${item.id}" ${isSelected} ${dataAttr}>${item[textProperty]}</option>`);
    });
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
    $('#update-id').val('');
    const $documentSelect = $('#doc-select');
    if ($documentSelect.length) {
      $documentSelect.val(documentId).trigger('change');
      disableElement($documentSelect);
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
    const $documentSelect = $form.find('#document');

    if ($documentSelect.length) {
      $documentSelect.val(documentId).trigger('change');
      disableElement($documentSelect);
    }

    // On cible les éléments du modal de document spécifique
    const $modal = $('#create-documentTache-modal');
    $modal.find('#modal-title').text('Nouvelle tâche pour ce document');
    $modal.find('#save-btn-text').text('Créer la tâche');
    $modal.find('#form-error, #form-success').hide();
  }
};
