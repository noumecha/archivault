// src/assets/js/modules/circulations/controllers/audit.controller.js
import { AuditService } from '../services/audit.service.js';
import { AuditUi } from '../ui/audit.ui.js';
import { startLoader, closeLoader } from '../../../helpers/utils.js';

export const AuditController = {
  async init() {
    // Si le corps du tableau d'audit est présent dans le DOM, charger les données initiales
    if ($('#audits-tbody').length) {
      await this.loadAudits();
    }
    this.bindEvents();
    this.bindMaintenanceEvents();
  },

  /**
   * Charge les données de l'API d'audit avec les filtres sélectionnés
   * @param {Object} params
   */
  async loadAudits(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await AuditService.fetchAll(params);

      // Injection de la page courante pour l'utilitaire de pagination globale
      res.current_page = parseInt(params.page) || 1;

      AuditUi.renderTable(res);
    } catch (err) {
      console.error("Erreur de chargement du journal d'audit:", err);
      AuditUi.showError("Erreur critique lors du chargement du journal d'audit système.");
    } finally {
      closeLoader('#table-loader');
    }
  },

  /**
   * Événements d'interaction standard (Recherche, Pagination, Rafraîchissement)
   */
  bindEvents() {
    // Écouteur sur les liens de pagination générés par l'UI
    $(document).on('click', '#audits-pagination .page-link', async function (e) {
      e.preventDefault();
      const page = $(this).data('page');
      if (page) {
        let params = AuditController.getCurrentParams();
        params.page = page;
        await AuditController.loadAudits(params);
      }
    });

    // Recherche globale temps réel (Debounce) et filtres Select2/Select de BaseCRUDView
    let searchTimer;
    $('#audit-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        const params = this.getCurrentParams();
        this.loadAudits(params);
      }, 350);
    });

    // Bouton d'effacement de la recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      const params = this.getCurrentParams();
      this.loadAudits(params);
    });

    // Bouton de rafraîchissement complet
    $('#refresh-button').on('click', () => {
      this.loadAudits();
      $('#audit-search-form').trigger('reset');
      $('#clearSearch').trigger('click');
    });
  },

  /**
   * Événements liés aux actions de maintenance (Purge des anciens logs)
   */
  bindMaintenanceEvents() {
    // Intercepter la soumission du formulaire de purge (SuperAdmin)
    $('#purgerAuditForm').on('submit', async e => {
      e.preventDefault();

      const $btn = $('#confirm-purge-btn');
      const formData = {
        mois_conservation: $('#id_mois_conservation').val()
      };

      try {
        // 1. Validation locale
        AuditService.validatePurge(formData);

        // 2. Traitement API
        $btn.prop('disabled', true);
        startLoader('#purge-loader');
        $('#purge-form-error').hide();

        const response = await AuditService.purgerLogs(formData);

        // 3. Succès et rechargement
        const bootstrapModal = bootstrap.Modal.getInstance(document.getElementById('modal-purger-logs'));
        if (bootstrapModal) bootstrapModal.hide();

        AuditUi.showSuccess(response.message || "La purge de maintenance s'est déroulée avec succès.");
        await this.loadAudits(this.getCurrentParams());
      } catch (err) {
        console.error("Erreur lors de l'exécution de la purge:", err);
        const errorMsg =
          err.data?.errors?.mois_conservation?.[0] ||
          err.data?.message ||
          'Une erreur système est survenue durant la purge.';
        AuditUi.showError(errorMsg, '#purge-form-error');
      } finally {
        $btn.prop('disabled', false);
        closeLoader('#purge-loader');
      }
    });
  },

  /**
   * Extrait dynamiquement tous les paramètres actifs des inputs du formulaire
   * @returns {Object} Un objet contenant les couples clés/valeurs pour l'API
   */
  getCurrentParams() {
    const formArray = $('#audit-search-form').serializeArray();
    const params = {};

    formArray.forEach(item => {
      if (item.value && item.value.trim() !== '') {
        params[item.name] = item.value;
      }
    });

    return params;
  }
};
AuditController.init();
