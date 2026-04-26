// modules/administration/ui/ministere.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';
export const MinistereUi = {
  // ─── Rendu de la table ───────────────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#ministeres-tbody');
    tbody.empty();

    // DRF renvoie { count, next, previous, results: [] } avec la pagination
    const ministeres = response.results || response;

    if (!ministeres || ministeres.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucun ministere trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = ministeres.map(ministere => this.createministereRow(ministere)).join('');
    tbody.html(rows);

    // Gérer la pagination
    this.renderPagination(response);
    // Réinitialiser la checkbox globale
    $('#check-all-ministeres').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  // Rendu d'une ligne ministere
  createministereRow(ministere) {
    return `
      <tr data-ministere-id="${ministere.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input ministere-checkbox" type="checkbox" value="${ministere.id}">
          </div>
        </th>
        <td>${ministere.nom}</td>
        <td>${ministere.code || '-'}</td>
        <td>${ministere.abrevation || '-'}</td>
        <td>${ministere.description_ministere || '-'}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown" disabled>
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" disabled class="dropdown-item" data-action="edit" data-id="${ministere.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>
              <a href="#" disabled class="dropdown-item text-danger" data-action="delete" data-id="${ministere.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>
            </div>
          </div>
        </td>
      </tr>
    `;
  },

  // Rendu de la pagination
  renderPagination(data) {
    renderPagination(data, '#ministeres-pagination', '#pagination-info');
  },

  // ─── Remplissage du formulaire ───────────────────────────────────────────
  renderForm(ministere = null) {
    if (ministere) {
      $('#update-id').val(ministere.id);
      $('#nom').val(ministere.nom);
      $('#description').val(ministere.description);
      $('#code').val(ministere.code);
      $('#abrevation').val(ministere.abrevation);
      $('#modal-title').text('Modifier un ministere');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      //$('#ministereForm').reset();
      resetForm('#ministereForm');
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
