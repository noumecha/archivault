// modules/users/users.ui.js
import { showAlertMessage, resetForm } from '../../helpers/utils.js';
export const UserUi = {
  // ─── Rendu de la table ───────────────────────────────────────────────────

  renderTable(response) {
    const tbody = $('#users-tbody');
    tbody.empty();

    // DRF renvoie { count, next, previous, results: [] } avec la pagination
    const users = response.results || response;

    if (!users || users.length === 0) {
      tbody.html('<tr><td colspan="7" class="text-center">Aucun utilisateur trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = users.map(user => this.createUserRow(user)).join('');
    tbody.html(rows);

    // Gérer la pagination
    this.renderPagination(response);
    // Réinitialiser la checkbox globale
    $('#check-all-users').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  createUserRow(user) {
    const statusBadge = user.is_active
      ? '<span class="badge rounded-pill bg-success">Activé</span>'
      : '<span class="badge rounded-pill bg-danger">Désactivé</span>';

    return `
      <tr data-user-id="${user.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input user-checkbox" type="checkbox" value="${user.id}">
          </div>
        </th>
        <td>${user.username}</td>
        <td>${user.first_name || '-'}</td>
        <td><span class="badge rounded-pill bg-primary">${user.role_display}</span></td>
        <td>${user.email}</td>
        <td>${statusBadge}</td>
        <td>
            ...
        </td>
      </tr>
    `;
  },

  renderPagination(data) {
    const container = $('#users-pagination');
    container.empty();

    if (!data.count || data.count <= 20) return; // CustomPagination.page_size = 20

    const totalPages = Math.ceil(data.count / 20);
    // Logique simplifiée : Précédent | Pages | Suivant
    let html = `
      <li class="page-item ${!data.previous ? 'disabled' : ''}">
        <a class="page-link" href="#" data-page-url="${data.previous}">Précédent</a>
      </li>
    `;

    for (let i = 1; i <= totalPages; i++) {
      // Note: Ici il faudrait une logique pour marquer la page "active"
      html += `<li class="page-item"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
    }

    html += `
      <li class="page-item ${!data.next ? 'disabled' : ''}">
        <a class="page-link" href="#" data-page-url="${data.next}">Suivant</a>
      </li>
    `;
    container.html(html);
  },

  /*renderTable(datas) {
    const tbody = $('#users-tbody');
    tbody.empty();
    let users = datas.results || datas; // Supporte à la fois les réponses paginées et non paginées
    if (!users.length) {
      tbody.html(`
        <tr>
          <td colspan="6" class="text-center">Aucun utilisateur trouvé</td>
        </tr>
      `);
      return;
    }

    // Pour chaque utilisateur, crée une ligne HTML
    const rows = users.map(user => this.createUserRow(user)).join('');
    tbody.html(rows);
  },

  // ─── Création d'une ligne utilisateur ────────────────────────────────────
  createUserRow(user) {
    const statusBadge =
      user.is_active === true
        ? '<span class="badge rounded-pill bg-success">Activé</span>'
        : '<span class="badge rounded-pill bg-danger">Désactivé</span>';

    return `
      <tr data-user-id="${user.id}">
        <td>${user.username}</td>
        <td>${user.first_name || '-'}</td>
        <td><span class="badge rounded-pill bg-primary">${user.role_display}</span></td>
        <td>${user.email}</td>
        <td>${statusBadge}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              <a href="#" class="dropdown-item" data-action="edit" data-id="${user.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${user.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>
              <a href="#" class="dropdown-item" data-action="toggle-status" data-id="${user.id}">
                <i class="ri-check-double-line me-1"></i>
                ${user.is_active === true ? 'Désactiver' : 'Activer'}
              </a>
            </div>
          </div>
        </td>
      </tr>
    `;
  },*/

  // ─── Remplissage du formulaire ───────────────────────────────────────────
  renderForm(user = null) {
    if (user) {
      $('#update-id').val(user.id);
      $('#username').val(user.username);
      $('#first_name').val(user.first_name);
      $('#email').val(user.email);
      $('#cellule').val(user.cellule);
      $('#role').val(user.role);
      $('#is_active').prop('checked', user.is_active);
      $('#modal-title').text('Modifier un utilisateur');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      //$('#utilisateurForm').reset();
      resetForm('#utilisateurForm');
      $('#update-id').val('');
      $('#save-btn-text').text('Enregistrer');
    }
  },

  resetForm(formSelector) {
    $(formSelector)[0].reset();
  },

  showMessage(message, selector) {
    const $msg = $(selector);
    $msg.text(message).fadeIn().delay(3000).fadeOut();
  },

  showError(message, id = '#message-show', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  },

  showSuccess(message, id = '#message-show', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  }
};
