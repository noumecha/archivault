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
   * @param {FormData} decisionData - FormData contenant decision, commentaire et optionnellement un fichier
   */
  traiterEtape(id, decisionData) {
    return ApiClient.request(`/api/circulations/${id}/traiter/`, {
      method: 'POST',
      body: decisionData
    });
  },

  // ── Validation ───────────────────────────────────────────────────────────

  /**
   * Valide les données de base d'une circulation ou d'une initialisation
   */
  validate(data) {
    const errors = {};

    if (!data.document) errors.document = ['Le document est requis'];
    if (!data.date_fin) errors.date_fin = ['La date de fin est requise'];
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
          if (!errors.etapes) errors.etapes = {};
          let etapeErrors = [];

          if (!etape.titre_etape) etapeErrors.push("Le titre de l'étape est requis");
          if (!etape.destinataire) etapeErrors.push('Le destinataire est requis');
          if (!etape.date_echeance) etapeErrors.push("La date d'échéance est requise");
          if (etape.date_echeance && new Date(etape.date_echeance) < new Date())
            etapeErrors.push("La date d'échéance doit être dans le futur");
          if (etape.date_echeance && data.date_fin && new Date(etape.date_echeance) > new Date(data.date_fin))
            etapeErrors.push("La date d'échéance de l'étape ne peut pas dépasser la date de fin du circuit");

          if (etapeErrors.length > 0) {
            errors.etapes[index] = etapeErrors.join(', ');
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

    const decision = data instanceof FormData ? data.get('decision') : data.decision;
    const commentaire = data instanceof FormData ? data.get('commentaire') : data.commentaire;

    if (!decision || !validDecisions.includes(decision)) {
      errors.decision = ['Une décision valide est requise'];
    }

    // Obliger un commentaire en cas de rejet ou retour
    if ((decision === 'rejete' || decision === 'retourne') && (!commentaire || commentaire.trim().length < 5)) {
      errors.commentaire = ['Un commentaire explicatif est requis (min. 5 caractères)'];
    }

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation de décision échouée' } };
    }
    return true;
  }
};
