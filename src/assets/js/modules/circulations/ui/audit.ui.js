// src/assets/js/modules/circulations/ui/audit.ui.js
import { showAlertMessage, renderPagination } from '../../../helpers/utils.js';

export const AuditUi = {
  // Configuration des classes de couleur pour les types d'actions
  actionColors: {
    creation: 'bg-label-success',
    modification: 'bg-label-warning',
    suppression: 'bg-label-danger',
    connexion: 'bg-label-primary',
    deconnexion: 'bg-label-secondary'
  },

  /**
   * Renvoie un badge HTML stylisé pour l'action d'audit
   */
  getActionBadge(action, display) {
    const colorClass = this.actionColors[action] || 'bg-label-secondary';
    return `<span class="badge ${colorClass}">${display || action}</span>`;
  },

  /**
   * Renvoie un badge HTML pour le statut de l'opération (success / failure)
   */
  getStatutBadge(statut, display) {
    const isSuccess = statut === 'success';
    const bgClass = isSuccess ? 'bg-success' : 'bg-danger';
    return `<span class="badge ${bgClass} text-white rounded-pill px-2" style="font-size: 0.75rem;">${display || statut}</span>`;
  },

  /**
   * Rendu principal du tableau des logs d'audit
   * @param {Object} response - Réponse paginée de l'API Client
   */
  renderTable(response) {
    const tbody = $('#audits-tbody');
    tbody.empty();

    const logs = response.results || response;

    if (!logs || logs.length === 0) {
      tbody.html(
        '<tr><td colspan="7" class="text-center text-muted py-4"><i class="ri-database-2-line ri-2x mb-2 d-block"></i>Aucun événement enregistré dans le journal d\'audit.</td></tr>'
      );
      this.renderPagination(0);
      return;
    }

    const rows = logs.map(log => this.createAuditRow(log)).join('');
    tbody.html(rows);

    this.renderPagination(response);
  },

  /**
   * Construit une ligne HTML de tableau pour une entrée d'audit unique
   */
  createAuditRow(log) {
    const dateCreation = new Date(log.timestamp).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });

    // Gestion de l'opérateur système ou utilisateur anonyme
    let operateurHtml = `<span class="badge bg-label-secondary"><i class="ri-computer-line"></i> Système / Anonyme</span>`;
    if (log.utilisateur_info) {
      operateurHtml = `
        <div class="d-flex flex-column">
          <span class="fw-bold">${log.utilisateur_info.full_name || log.utilisateur_info.username}</span>
          <small class="text-muted">@${log.utilisateur_info.username}</small>
        </div>`;
    }

    const actionBadge = this.getActionBadge(log.action, log.action_display);
    const statutBadge = this.getStatutBadge(log.statut, log.statut_display);
    const ipAddress = log.ip_address || '—';

    // Génération dynamique de l'URL de détail Django
    const detailUrl = `/supervision/audit/${log.id}/`;

    return `
      <tr data-log-id="${log.id}">
        <td><span class="text-sm fw-medium">${dateCreation}</span></td>
        <td>${operateurHtml}</td>
        <td>${actionBadge}</td>
        <td>
          <div class="d-flex flex-column">
            <span class="text-wrap" style="max-width: 250px;"><strong>${log.objet_label || '—'}</strong></span>
            <small class="text-muted text-xs">${(log.objet_type || 'INCONNU').toUpperCase()} #${log.object_id || ''}</small>
          </div>
        </td>
        <td>${statutBadge}</td>
        <td><code>${ipAddress}</code></td>
        <td>
          <a href="${detailUrl}" class="btn btn-sm btn-icon btn-outline-primary" title="Inspecter les métadonnées">
            <i class="ri-eye-line"></i>
          </a>
        </td>
      </tr>`;
  },

  /**
   * Gestion de la pagination via l'utilitaire global partagé
   */
  renderPagination(data) {
    renderPagination(data, '#audits-pagination', '#pagination-info');
  },

  showError(message, id = '#message-show-error', loader = null) {
    showAlertMessage(message, id, loader);
  },

  showSuccess(message, id = '#message-show-success', loader = null) {
    showAlertMessage(message, id, loader);
  }
};
