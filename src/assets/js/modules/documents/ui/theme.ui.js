// modules/documents/ui/themes.ui.js
import { showAlertMessage, resetForm, renderPagination } from '../../../helpers/utils.js';
export const ThemeUi = {
  // ─── Rendu de la table ───────────────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#themes-tbody');
    tbody.empty();
    const themes = response.results || response;

    if (!themes || themes.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucun thème trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = themes.map(theme => this.createThemeRow(theme)).join('');
    tbody.html(rows);

    // Gérer la pagination
    this.renderPagination(response);
    // Réinitialiser la checkbox globale
    $('#check-all-themes').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  // Rendu d'une ligne thème
  createThemeRow(theme) {
    // 🟢 Badge visuel pour différencier Générique vs Unité spécifique
    const celluleBadge = theme.cellule_info?.nom
      ? `<span class="badge bg-label-secondary">${theme.cellule_info.nom}</span>`
      : `<span class="badge bg-label-info"><i class="ri-global-line me-1"></i>Générique</span>`;
    return `
      <tr data-theme-id="${theme.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input theme-checkbox" type="checkbox" value="${theme.id}">
          </div>
        </th>
        <td>${theme.libelle}</td>
        <td>${theme.description_theme || '-'}</td>
        <td>${theme.cellule_info?.nom || '-'}</td>
        <td>${celluleBadge}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="edit" data-id="${theme.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${theme.id}">
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
    renderPagination(data, '#themes-pagination', '#pagination-info');
  },

  // ─── Remplissage du formulaire ───────────────────────────────────────────
  renderForm(theme = null) {
    if (theme) {
      $('#update-id').val(theme.id);
      $('#libelle').val(theme.libelle);
      $('#description_theme').val(theme.description_theme || '');
      // 🟢 Extraction robuste de la valeur cellule
      const celluleVal =
        typeof theme.cellule === 'object' && theme.cellule !== null ? theme.cellule.id : theme.cellule || '';

      $('#cellule').val(celluleVal).trigger('change');
      $('#modal-title').text('Modifier un thème');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#themeForm');
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
