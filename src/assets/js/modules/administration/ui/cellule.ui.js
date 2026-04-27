// modules/adminstration/ui/cellules.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';
export const CelluleUi = {
  // ─── Rendu de la table ───────────────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#cellules-tbody');
    tbody.empty();

    // DRF renvoie { count, next, previous, results: [] } avec la pagination
    const cellules = response.results || response;

    if (!cellules || cellules.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucune unité de traitement trouvée</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = cellules.map(cellule => this.createcelluleRow(cellule)).join('');
    tbody.html(rows);

    // Gérer la pagination
    this.renderPagination(response);
    // Réinitialiser la checkbox globale
    $('#check-all-cellules').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  // Rendu d'une ligne unité de traitement
  createcelluleRow(cellule) {
    const statusBailleurBadge = cellule.accepte_bailleurs
      ? '<span class="badge rounded-pill bg-success">Activé</span>'
      : '<span class="badge rounded-pill bg-danger">Désactivé</span>';
    return `
      <tr data-cellule-id="${cellule.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input cellule-checkbox" type="checkbox" value="${cellule.id}">
          </div>
        </th>
        <td>${cellule.nom}</td>
        <td>${cellule.description_cellule || '-'}</td>
        <td>${cellule.division_display || '-'}</td>
        <td>${statusBailleurBadge}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="edit" data-id="${cellule.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${cellule.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>
              <a href="#" class="dropdown-item" data-action="toggle-acceptebailleurs" data-id="${cellule.id}">
                <i class="ri-check-double-line me-1"></i>
                ${cellule.accepte_bailleurs === true ? 'Désactiver (accepte bailleurs)' : 'Activer (accepte bailleurs)'}
              </a>
            </div>
          </div>
        </td>
      </tr>
    `;
  },

  // Rendu de la pagination
  renderPagination(data) {
    renderPagination(data, '#cellules-pagination', '#pagination-info');
  },

  // ─── Remplissage du formulaire ───────────────────────────────────────────
  renderForm(cellule = null) {
    if (cellule) {
      $('#update-id').val(cellule.id);
      $('#nom').val(cellule.nom);
      $('#description_cellule').val(cellule.description_cellule);
      $('#division').val(cellule.division);
      $('#accepte_bailleurs').prop('checked', cellule.accepte_bailleurs);
      $('#modal-title').text('Modifier une unité de traitement');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      //$('#celluleForm').reset();
      resetForm('#celluleForm');
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
