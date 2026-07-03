// src/assets/js/modules/circulations/circulations.ui.js
import { showAlertMessage, resetForm, renderPagination, disableElement, enableElement } from '../../helpers/utils.js';

export const CirculationUi = {
  etapeIndex: 0,
  // Configuration des statuts pour les badges
  statusColors: {
    en_attente: 'bg-secondary',
    en_cours: 'bg-primary',
    valide: 'bg-success',
    rejete: 'bg-danger',
    retourne: 'bg-warning',
    clos: 'bg-info'
  },

  /**
   * Rendu d'un badge de statut
   * @param {*} statut - Le code du statut (ex: 'en_attente', 'valide')
   * @param {*} display - Le texte à afficher (optionnel, sinon utilise le statut)
   * @returns {string} HTML du badge
   */
  getStatusBadge(statut, display) {
    const colorClass = this.statusColors[statut] || 'bg-secondary';
    return `<span class="badge rounded-pill ${colorClass}">${display || statut}</span>`;
  },

  /**
   * Rendu de la table principale des circulations
   * @param {*} response - Données de réponse contenant la liste des circulations
   * @returns {void}
   */
  renderTable(response) {
    const tbody = $('#circulations-tbody');
    tbody.empty();

    const circulations = response.results || response;

    if (!circulations || circulations.length === 0) {
      tbody.html('<tr><td colspan="10" class="text-center">Aucun circuit de circulation trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = circulations.map(circ => this.createCirculationRow(circ)).join('');
    tbody.html(rows);

    this.renderPagination(response);
  },

  /**
   * Rendu d'une ligne de circulation dans la table principale
   * @param {*} circ - Objet circulation à afficher
   * @returns {string} HTML de la ligne
   */
  createCirculationRow(circ) {
    const statusBadge = this.getStatusBadge(circ.statut, circ.statut_display);
    const dateDebut = new Date(circ.date_debut).toLocaleDateString();

    // Calcul de la progression (ex: 2/5 étapes)
    const totalEtapes = circ.etapes_count || 0;
    const etapeActuelleOrdre = circ.etape_actuelle ? circ.etape_actuelle.ordre : totalEtapes;
    const isClos = circ.statut === 'clos';
    const actuelActeurId = circ.etape_actuelle ? circ.etape_actuelle.destinataire : '';

    return `
      <tr data-circulation-id="${circ.id}" data-actuel-acteur-id="${actuelActeurId}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input circulation-checkbox" type="checkbox" value="${circ.id}">
          </div>
        </th>
        <td><strong>${circ.document_titre || '-'}</strong></td>
        <td>${circ.titre}</td>
        <td>${circ.initie_par_name || '-'}</td>
        <td>${dateDebut}</td>
        <td>
            <div class="d-flex flex-column">
                <small class="mb-1">Progression: ${etapeActuelleOrdre}/${totalEtapes}</small>
                <div class="progress" style="height: 6px;">
                    <div class="progress-bar" role="progressbar" style="width: ${(etapeActuelleOrdre / totalEtapes) * 100}%"></div>
                </div>
            </div>
        </td>
        <td>${statusBadge}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="view" data-id="${circ.id}">
                <i class="ri-eye-line me-1"></i>Détails
              </a>
              <a href="#" class="dropdown-item" data-action="view-timeline" data-id="${circ.id}">
                <i class="ri-git-commit-line me-1"></i>Voir Timeline
              </a>
              <a href="#" class="dropdown-item ${isClos ? 'disabled' : ''}" data-doc-titre="${circ.document_titre}" data-ordre="${circ.etape_actuelle?.ordre}"
                data-action="process" data-id="${circ.id}">
                <i class="ri-checkbox-circle-line me-1"></i>Traiter l'étape
              </a>
              <div class="dropdown-divider"></div>
              <a href="#" class="dropdown-item text-primary ${isClos || !circ.can_update ? 'disabled' : ''}" data-action="edit-circulation" data-id="${circ.id}">
                <i class="ri-edit-line me-1"></i>Modifier
              </a>
              <a href="#" class="dropdown-item text-danger  ${isClos || !circ.can_delete ? 'disabled' : ''}" data-action="delete-circulation" data-id="${circ.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>
            </div>
          </div>
        </td>
      </tr>`;
  },

  /**
   * Méthode pour l'affichage de la timeline dans un modal avec en-tête récapitulatif
   * @param {*} circulation - Objet circulation contenant les étapes à afficher
   * @returns {void}
   */
  renderTimeline(circulation) {
    const container = $('#timeline-container');
    container.empty();

    if (!circulation.etapes || circulation.etapes.length === 0) {
      container.html('<p class="text-center">Aucune étape définie</p>');
      return;
    }

    // 1. Génération de l'en-tête de la circulation (Titre et Statut Global)
    const headerHtml = `
        <div class="card bg-lighter border-0 mb-4">
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <small class="text-uppercase text-muted fw-semibold d-block mb-1" style="font-size: 0.7rem; letter-spacing: 1px;">Circuit de circulation</small>
                        <h5 class="mb-0 text-dark fw-bold">${circulation.titre}</h5>
                    </div>
                    <div class="text-end">
                        <small class="text-muted d-block mb-1 small">Statut actuel</small>
                        ${this.getStatusBadge(circulation.statut, circulation.statut_display)}
                    </div>
                </div>
            </div>
        </div>
        <div class="ps-2 mb-3">
            <h6 class="text-muted fw-normal"><i class="ri-git-merge-line me-1"></i> Progression des étapes</h6>
        </div>
    `;

    // 2. Génération des items de la timeline
    const timelineHtml = circulation.etapes
      .map((etape, index) => {
        const isCompleted = ['valide', 'rejete', 'retourne'].includes(etape.statut);
        const isActive = etape.est_actuelle;

        // Logique d'icône optimisée
        let iconClass = 'ri-checkbox-blank-circle-line text-muted';
        if (isCompleted) iconClass = 'ri-checkbox-circle-fill text-success';
        else if (isActive) iconClass = 'ri-flashlight-fill text-primary animate-pulse'; // "animate-pulse" pour le côté "en cours"

        const dateEcheance = etape.date_echeance ? new Date(etape.date_echeance).toLocaleDateString() : '-';

        return `
                <div class="timeline-item pb-4 border-start ms-3 ps-4 position-relative">
                    <span class="position-absolute translate-middle start-0 bg-white px-1">
                        <i class="${iconClass} fs-4"></i>
                    </span>
                    <div class="timeline-header d-flex justify-content-between align-items-start mb-1">
                        <h6 class="mb-0 ${isActive ? 'fw-bold text-primary' : 'text-dark'}">
                            Étape ${etape.ordre} : ${etape.titre_etape || 'Validation'}
                        </h6>
                        <small class="text-muted font-monospace">
                            ${etape.date_traitement ? new Date(etape.date_traitement).toLocaleDateString() : ''}
                        </small>
                    </div>

                    <div class="d-flex flex-wrap align-items-center gap-3 mb-2">
                        <div class="small text-muted">
                            <i class="ri-user-3-line me-1"></i><strong>${etape.destinataire_name}</strong>
                        </div>
                        <div class="small text-muted">
                            <i class="ri-calendar-event-line me-1"></i>Échéance : ${dateEcheance}
                        </div>
                        ${this.getStatusBadge(etape.statut, etape.statut_display)}
                    </div>

                    ${
                      etape.commentaire
                        ? `
                        <div class="bg-light p-2 rounded border-start border-3 border-primary small italic text-secondary">
                            <i class="ri-chat-quote-line me-1"></i> "${etape.commentaire}"
                        </div>
                    `
                        : ''
                    }
                </div>
            `;
      })
      .join('');

    // Insertion du header et de la timeline
    container.html(headerHtml + `<div class="timeline-wrapper mt-2">${timelineHtml}</div>`);

    // Mise à jour du titre du modal (Optionnel si vous l'avez déjà dans le headerHtml)
    $('#modal-timeline-title').html(
      `<i class="ri-file-list-3-line me-2"></i> Document : ${circulation.document_titre}`
    );
  },

  /**
   * filtrer les utilisateurs en fonction de la cellule (sauf pour les admins)
   * @param {string|null} celluleId - ID de la cellule liée au document
   * @returns {void}
   */
  filterUserSelects(celluleId) {
    const userSelects = document.querySelectorAll('.user-select');
    const btnAdd = $('#btn-add-etape');

    // Vérification du rôle de l'utilisateur connecté
    const userRole = window.CURRENT_USER_ROLE;
    const isAdmin = userRole === 'administrateur' || userRole === 'superadmin';

    if (!celluleId) {
      btnAdd.addClass('disabled');
      userSelects.forEach(select => {
        $(select).html('<option value="">Veuillez d\'abord choisir un document valide</option>');
      });
      return;
    }

    btnAdd.removeClass('disabled');

    userSelects.forEach(select => {
      const currentValue = select.value;
      const options = select.querySelectorAll('option');

      options.forEach(opt => {
        if (opt.value === '') return;
        const userCellule = opt.getAttribute('data-cellule');
        const celluleNom = opt.getAttribute('data-cellule-nom') || 'Sans unité';

        // Sauvegarde du texte initial sans préfixe
        if (!$(opt).data('original-text')) {
          $(opt).data('original-text', opt.textContent.trim());
        }
        const originalText = $(opt).data('original-text');

        // 🟢 LOGIQUE TRANSVERSALE : Si Admin -> Accès complet, sinon -> Même cellule uniquement
        if (isAdmin || userCellule === String(celluleId)) {
          opt.style.display = 'block';
          opt.disabled = false;
          // Met en avant le nom de l'unité pour l'administrateur
          opt.textContent = `(${celluleNom}) - ${originalText}`;
        } else {
          opt.style.display = 'none';
          opt.disabled = true;
        }
      });

      // Reset si la sélection n'est plus autorisée
      const selectedOption = select.querySelector(`option[value="${currentValue}"]`);
      if (selectedOption && selectedOption.disabled) {
        select.value = '';
      }
    });
  },

  /**
   * Pour la gestion des étapes de circulation (ajout , supression dans le form)
   * @param {*} index
   * @param {*} activeCelluleId
   * @param {*} isLocked - Si true, désactive les champs pour rendre la ligne non éditable (ex: lors de l'affichage d'une circulation)
   * @returns {string} HTML de la ligne d'étape
   */
  renderEtapeRow(index, activeCelluleId = null, isLocked = false) {
    const sourceHtml = document.getElementById('user-source-list').innerHTML;
    const userRole = window.CURRENT_USER_ROLE;
    const isAdmin = userRole === 'administrateur' || userRole === 'superadmin';

    const tempSelect = document.createElement('select');
    tempSelect.innerHTML = sourceHtml;

    tempSelect.querySelectorAll('option').forEach(opt => {
      if (opt.value !== '') {
        const userCellule = opt.getAttribute('data-cellule');
        const celluleNom = opt.getAttribute('data-cellule-nom') || 'Sans unité';
        const originalText = opt.textContent.trim();

        // 🟢 LOGIQUE TRANSVERSALE AU RENDU : Si l'utilisateur n'est ni Admin ni de la cellule, on supprime l'option
        if (isAdmin || (activeCelluleId && String(userCellule) === String(activeCelluleId))) {
          opt.textContent = `(${celluleNom}) - ${originalText}`;
        } else {
          opt.remove();
        }
      }
    });

    const optionsFinales = tempSelect.innerHTML;
    const disabledAttr = isLocked ? 'disabled' : '';

    return `
    <div class="row etape-item mb-3 align-items-end" data-index="${index}">
      <input type="hidden" name="etapes[${index}][id]" class="etape-id">
      <div class="col-md-1 text-center fw-bold pb-2 mb-3">#${index + 1}</div>
      <div class="col-md-4 mb-3">
        <label class="form-label">Titre de l'étape</label>
        <input type="text" class="form-control" name="etapes[${index}][titre_etape]" placeholder="Ex: Validation Direction" required ${disabledAttr}>
      </div>
      <div class="col-md-4 mb-3">
        <label class="form-label">Destinataire</label>
        <select id="etape-user-select" class="form-select user-select" name="etapes[${index}][destinataire]" required ${disabledAttr}>
          ${optionsFinales}
        </select>
      </div>
      <div class="col-md-3 mb-3">
        <label class="form-label">Échéance</label>
        <input type="date" class="form-control" name="etapes[${index}][date_echeance]" required ${disabledAttr}>
      </div>
      <div class="col-md-12 text-end">
          <button type="button" title="supprimer l'étape" class="btn btn-label-danger btn-icon remove-etape" ${disabledAttr}>
              <i class="ri-delete-bin-line"></i>
          </button>
      </div>
    </div>`;
  },

  /**
   * Remplissage du formulaire pour édition
   * @param {Object} Circulation - Les données de la circulation à éditer. Si null, le formulaire est réinitialisé pour une nouvelle création.
   * @param {Object} docCelluleMap - Mapping des documents aux cellules pour le filtrage des destinataires dans les étapes
   */
  renderForm(circulation = null, docCelluleMap = {}) {
    const container = $('#etapes-container');
    container.empty();
    if (circulation) {
      $('#update-id').val(circulation.id);
      $('#doc-select').val(circulation.document).trigger('change');
      const $documentSelect = $('#doc-select');
      disableElement($documentSelect);
      $('#circuit-titre').val(circulation.titre);
      $('#circuit-desc').val(circulation.description);
      $('#date-fin').val(circulation.date_fin ? circulation.date_fin.split('T')[0] : '');
      const container = $('#etapes-container');
      container.empty();
      circulation.etapes.forEach((etape, index) => {
        const isLocked = etape.statut !== 'en_attente' && etape.statut !== 'en_cours';
        this.etapeIndex = index;
        const html = CirculationUi.renderEtapeRow(index, docCelluleMap[circulation.document], isLocked);
        container.append(html);
        const $row = container.find(`.etape-item[data-index="${index}"]`);
        $row.find('.etape-id').val(etape.id);
        $row.find('input[name*="[titre_etape]"]').val(etape.titre_etape);
        $row.find('select').val(etape.destinataire);
        if (etape.date_echeance) {
          $row.find('input[name*="[date_echeance]"]').val(etape.date_echeance.split('T')[0]);
        }
        if (isLocked) {
          $row.find('.remove-etape').hide();
        }
      });
      this.etapeIndex = circulation.etapes.length;
      $('#modal-title').text('Modifier le circuit de circulation');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#initierCircuitForm');
      $('#update-id').val('');
      this.etapeIndex = 0;
    }
  },

  /**
   * Rendu de la pagination
   * @param {*} data
   */
  renderPagination(data) {
    renderPagination(data, '#circulations-pagination', '#pagination-info');
  },

  /**
   * Affichage d'un message d'erreur
   * @param {*} message - Le texte du message d'erreur
   * @param {*} id - L'ID de l'élément HTML pour afficher le message (optionnel)
   * @param {*} loader - L'élément jQuery du loader à masquer (optionnel)
   * @returns {void}
   */
  showError(message, id = '#message-show-error', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  },

  /**
   * Affichage d'un message de succès
   * @param {*} message - Le texte du message de succès
   * @param {*} id - L'ID de l'élément HTML pour afficher le message (optionnel)
   * @param {*} loader - L'élément jQuery du loader à masquer (optionnel)
   * @returns {void}
   */
  showSuccess(message, id = '#message-show-success', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  }
};
