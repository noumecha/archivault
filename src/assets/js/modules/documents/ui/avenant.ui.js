import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';

export const AvenantUi = {
  renderTable(response) {
    const tbody = $('#avenants-tbody');
    tbody.empty();
    const items = response.results || response;
    if (!items || items.length === 0) {
      tbody.html('<tr><td colspan="5" class="text-center">Aucun avenant trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }
    tbody.html(items.map(item => this.createRow(item)).join(''));
    this.renderPagination(response);
    $('#check-all-avenants').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },
  createRow(item) {
    return `
      <tr data-id="${item.id}">
        <th><div class="form-check"><input class="form-check-input item-checkbox" type="checkbox" value="${item.id}"></div></th>
        <td><span class="fw-medium">${item.libelle}</span></td>
        <td>${item.numero}</td>
        <td>${item.bailleur_display}</td>
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
    renderPagination(data, '#avenants-pagination', '#pagination-info');
  },
  renderForm(item = null) {
    if (item) {
      $('#update-id').val(item.id);
      $('#libelle').val(item.libelle);
      $('#numero').val(item.numero);
      $('#bailleur').val(item.bailleur);
      $('#modal-title').text("Modifier l'avenant");
    } else {
      resetForm('#avenantForm');
      $('#update-id').val('');
      $('#modal-title').text('Enregistrer un avenant');
    }
  },
  showError(msg, id = '#message-show-error') {
    showAlertMessage(msg, id, $('#form-loader'));
  },
  showSuccess(msg, id = '#message-show-success') {
    showAlertMessage(msg, id, $('#form-loader'));
  }
};
