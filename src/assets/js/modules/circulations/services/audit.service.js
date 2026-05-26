// src/assets/js/modules/circulations/services/audit.service.js
import { ApiClient } from '../../../helpers/api-client.js';

export const AuditService = {
  /**
   * Récupère la liste paginée et filtrée des logs d'audit
   * @param {Object} params - { page, search, action, statut, utilisateur }
   */
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/audits/?${query}`);
  },

  /**
   * Récupère les détails complets d'une seule entrée d'audit
   * @param {number} id - ID du log d'audit
   */
  fetchOne(id) {
    return ApiClient.request(`/api/audits/${id}/`);
  },

  /**
   * Déclenche la purge de maintenance des logs (SuperAdmin)
   * @param {Object} data - { mois_conservation: X }
   */
  purgerLogs(data) {
    return ApiClient.request('/api/audits/purge/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Valide localement le formulaire de purge avant envoi à l'API
   * @param {Object} data
   * @returns {boolean}
   */
  validatePurge(data) {
    const errors = {};
    const mois = parseInt(data.mois_conservation);

    if (!data.mois_conservation) {
      errors.mois_conservation = ["Le choix d'un seuil de conservation est obligatoire."];
    } else if (isNaN(mois) || mois < 1) {
      errors.mois_conservation = ['Le seuil de conservation spécifié est invalide.'];
    }

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation de maintenance échouée' } };
    }
    return true;
  }
};
