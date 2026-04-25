// modules/users/users.ui.js
import { showAlertMessage, resetForm } from '../../helpers/utils.js';
export const UserUi = {
  // Mapper des couleurs par rôle
  roleColors: {
    superadmin: 'bg-danger', // Rouge pour le niveau critique
    administrateur: 'bg-primary', // Bleu standard pour l'admin
    superviseur: 'bg-warning', // Orange/Jaune pour le superviseur
    gestionnaire: 'bg-info', // Bleu clair pour le gestionnaire
    responsable: 'bg-secondary' // Gris pour le responsable
  },

  // Helper pour générer le badge de rôle
  getRoleBadge(user) {
    // On récupère la couleur, sinon 'bg-secondary' par défaut
    const colorClass = this.roleColors[user.role] || 'bg-secondary';

    return `<span class="badge rounded-pill ${colorClass}">
              ${user.role_display}
            </span>`;
  },

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

  // Rendu d'une ligne utilisateur
  createUserRow(user) {
    const statusBadge = user.is_active
      ? '<span class="badge rounded-pill bg-success">Activé</span>'
      : '<span class="badge rounded-pill bg-danger">Désactivé</span>';
    const roleBadge = this.getRoleBadge(user);
    return `
      <tr data-user-id="${user.id}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input user-checkbox" type="checkbox" value="${user.id}">
          </div>
        </th>
        <td>
          <img src="${user.avatar_url || '/static/img/avatars/1.png'}" alt="${user.username}" class="w-px-40 h-auto rounded-circle">
        </td>
        <td>${user.username}</td>
        <td>${user.first_name || '-'}</td>
        <td>${roleBadge}</td>
        <td>${user.email || '-'}</td>
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
  },

  // Rendu de la pagination
  renderPagination(data) {
    const $container = $('#users-pagination');
    const $info = $('#pagination-info');
    $container.empty();
    $info.empty();

    if (!data.count || data.count === 0) return;

    const pageSize = data.page_size || 10;
    const totalPages = Math.ceil(data.count / pageSize);
    const currentPage = data.current_page || 1;

    const startEntry = (currentPage - 1) * pageSize + 1;
    const endEntry = Math.min(currentPage * pageSize, data.count);
    $info.text(`Affichage de ${startEntry} à ${endEntry} sur ${data.count} éléments`);

    if (totalPages <= 1) return;

    let html = '';

    html += `
        <li class="page-item ${!data.previous ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}"><i class="ri-arrow-left-s-line"></i></a>
        </li>`;

    const delta = 1;
    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
        html += `
                <li class="page-item ${currentPage === i ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>`;
      } else if (i === currentPage - delta - 1 || i === currentPage + delta + 1) {
        html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
      }
    }

    html += `
        <li class="page-item ${!data.next ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}"><i class="ri-arrow-right-s-line"></i></a>
        </li>`;

    $container.html(html);
  },

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

  showError(message, id = '#message-show', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  },

  showSuccess(message, id = '#message-show', loader = $('#form-loader')) {
    showAlertMessage(message, id, loader);
  }
};
