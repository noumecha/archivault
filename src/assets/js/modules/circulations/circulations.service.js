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

  update(id, data) {
    return ApiClient.request(`/api/circulations/${id}/update/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  logConsultation(id) {
    return ApiClient.request(`/api/circulations/${id}/log-consultation/`, {
      method: 'POST'
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

  /***
   * Récupère les données du formulaire d'initialisation de circuit
   * @param {string} formSelector - Le sélecteur du formulaire
   * @returns {Object} Les données formatées pour l'API
   */
  getFormData(formSelector) {
    const $form = $(formSelector);
    const data = {
      document: $form.find('#doc-select').val(),
      titre: $form.find('#circuit-titre').val(),
      description: $form.find('#circuit-desc').val(),
      date_fin: $form.find('#date-fin').val(),
      etapes: []
    };

    $form.find('.etape-item').each(function (i) {
      data.etapes.push({
        id: $(this).find('.etape-id').val() || null,
        destinataire: $(this).find('#etape-user-select').val(),
        ordre: i + 1,
        titre_etape: $(this).find('input[name*="[titre_etape]"]').val(),
        date_echeance: $(this).find('input[name*="[date_echeance]"]').val()
      });
    });

    return data;
  },

  /**
   * Validez les données du formulaire de circulation
   * @param {*} data
   * @returns
   */
  validate(data) {
    const errors = {};

    if (!data.document) errors.document = ['Le document est requis'];
    if (!data.date_fin) errors.date_fin = ['La date de fin est requise'];
    if (!data.titre || data.titre.trim().length === 0) {
      errors.titre = ['Le titre du circuit est requis'];
    }

    if (data.etapes && Array.isArray(data.etapes)) {
      if (data.etapes.length === 0) {
        errors.etapes_global = ['Au moins une étape est requise'];
      } else {
        const etapesErrors = {};
        data.etapes.forEach((etape, index) => {
          let messages = [];

          if (!etape.titre_etape) messages.push('Titre requis');
          if (!etape.destinataire) messages.push('Destinataire requis');
          if (!etape.date_echeance) messages.push('Échéance requise');

          const currentEcheance = new Date(etape.date_echeance);
          const now = new Date();

          if (etape.date_echeance && currentEcheance < now) {
            messages.push("L'échéance doit être dans le futur");
          }

          if (etape.date_echeance && data.date_fin && currentEcheance > new Date(data.date_fin)) {
            messages.push("L'échéance ne peut pas dépasser la fin du circuit");
          }

          if (index > 0 && etape.date_echeance) {
            const prevEcheanceRaw = data.etapes[index - 1].date_echeance;
            if (prevEcheanceRaw) {
              const prevEcheance = new Date(prevEcheanceRaw);
              if (currentEcheance < prevEcheance) {
                messages.push("L'échéance doit être après celle de l'étape précédente");
              }
            }
          }

          if (messages.length > 0) {
            etapesErrors[index] = messages.join(', ');
          }
        });

        if (Object.keys(etapesErrors).length > 0) {
          errors.etapes = etapesErrors;
        }
      }
    }

    if (Object.keys(errors).length > 0) {
      throw { data: { errors: errors, message: 'Validation locale échouée' } };
    }
    return true;
  },

  /**
   * Valide les données du formulaire de traitement d'étape
   * Supporte aussi bien un objet simple qu'un FormData
   * @param {FormData|Object} data
   * @returns {boolean}
   */
  validateDecision(data) {
    console.log('Validation des données de décision :', data);
    const errors = {};

    // Prise en compte de 'retourne'
    const validDecisions = ['valide', 'rejete', 'retourne'];

    const isFormData = data instanceof FormData;
    const decision = isFormData ? data.get('decision') : data.decision;
    const commentaire = isFormData ? data.get('commentaire') : data.commentaire;
    const isDocumentModifie = isFormData ? data.get('is_document_modifie') : data.is_document_modifie;

    // Récupération du fichier : attention, le nom dans le FormData doit correspondre au name de l'input HTML
    const fichier = isFormData ? data.get('fichier') : data.fichier;

    // 1. Validation de la décision globale
    if (!decision || !validDecisions.includes(decision)) {
      errors.decision = ['Veuillez sélectionner une décision valide (Valider, Rejeter ou Retourner).'];
    }

    // 2. Validation du commentaire pour Rejet OU Retour
    if (decision === 'rejete' || decision === 'retourne') {
      if (!commentaire || commentaire.trim().length < 5) {
        errors.commentaire = [
          `Un commentaire explicatif est obligatoire pour justifier le ${decision === 'rejete' ? 'rejet' : 'retour'} (min. 5 caractères).`
        ];
      }
    }

    // 3. Validation spécifique à la validation ('valide')
    if (decision === 'valide') {
      // Vérifier si le choix Oui/Non a été fait
      if (!isDocumentModifie) {
        errors.is_document_modifie = ['Veuillez spécifier si vous avez modifié le document original ou non.'];
      }
      // Si "Oui", le fichier devient obligatoire
      else if (isDocumentModifie === 'oui') {
        if (!fichier || (fichier instanceof File && fichier.size === 0)) {
          errors.fichier = ['Vous avez indiqué avoir modifié le document. Veuillez charger la nouvelle version.'];
        }
      }
    }

    // Levée des erreurs si existantes
    if (Object.keys(errors).length > 0) {
      throw {
        data: {
          errors: errors
        }
      };
    }

    return true;
  }
};
