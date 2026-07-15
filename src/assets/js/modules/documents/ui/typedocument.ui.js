// modules/documents/ui/typedocument.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';

export const TypeDocumentUi = {
  renderTable(response) {
    const tbody = $('#typedocuments-tbody');
    tbody.empty();
    const types = response.results || response;

    if (!types || types.length === 0) {
      tbody.html('<tr><td colspan="6" class="text-center">Aucun type trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = types.map(type => this.createTypeRow(type)).join('');
    tbody.html(rows);
    this.renderPagination(response);
    $('#check-all-types').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  createTypeRow(type) {
    // 🟢 Distinction visuelle : Cellule vs Générique
    const celluleBadge = type.cellule_info?.nom
      ? `<span class="badge bg-label-secondary">${type.cellule_info.nom}</span>`
      : `<span class="badge bg-label-info"><i class="ri-global-line me-1"></i>Générique</span>`;
    return `
      <tr data-type-id="${type.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input type-checkbox" type="checkbox" value="${type.id}">
          </div>
        </th>
        <td><span class="fw-medium">${type.libelle}</span></td>
        <td>${type.description_typedocument || '-'}</td>
        <td>${type.parent_type_display || '<span class="badge rounded-pill bg-label-primary">Principal</span>'}</td>
        <td>${celluleBadge}</td>
        <td>${type.cellule_info?.nom || '-'}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ri-more-2-line"></i></button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="edit" data-id="${type.id}"><i class="ri-pencil-line me-1"></i>Modifier</a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${type.id}"><i class="ri-delete-bin-line me-1"></i>Supprimer</a>
            </div>
          </div>
        </td>
      </tr>`;
  },

  renderPagination(data) {
    renderPagination(data, '#typedocuments-pagination', '#pagination-info');
  },

  renderForm(type = null) {
    if (type) {
      $('#update-id').val(type.id);
      $('#libelle').val(type.libelle);
      $('#description_typedocument').val(type.description_typedocument || '');
      // 🟢 Récupération correcte de l'ID de la cellule (ou "" si null / générique)
      const celluleVal =
        typeof type.cellule === 'object' && type.cellule !== null ? type.cellule.id : type.cellule || '';

      const parentTypeVal =
        typeof type.parent_type === 'object' && type.parent_type !== null
          ? type.parent_type.id
          : type.parent_type || '';

      $('#cellule').val(celluleVal).trigger('change');
      $('#parent_type').val(parentTypeVal).trigger('change');
      $('#modal-title').text('Modifier le type');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#typedocumentForm');
      $('#update-id').val('');
      $('#save-btn-text').text('Enregistrer');
    }
  },

  showError(msg, id = '#message-show-error') {
    showAlertMessage(msg, id, $('#form-loader'));
  },
  showSuccess(msg, id = '#message-show-success') {
    showAlertMessage(msg, id, $('#form-loader'));
  }
};
