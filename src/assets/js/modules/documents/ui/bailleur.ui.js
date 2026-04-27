// modules/documents/ui/bailleur.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';

export const BailleurUi = {
  renderTable(response) {
    const tbody = $('#bailleurs-tbody');
    tbody.empty();
    const items = response.results || response;

    if (!items || items.length === 0) {
      tbody.html('<tr><td colspan="6" class="text-center">Aucun bailleur trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = items.map(item => this.createRow(item)).join('');
    tbody.html(rows);
    this.renderPagination(response);
    $('#check-all-bailleurs').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  createRow(item) {
    return `
      <tr data-id="${item.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input item-checkbox" type="checkbox" value="${item.id}">
          </div>
        </th>
        <td><span class="fw-medium">${item.abrevation}</span></td>
        <td>${item.libelle}</td>
        <td>${item.description || '-'}</td>
        <td>${item.cellule_display || '-'}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ri-more-2-line"></i></button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="edit" data-id="${item.id}"><i class="ri-pencil-line me-1"></i>Modifier</a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${item.id}"><i class="ri-delete-bin-line me-1"></i>Supprimer</a>
            </div>
          </div>
        </td>
      </tr>`;
  },

  renderPagination(data) {
    renderPagination(data, '#bailleurs-pagination', '#pagination-info');
  },

  renderForm(item = null) {
    if (item) {
      $('#update-id').val(item.id);
      $('#libelle').val(item.libelle);
      $('#abrevation').val(item.abrevation);
      $('#description').val(item.description || '');
      $('#cellule').val(item.cellule || '');
      $('#modal-title').text('Modifier le bailleur');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#bailleurForm');
      $('#update-id').val('');
      $('#save-btn-text').text('Enregistrer');
      $('#modal-title').text('Enregistrer un bailleur');
    }
  },

  showError(msg, id = '#message-show-error') {
    showAlertMessage(msg, id, $('#form-loader'));
  },
  showSuccess(msg, id = '#message-show-success') {
    showAlertMessage(msg, id, $('#form-loader'));
  }
};
