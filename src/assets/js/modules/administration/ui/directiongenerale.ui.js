// modules/administration/ui/directiongenerale.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';
export const DirectionGeneraleUi = {
  // ─── Rendu de la table ───────────────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#directiongenerales-tbody');
    tbody.empty();

    // DRF renvoie { count, next, previous, results: [] } avec la pagination
    const directiongenerales = response.results || response;

    if (!directiongenerales || directiongenerales.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucun direction générale trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = directiongenerales
      .map(directiongenerale => this.createdirectiongeneraleRow(directiongenerale))
      .join('');
    tbody.html(rows);

    // Gérer la pagination
    this.renderPagination(response);
    // Réinitialiser la checkbox globale
    $('#check-all-directiongenerales').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  // Rendu d'une ligne direction générale
  createdirectiongeneraleRow(directiongenerale) {
    return `
      <tr data-directiongenerale-id="${directiongenerale.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input directiongenerale-checkbox" type="checkbox" value="${directiongenerale.id}">
          </div>
        </th>
        <td>${directiongenerale.nom}</td>
        <td>${directiongenerale.description_direction_generale}</td>
        <td>${directiongenerale.ministere_display}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="edit" data-id="${directiongenerale.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${directiongenerale.id}">
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
    renderPagination(data, '#directiongenerales-pagination', '#pagination-info');
  },

  // ─── Remplissage du formulaire ───────────────────────────────────────────
  renderForm(directiongenerale = null) {
    if (directiongenerale) {
      $('#update-id').val(directiongenerale.id);
      $('#nom').val(directiongenerale.nom);
      $('#description_direction_generale').val(directiongenerale.description_direction_generale);
      $('#ministere').val(directiongenerale.ministere);
      $('#modal-title').text('Modifier une direction générale');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#directiongeneraleForm');
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
