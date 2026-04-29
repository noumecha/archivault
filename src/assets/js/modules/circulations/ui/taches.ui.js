// modules/circulations/ui/taches.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';

export const TacheUi = {
  // Mapper des couleurs par priorité ou statut
  priorityColors: {
    basse: 'bg-info',
    normale: 'bg-primary',
    haute: 'bg-warning',
    urgente: 'bg-danger'
  },

  statusColors: {
    a_faire: 'bg-secondary',
    en_attente: 'bg-warning',
    'en cours': 'bg-primary',
    terminee: 'bg-success',
    cloturee: 'bg-success',
    annulee: 'bg-danger'
  },

  getPriorityBadge(tache) {
    const colorClass = this.priorityColors[tache.priorite] || 'bg-secondary';
    return `<span class="badge rounded-pill ${colorClass}">
              ${tache.priorite_display || tache.priorite}
            </span>`;
  },

  getStatusBadge(tache) {
    const colorClass = this.statusColors[tache.statut] || 'bg-secondary';
    return `<span class="badge rounded-pill ${colorClass}">
              ${tache.statut_display || tache.statut}
            </span>`;
  },

  // ─── Rendu de la table ───────────────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#taches-tbody');
    tbody.empty();

    const taches = response.results || response;

    if (!taches || taches.length === 0) {
      tbody.html('<tr><td colspan="8" class="text-center">Aucune tâche trouvée</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = taches.map(tache => this.createTacheRow(tache)).join('');
    tbody.html(rows);

    this.renderPagination(response);
    $('#check-all-taches').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  createTacheRow(tache) {
    const priorityBadge = this.getPriorityBadge(tache);
    const statusBadge = this.getStatusBadge(tache);
    const dateEcheance = tache.date_echeance ? new Date(tache.date_echeance).toLocaleDateString() : '-';
    const p = tache.tache_actions;

    return `
      <tr data-tache-id="${tache.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input tache-checkbox" type="checkbox" value="${tache.id}">
          </div>
        </th>
        <td>${tache.document_titre || '-'}</td>
        <td>${tache.titre}</td>
        <td>${tache.assignee_a_name || '-'}</td>
        <td>${tache.assignee_par_name || '-'}</td>
        <td>${priorityBadge}</td>
        <td>${dateEcheance}</td>
        <td>${statusBadge}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              ${
                p.can_view
                  ? `<a href="#" class="dropdown-item" data-action="view" data-id="${tache.id}">
                <i class="ri-eye-line me-1"></i>Détails
              </a>`
                  : ''
              }
              ${
                p.can_edit
                  ? `<a href="#" class="dropdown-item" data-action="edit" data-id="${tache.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>`
                  : ''
              }
              ${
                p.can_delete
                  ? `<a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${tache.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>`
                  : ''
              }
            </div>
          </div>
        </td>
      </tr>`;
  },

  renderPagination(data) {
    renderPagination(data, '#taches-pagination', '#pagination-info');
  },

  renderForm(tache = null) {
    if (tache) {
      $('#update-id').val(tache.id);
      $('#titre').val(tache.titre);
      $('#description').val(tache.description);
      $('#document').val(tache.document).trigger('change');
      $('#assignee_a').val(tache.assignee_a).trigger('change');
      $('#priorite').val(tache.priorite);
      $('#statut').val(tache.statut);
      $('#date_echeance').val(tache.date_echeance ? tache.date_echeance.split('T')[0] : '');
      $('#modal-title').text('Modifier la tâche');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#tacheForm');
      $('#update-id').val('');
      $('#modal-title').text('Nouvelle tâche');
      $('#save-btn-text').text('Enregistrer');
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
  }
};
