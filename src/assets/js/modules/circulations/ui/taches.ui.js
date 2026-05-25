// modules/circulations/ui/taches.ui.js
import {
  showAlertMessage,
  resetForm,
  renderPagination,
  disableElement,
  enableElement
} from '../../../helpers/utils.js';

export const TacheUi = {
  // Mapper des couleurs par priorité ou statut
  priorityColors: {
    basse: 'bg-info',
    normale: 'bg-primary',
    haute: 'bg-warning',
    urgente: 'bg-danger'
  },

  statusColors: {
    a_faire: 'bg-secondary',
    en_attente: 'bg-warning',
    'en cours': 'bg-primary',
    terminee: 'bg-success',
    cloturee: 'bg-success',
    annulee: 'bg-danger'
  },

  /**
   * Génération du badge de consultation
   * @param {*} tache
   * @returns
   */
  getConsultationBadge(tache) {
    if (!tache.date_premiere_consultation) {
      return `<span class="badge bg-label-danger d-flex align-items-center gap-1 w-100 justify-content-center">
                <i class="ri-eye-off-line"></i> Non consulté
              </span>`;
    }

    const dateLettre = new Date(tache.date_premiere_consultation).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });

    return `<span class="badge bg-label-success d-flex align-items-center gap-1 w-100 justify-content-center" data-bs-toggle="tooltip" title="Consulté ${tache.nb_consultations || 1} fois">
              <i class="ri-eye-line"></i> Vu le ${dateLettre}
            </span>`;
  },

  getPriorityBadge(tache) {
    const colorClass = this.priorityColors[tache.priorite] || 'bg-secondary';
    return `<span class="badge rounded-pill ${colorClass}">
              ${tache.priorite_display || tache.priorite}
            </span>`;
  },

  getStatusBadge(tache) {
    const colorClass = this.statusColors[tache.statut] || 'bg-secondary';
    return `<span class="badge rounded-pill ${colorClass}">
              ${tache.statut_display || tache.statut}
            </span>`;
  },

  // ─── Rendu de la table ───────────────────────────────────────────────────
  renderTable(response) {
    const tbody = $('#taches-tbody');
    tbody.empty();

    const taches = response.results || response;

    if (!taches || taches.length === 0) {
      tbody.html('<tr><td colspan="8" class="text-center">Aucune tâche trouvée</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = taches.map(tache => this.createTacheRow(tache)).join('');
    tbody.html(rows);

    this.renderPagination(response);
    $('#check-all-taches').prop('checked', false);
    $('#bulk-actions-container').addClass('d-none');
  },

  createTacheRow(tache) {
    const priorityBadge = this.getPriorityBadge(tache);
    const consultationBadge = this.getConsultationBadge(tache);
    const statusBadge = this.getStatusBadge(tache);
    const dateEcheance = tache.date_echeance ? new Date(tache.date_echeance).toLocaleDateString() : '-';
    const p = tache.tache_actions;

    return `
      <tr data-tache-id="${tache.id}" data-assignee-id="${tache.assignee_a || ''}">
        <th style="width: 40px;">
          <div class="form-check mb-0">
            <input class="form-check-input tache-checkbox" type="checkbox" value="${tache.id}">
          </div>
        </th>
        <td>${tache.document_titre || '-'}</td>
        <td>${tache.titre}</td>
        <td>${tache.assignee_a_name || '-'}</td>
        <td>${tache.assignee_par_name || '-'}</td>
        <td>${priorityBadge}</td>
        <td>${dateEcheance}</td>
        <td>${statusBadge}</td>
        <td>${consultationBadge}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
              <i class="ri-more-2-line"></i>
            </button>
            <div class="dropdown-menu">
              ${
                p.can_view
                  ? `<a href="#" class="dropdown-item" data-action="view" data-id="${tache.id}">
                <i class="ri-eye-line me-1"></i>Détails
              </a>`
                  : ''
              }
              ${
                p.can_edit
                  ? `<a href="#" class="dropdown-item" data-action="edit" data-id="${tache.id}">
                <i class="ri-pencil-line me-1"></i>Modifier
              </a>`
                  : ''
              }
              ${
                p.can_delete
                  ? `<a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${tache.id}">
                <i class="ri-delete-bin-6-line me-1"></i>Supprimer
              </a>`
                  : ''
              }
            </div>
          </div>
        </td>
      </tr>`;
  },

  /**
   * Filtrage des destinataires avec contrainte de rôle :
   * - Admin / Superadmin : Mode transversal (Accès à tous, marquage visuel)
   * - Autres rôles : Mode cloisonné (Masquage et désactivation des utilisateurs hors cellule)
   */
  filterAssigneeList(celluleId, userRole) {
    const $assigneeSelect = $('#assignee_a');
    const $options = $assigneeSelect.find('option');

    // Vérification du niveau de privilège
    const isAdmin = userRole === 'administrateur' || userRole === 'superadmin';

    // Icône stylisée pour remplacer l'étoile standard
    const icon = '👤 ';

    // Cas où aucun document n'est sélectionné
    if (!celluleId) {
      $options.each(function () {
        const $option = $(this);
        if ($option.val() !== '') {
          // Sauvegarde et nettoyage du nom d'origine au tout premier passage
          if (!$option.data('original-text')) {
            $option.data('original-text', $option.text().trim());
          }
          const originalText = $option.data('original-text');

          if (isAdmin) {
            $option.show().prop('disabled', false).text(originalText);
          } else {
            $option.hide().prop('disabled', true);
          }
        }
      });
      if (!isAdmin) $assigneeSelect.val('');
      return;
    }

    // Parcours et filtrage dynamique
    $options.each(function () {
      const $option = $(this);
      const userCellule = $option.data('cellule');

      if ($option.val() === '') return; // Placeholder

      // 🟢 Sauvegarde du texte d'origine nettoyé de tout espace inutile ou ancien badge
      if (!$option.data('original-text')) {
        // Supprime les résidus si le HTML initial contenait déjà des suffixes
        let textRaw = $option.text().replace('(Hors UNITE)', '').replace('⭐ (Même UNITE)', '').trim();
        $option.data('original-text', textRaw);
      }

      const originalText = $option.data('original-text');

      if (String(userCellule) === String(celluleId)) {
        $option.show().prop('disabled', false);
        if (isAdmin) {
          $option.text(`${icon} (Même UNITE) ${originalText}`).addClass('meme-unite').removeClass('hors-unite');
        } else {
          $option.text(originalText).removeClass('meme-unite hors-unite');
        }
      } else {
        if (isAdmin) {
          $option.show().prop('disabled', false);
          $option.text(`${originalText} (Hors UNITE)`).addClass('hors-unite').removeClass('meme-unite');
        } else {
          $option.hide().prop('disabled', true);
        }
      }
    });

    // Si l'utilisateur actuel (non-admin) avait déjà sélectionné quelqu'un qui se retrouve masqué, on reset
    if (!isAdmin && $assigneeSelect.val() !== '') {
      const selectedOptionCellule = $assigneeSelect.find('option:selected').data('cellule');
      if (String(selectedOptionCellule) !== String(celluleId)) {
        $assigneeSelect.val('');
      }
    }
  },

  // Rendu de la pagination
  renderPagination(data) {
    renderPagination(data, '#taches-pagination', '#pagination-info');
  },

  setupCreateForm(formSelector = '#tacheForm') {
    const $form = $(formSelector);
    if (!$form.length) return;

    $form.trigger('reset');
    $('#update-id').val('');

    // Libérer le sélecteur de document pour la création pure
    const $documentSelect = $form.find('[name="document"]');
    enableElement($documentSelect);

    // Mode création : on affiche les métadonnées, on cache les zones de traitement
    $form.find('.meta-field').prop('disabled', false);
    $form.find('#zone-traitement-assigne').addClass('d-none');
    $form.find('#zone-versioning-document').addClass('d-none');
    $('#timeline-commentaires').empty().addClass('d-none');
  },

  setupDynamicForm(tache, currentUserId, currentUserRole, formSelector = '#tacheForm') {
    const $form = $(formSelector);
    $form.trigger('reset');

    // Remplissage des champs cachés et de base
    $('#update-id').val(tache.id);
    $form.find('[name="titre"]').val(tache.titre);
    $form.find('[name="description"]').val(tache.description);
    $form.find('[name="document"]').val(tache.document).trigger('change');
    $form.find('[name="assignee_a"]').val(tache.assignee_a);
    $form.find('[name="priorite"]').val(tache.priorite);
    $form.find('[name="date_echeance"]').val(tache.date_echeance);
    $form.find('[name="statut"]').val(tache.statut);

    // Injection et sélection du document
    const $documentSelect = $form.find('[name="document"]');
    $documentSelect.val(tache.document).trigger('change');
    disableElement($documentSelect);

    // Détermination des rôles sur le ticket
    const isManager =
      ['superadmin', 'admin', 'responsable'].includes(currentUserRole) || tache.assignee_par === currentUserId;
    const isAssignee = tache.assignee_a === currentUserId;

    // 🔴 REGLE 1 : Qui peut modifier les structures/métadonnées de la tâche ?
    if (isManager && tache.statut !== 'terminee') {
      $form.find('.meta-field').prop('disabled', false);
    } else {
      $form.find('.meta-field').prop('disabled', true); // Lecture seule pour l’assigné
    }

    // 🟢 REGLE 2 : Zone de traitement et de versioning pour l'assigné
    if (isAssignee && tache.statut !== 'terminee') {
      $form.find('#zone-traitement-assigne').removeClass('d-none');
      $form.find('#zone-versioning-document').removeClass('d-none');
      $form.find('[name="statut"]').prop('disabled', false); // L'assigné peut changer le statut (ex: En révision)
    } else {
      $form.find('#zone-traitement-assigne').addClass('d-none');
      $form.find('#zone-versioning-document').addClass('d-none');
    }

    // 📜 REGLE 3 : Affichage de l'historique des traitements passés (Timeline)
    if (tache.commentaires && tache.commentaires.length > 0) {
      this.renderTimeline(tache.commentaires);
    } else {
      $('#timeline-commentaires').empty().addClass('d-none');
    }
  },

  renderTimeline(commentaires) {
    const $container = $('#timeline-commentaires').removeClass('d-none');
    $container.empty();

    const html = commentaires
      .map(
        c => `
      <div class="timeline-item mb-3 p-2 border-start border-primary border-3 bg-light">
        <small class="text-muted"><strong>${c.auteur_name}</strong> - ${new Date(c.Date_creation).toLocaleString()}</small>
        <p class="mb-0 mt-1">${c.contenu}</p>
        ${c.nouveau_statut ? `<span class="badge bg-secondary mt-1">${c.nouveau_statut}</span>` : ''}
      </div>
    `
      )
      .join('');

    $container.html('<h5>Historique du traitement</h5>' + html);
  },

  renderForm(tache = null) {
    if (tache) {
      $('#update-id').val(tache.id);
      $('#titre').val(tache.titre);
      $('#description').val(tache.description);
      $('#document').val(tache.document).trigger('change');
      $('#assignee_a').val(tache.assignee_a).trigger('change');
      $('#priorite').val(tache.priorite);
      $('#statut').val(tache.statut);
      $('#date_echeance').val(tache.date_echeance ? tache.date_echeance.split('T')[0] : '');
      $('#modal-title').text('Modifier la tâche');
      $('#save-btn-text').text('Mettre à jour');
    } else {
      resetForm('#tacheForm');
      $('#update-id').val('');
      $('#modal-title').text('Nouvelle tâche');
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
