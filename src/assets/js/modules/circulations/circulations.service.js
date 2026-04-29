import { ApiClient } from '../../helpers/api-client.js';

export const CirculationService = {
  // ── Opérations CRUD standards ────────────────────────────────────────────
  fetchAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return ApiClient.request(`/api/circulations/?${query}`);
  },

  fetchOne(id) {
    return ApiClient.request(`/api/circulations/${id}/`);
  },

  create(data) {
    return ApiClient.request('/api/circulations/create/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  update(id, data) {
    return ApiClient.request(`/api/circulations/${id}/update/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  remove(id) {
    return ApiClient.request(`/api/circulations/${id}/delete/`, {
      method: 'DELETE'
    });
  },

  // ── Actions personnalisées ───────────────────────────────────────────────
  bulkDelete(ids) {
    return ApiClient.request('/api/circulations/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids })
    });
  },

  // ── Actions Spécifiques au Workflow (Circulation) ────────────────────────

  /**
   * Initialise un circuit complet avec ses étapes
   * @param {Object} data - { document: id, titre: "", description: "", etapes: [...] }
   */
  initierCircuit(data) {
    return ApiClient.request('/api/circulations/initier/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Traite l'étape actuelle (Valider, Rejeter, Retourner)
   * @param {number} id - ID de la circulation
   * @param {Object} decisionData - { decision: "valide", commentaire: "..." }
   */
  traiterEtape(id, decisionData) {
    return ApiClient.request(`/api/circulations/${id}/traiter/`, {
      method: 'POST',
      body: JSON.stringify(decisionData)
    });
  },

  // ── Validation ───────────────────────────────────────────────────────────

  /**
   * Valide les données de base d'une circulation ou d'une initialisation
   */
  validate(data) {
    const errors = {};

    if (!data.document) errors.document = ['Le document est requis'];
    if (!data.titre || data.titre.trim().length === 0) {
      errors.titre = ['Le titre du circuit est requis'];
    }

    // Si on est dans le cadre d'une initialisation de circuit (avec étapes)
    if (data.etapes) {
      if (!Array.isArray(data.etapes) || data.etapes.length === 0) {
        errors.etapes = ['Au moins une étape est requise pour le circuit'];
      } else {
        // Validation sommaire de chaque étape
        data.etapes.forEach((etape, index) => {
          if (!etape.destinataire) {
            if (!errors.etapes) errors.etapes = {};
            errors.etapes[index] = 'Le destinataire est requis pour cette étape';
          }
        });
      }
    }

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  /**
   * Valide spécifiquement la décision sur une étape
   */
  validateDecision(data) {
    const errors = {};
    const validDecisions = ['valide', 'rejete', 'retourne'];

    if (!data.decision || !validDecisions.includes(data.decision)) {
      errors.decision = ['Une décision valide est requise'];
    }

    // Obliger un commentaire en cas de rejet ou retour
    if (
      (data.decision === 'rejete' || data.decision === 'retourne') &&
      (!data.commentaire || data.commentaire.trim().length < 5)
    ) {
      errors.commentaire = ['Un commentaire explicatif est requis (min. 5 caractères)'];
    }

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation de décision échouée' } };
    }
    return true;
  }
};
