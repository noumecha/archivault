import { showAlertMessage, resetForm, renderPagination } from '../../helpers/utils.js';

export const CirculationUi = {
  // Configuration des statuts pour les badges
  statusColors: {
    en_attente: 'bg-secondary',
    en_cours: 'bg-primary',
    valide: 'bg-success',
    rejete: 'bg-danger',
    retourne: 'bg-warning',
    clos: 'bg-info'
  },

  getStatusBadge(statut, display) {
    const colorClass = this.statusColors[statut] || 'bg-secondary';
    return `<span class="badge rounded-pill ${colorClass}">${display || statut}</span>`;
  },

  // ─── Rendu de la table principale ────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#circulations-tbody');
    tbody.empty();

    const circulations = response.results || response;

    if (!circulations || circulations.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucun circuit de circulation trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = circulations.map(circ => this.createCirculationRow(circ)).join('');
    tbody.html(rows);

    this.renderPagination(response);
  },

  createCirculationRow(circ) {
    const statusBadge = this.getStatusBadge(circ.statut, circ.statut_display);
    const dateDebut = new Date(circ.date_debut).toLocaleDateString();

    // Calcul de la progression (ex: 2/5 étapes)
    const totalEtapes = circ.etapes_count || 0;
    const etapeActuelleOrdre = circ.etape_actuelle ? circ.etape_actuelle.ordre : totalEtapes;

    return `
      <tr data-id="${circ.id}">
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
              <a href="#" class="dropdown-item" data-ordre="${circ.etape_actuelle?.ordre}" data-action="process" data-id="${circ.id}">
                <i class="ri-checkbox-circle-line me-1"></i>Traiter l'étape
              </a>
              <div class="dropdown-divider"></div>
              <a href="#" class="dropdown-item text-danger" data-action="delete-circulation" data-id="${circ.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>
            </div>
          </div>
        </td>
      </tr>`;
  },

  // ─── Rendu de la Timeline (Le besoin du "Grand Boss") ──────────────────────
  renderTimeline(circulation) {
    const container = $('#timeline-container');
    container.empty();

    if (!circulation.etapes || circulation.etapes.length === 0) {
      container.html('<p class="text-center">Aucune étape définie</p>');
      return;
    }

    const timelineHtml = circulation.etapes
      .map((etape, index) => {
        const isCompleted = ['valide', 'rejete', 'retourne'].includes(etape.statut);
        const isActive = etape.est_actuelle;
        const icon = isCompleted
          ? 'ri-checkbox-circle-fill text-success'
          : isActive
            ? 'ri-time-line text-primary'
            : 'ri-checkbox-blank-circle-line text-muted';

        return `
            <div class="timeline-item pb-4 border-start ms-3 ps-4 position-relative">
                <span class="position-absolute translate-middle start-0 bg-white">
                    <i class="${icon} fs-4"></i>
                </span>
                <div class="timeline-header d-flex justify-content-between">
                    <h6 class="mb-0 ${isActive ? 'fw-bold text-primary' : ''}">Étape ${etape.ordre}: ${etape.destinataire_name}</h6>
                    <small class="text-muted">${etape.date_traitement ? new Date(etape.date_traitement).toLocaleString() : ''}</small>
                </div>
                <p class="mb-1">${this.getStatusBadge(etape.statut, etape.statut_display)}</p>
                ${etape.commentaire ? `<div class="alert alert-light p-2 mb-0 small">"${etape.commentaire}"</div>` : ''}
            </div>
        `;
      })
      .join('');

    container.html(timelineHtml);
    $('#modal-timeline-title').text(`Suivi : ${circulation.document_titre}`);
  },

  // Nouvelle méthode pour filtrer les utilisateurs selon une cellule
  filterUserSelects(celluleId) {
    const userSelects = document.querySelectorAll('.user-select');
    const btnAdd = $('#btn-add-etape');

    // Problème 3 : Si pas de document ou document sans cellule
    if (!celluleId) {
      btnAdd.addClass('disabled'); // Empêcher l'ajout d'étapes
      userSelects.forEach(select => {
        $(select).html('<option value="">Veuillez d\'abord choisir un document valide</option>');
      });
      return;
    }

    btnAdd.removeClass('disabled');

    // Filtrer les selects existants
    userSelects.forEach(select => {
      const currentValue = select.value;
      const options = select.querySelectorAll('option');

      options.forEach(opt => {
        if (opt.value === '') return;
        const userCellule = opt.getAttribute('data-cellule');

        if (userCellule === celluleId) {
          opt.style.display = 'block';
          opt.disabled = false;
        } else {
          opt.style.display = 'none';
          opt.disabled = true;
        }
      });

      // Reset si la sélection n'est plus valide
      const selectedOption = select.querySelector(`option[value="${currentValue}"]`);
      if (selectedOption && selectedOption.disabled) {
        select.value = '';
      }
    });
  },

  renderEtapeRow(index, activeCelluleId = null) {
    const sourceHtml = document.getElementById('user-source-list').innerHTML;

    // On crée un élément temporaire pour filtrer les options avant injection
    const tempSelect = document.createElement('select');
    tempSelect.innerHTML = sourceHtml;

    // Si on a une cellule, on filtre. Si on n'en a pas, on vide tout sauf le placeholder.
    tempSelect.querySelectorAll('option').forEach(opt => {
      if (opt.value !== '') {
        if (!activeCelluleId || opt.getAttribute('data-cellule') !== activeCelluleId) {
          opt.remove();
        }
      }
    });

    /*if (activeCelluleId) {
      tempSelect.querySelectorAll('option').forEach(opt => {
        if (opt.value !== '' && opt.getAttribute('data-cellule') !== activeCelluleId) {
          opt.remove(); // On ne garde que les users de la bonne cellule pour cette nouvelle ligne
        }
      });
    }*/
    const optionsFinales = tempSelect.innerHTML;

    return `
      <div class="row etape-item mb-3 align-items-end" data-index="${index}">
        <div class="col-md-1 text-center fw-bold pb-2">#${index + 1}</div>
        <div class="col-md-9">
          <label class="form-label">Destinataire (Cellule : ${activeCelluleId || 'Aucune'})</label>
          <select class="form-select user-select" name="etapes[${index}][destinataire]" required>
            ${optionsFinales}
          </select>
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-label-danger btn-icon remove-etape">
                <i class="ri-delete-bin-line"></i>
            </button>
        </div>
      </div>`;
    /**
       * <div class="row etape-item mb-3 align-items-end" data-index="${index}">
        <div class="col-md-1 text-center fw-bold pt-2">${index + 1}</div>
        <div class="col-md-7">
          <label class="form-label text-xs">Destinataire</label>
          <select class="form-select user-select" name="etapes[${index}][destinataire]" required>
            ${optionsFinales}
          </select>
        </div>
        <div class="col-md-3">
            <button type="button" class="btn btn-outline-danger btn-sm remove-etape">
                <i class="ri-delete-bin-line"></i>
            </button>
        </div>
      </div>
       */
  },

  // ─── Utilitaires standards ──────────────────────────────────────────────
  renderPagination(data) {
    renderPagination(data, '#circulations-pagination', '#pagination-info');
  },

  showError(message, id = '#message-show-error', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  },

  showSuccess(message, id = '#message-show-success', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  }
};
