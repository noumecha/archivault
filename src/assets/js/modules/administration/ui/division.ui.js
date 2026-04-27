// modules/administration/ui/divisions.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';
export const DivisionUi = {
  // ─── Rendu de la table ───────────────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#divisions-tbody');
    tbody.empty();

    // DRF renvoie { count, next, previous, results: [] } avec la pagination
    const divisions = response.results || response;

    if (!divisions || divisions.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucune division trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = divisions.map(division => this.createDivisionRow(division)).join('');
    tbody.html(rows);

    // Gérer la pagination
    this.renderPagination(response);
    // Réinitialiser la checkbox globale
    $('#check-all-divisions').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  // Rendu d'une ligne division
  createDivisionRow(division) {
    const statusBadge = division.statut
      ? '<span class="badge rounded-pill bg-success">Activé</span>'
      : '<span class="badge rounded-pill bg-danger">Désactivé</span>';
    return `
      <tr data-division-id="${division.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input division-checkbox" type="checkbox" value="${division.id}">
          </div>
        </th>
        <td>${division.nom}</td>
        <td>${division.description_division || '-'}</td>
        <td>${statusBadge}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="edit" data-id="${division.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${division.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>
              <a href="#" class="dropdown-item" data-action="toggle-status" data-id="${division.id}">
                <i class="ri-check-double-line me-1"></i>
                ${division.statut === true ? 'Désactiver' : 'Activer'}
              </a>
            </div>
          </div>
        </td>
      </tr>
    `;
  },

  // Rendu de la pagination
  renderPagination(data) {
    renderPagination(data, '#divisions-pagination', '#pagination-info');
  },

  // ─── Remplissage du formulaire ───────────────────────────────────────────
  renderForm(division = null) {
    if (division) {
      $('#update-id').val(division.id);
      $('#nom').val(division.nom);
      $('#ministere').val(division.ministere);
      $('#direction_generale').val(division.direction_generale);
      $('#description_division').val(division.description_division);
      $('#statut').prop('checked', division.statut);
      $('#modal-title').text('Modifier une division');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#divisionForm');
      $('#update-id').val('');
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
