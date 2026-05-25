import { CirculationService } from './circulations.service.js';
import { CirculationUi } from './circulations.ui.js';
import { startLoader, closeLoader, toggleBulkButton, enableElement } from '../../helpers/utils.js';

export const CirculationController = {
  etapeIndex: 0,
  docCelluleMap: {}, // Stockage du mapping

  async init() {
    // Récupérer le mapping depuis le script JSON du template
    const mapData = document.getElementById('doc-cellule-data');
    if (mapData) {
      this.docCelluleMap = JSON.parse(mapData.textContent);
    }
    if ($('#circulations-tbody').length) {
      await this.loadCirculations();
    }
    this.bindEvents();
    this.bindWorkflowEvents();
  },

  // ─── Chargement des données ───────────────────────────────────────
  async loadCirculations(params = {}) {
    try {
      startLoader('#table-loader');
      const res = await CirculationService.fetchAll(params);
      res.current_page = parseInt(params.page) || 1;
      CirculationUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      CirculationUi.showError('Erreur lors du chargement des circuits');
    } finally {
      closeLoader('#table-loader');
    }
  },

  // ─── Événements de base (Recherche, Pagination) ───────────────────
  bindEvents() {
    $('#modal-initier-circuit').on('hidden.bs.modal', () => {
      const $form = $('#initierCircuitForm');
      $form[0].reset();
      $('#etapes-container').empty();
      $('#update-id').val('');
      CirculationUi.etapeIndex = 0;
      enableElement('#doc-select');
    });

    // Écouter le changement de document pour filtrer
    $('#doc-select').on('change', e => {
      const docId = e.target.value;
      const celluleId = this.docCelluleMap[docId];
      CirculationUi.filterUserSelects(celluleId);
    });

    // Pagination
    $(document).on('click', '#circulations-pagination .page-link', async function (e) {
      e.preventDefault();
      const page = $(this).data('page');
      if (page) {
        let params = CirculationController.getCurrentParams();
        params.page = page;
        await CirculationController.loadCirculations(params);
      }
    });

    //Gestion de la sélection multiple
    $(document).on('change', '#check-all-circulations', function () {
      const isChecked = $(this).is(':checked');
      $('.circulation-checkbox').prop('checked', isChecked);
      toggleBulkButton('.circulation-checkbox:checked', '#bulk-actions-container');
    });

    // suppression groupée
    $(document).on('click', '#btn-bulk-delete', function (e) {
      e.preventDefault();
      const ids = $('.circulation-checkbox:checked')
        .map(function () {
          return $(this).val();
        })
        .get();

      if (ids.length === 0) {
        return;
      }

      const modalElement = document.getElementById('bulk-delete-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-bulk-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-bulk-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#bulk-delete-loader');
            const res = await CirculationService.bulkDelete(ids);
            CirculationUi.showSuccess(res.message);
            modalInstance.hide();
            const currentParams = CirculationController.getCurrentParams();
            await CirculationController.loadCirculations(currentParams);
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Erreur lors de la suppression groupée';
            CirculationUi.showError(message, '#bulk-delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#bulk-delete-loader');
          }
        });
    });

    // Recherche
    let searchTimer;
    $('#circ-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        const params = this.getCurrentParams();
        this.loadCirculations(params);
      }, 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadCirculations();
    });

    // Refresh
    $('#refresh-button').on('click', () => {
      this.loadCirculations();
      // reset filter forms
      $('#circ-search-form').trigger('reset');
      $('#clearSearch').trigger('click');
    });

    // Supprimer
    $(document).on('click', '[data-action="delete-circulation"]', e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      const modalElement = document.getElementById('delete-circulation-modal');
      const modalInstance = new bootstrap.Modal(modalElement);

      modalInstance.show();

      $('#confirm-delete-btn')
        .off('click')
        .on('click', async () => {
          const $btn = $('#confirm-delete-btn');

          try {
            $btn.prop('disabled', true);
            startLoader('#delete-loader');

            await CirculationService.remove(id);

            modalInstance.hide();
            CirculationUi.showSuccess('Circulation supprimée avec succès');

            await this.loadCirculations(this.getCurrentParams());
          } catch (err) {
            console.error('Erreur suppression:', err);
            const message = err.data?.message || 'Impossible de supprimer cette circulation';
            CirculationUi.showError(message, '#delete-form-error');
          } finally {
            $btn.prop('disabled', false);
            closeLoader('#delete-loader');
          }
        });
    });

    // Modifier circulation
    $(document).on('click', '[data-action="edit-circulation"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await CirculationService.fetchOne(id);
        // Passe res.data ET le mapping du contrôleur
        CirculationUi.renderForm(res.data, CirculationController.docCelluleMap);
        new bootstrap.Modal(document.getElementById('modal-initier-circuit')).show();
      } catch (err) {
        console.error('Erreur chargement circulation:', err);
        CirculationUi.showError('Erreur chargement circulation');
      }
    });

    // Voir (Détail) - Gestion du tracking de lecture hiérarchique des circulations
    $(document).on('click', '[data-action="view"]', async function (e) {
      e.preventDefault();

      const $btn = $(this);
      const circulationId = $btn.data('id');
      const targetUrl = `/circulations/detail/${circulationId}/`;

      const $row = $btn.closest('tr');
      const actuelActeurId = $row.data('actuel-acteur-id');
      const currentUserId = window.CURRENT_USER_ID;

      const isActuelActeur =
        $row.length && actuelActeurId && currentUserId && String(actuelActeurId) === String(currentUserId);

      if (isActuelActeur) {
        try {
          await CirculationService.logConsultation(circulationId);
        } catch (err) {
          console.warn("Échec de l'enregistrement de l'accusé de réception circulation :", err);
        } finally {
          window.location.href = targetUrl;
        }
      } else {
        window.location.href = targetUrl;
      }
    });

    // Détail / Timeline
    $(document).on('click', '[data-action="view-timeline"]', async e => {
      const id = $(e.currentTarget).data('id');
      try {
        const res = await CirculationService.fetchOne(id);
        CirculationUi.renderTimeline(res.data);
        new bootstrap.Modal(document.getElementById('modal-timeline')).show();
      } catch (err) {
        CirculationUi.showError('Impossible de charger la timeline');
      }
    });
  },

  // ─── Événements du Workflow (Création & Traitement) ───────────────
  bindWorkflowEvents() {
    // Écouter le changement de document pour filtrer
    $('#doc-select').on('change', e => {
      const docId = e.target.value;
      const celluleId = this.docCelluleMap[docId] || null;

      // Optionnel : Vider les étapes si on change de document pour éviter les erreurs
      $('#etapes-container').empty();
      this.etapeIndex = 0;

      // Appliquer le filtre (UI)
      CirculationUi.filterUserSelects(celluleId);
    });

    // ajouter une étape
    $('#btn-add-etape').on('click', e => {
      const currentDocId = $('#doc-select').val();
      const activeCelluleId = this.docCelluleMap[currentDocId] || null;

      if (!activeCelluleId) {
        CirculationUi.showSuccess('Veuillez sélectionner un document lié à une cellule.', '#form-error', null);
        return;
      }

      const html = CirculationUi.renderEtapeRow(CirculationUi.etapeIndex, activeCelluleId);
      $('#etapes-container').append(html);

      CirculationUi.etapeIndex++;
    });

    // supprimer une étape
    $(document).on('click', '.remove-etape', function () {
      $(this).closest('.etape-item').remove();
      CirculationController.reindexEtapes();
    });

    // Soumission Initialisation Circuit
    $('#initierCircuitForm').on('submit', async e => {
      e.preventDefault();
      const $btn = $('#save-circuit-btn');
      const data = CirculationService.getFormData($('#initierCircuitForm'));
      console.log('Données avant envoi:', data);
      try {
        const id = $('#update-id').val();
        $btn.prop('disabled', true);
        CirculationService.validate(data);
        let response;
        if (id) {
          response = await CirculationService.update(id, data);
        } else {
          response = await CirculationService.initierCircuit(data);
        }
        CirculationUi.showSuccess(response.message || 'Circuit initié avec succès', '#form-success');
        setTimeout(async () => {
          const modalInstance = bootstrap.Modal.getInstance(document.getElementById('modal-initier-circuit'));
          if (modalInstance) modalInstance.hide();
          await this.loadCirculations(this.getCurrentParams());
          $('#initierCircuitForm')[0].reset();
          enableElement('#doc-select');
          CirculationController.reindexEtapes();
        }, 3000);
      } catch (err) {
        console.log('error : ', err);
        const msg = err.data?.errors || err.data?.message || 'Erreur de validation';
        CirculationUi.showError(msg, '#form-error');
      } finally {
        $btn.prop('disabled', false);
      }
    });

    // 1. Écouteur sur le changement de décision globale
    $(document).on('change', 'input[name="decision"]', function () {
      const decision = $(this).val();

      if (decision === 'valide') {
        $('#document-modifie-section').slideDown();
        $('#delai-retour-section').slideUp();

        // Rétablir l'affichage de l'upload si 'Oui' était déjà coché
        if ($('input[name="is_document_modifie"]:checked').val() === 'oui') {
          $('#version-upload-section').slideDown();
        }
      } else {
        // Si 'rejete' ou 'retourne'
        $('#document-modifie-section').slideUp();
        $('#version-upload-section').slideUp();
        $('#delai-retour-section').slideDown();
      }
    });

    // Ecouteur sur le changement du choix "Document modifié"
    $(document).on('change', 'input[name="is_document_modifie"]', function () {
      if ($(this).val() === 'oui') {
        $('#version-upload-section').slideDown();
      } else {
        $('#version-upload-section').slideUp();
        $('#document-revision').val('');
      }
    });

    // OUVERTURE DE LA MODAL (Déclencheur)
    $(document).on('click', '[data-action="process"]', e => {
      const $btn = $(e.currentTarget);
      const id = $btn.data('id');
      const ordre = $btn.data('ordre') || 'En cours';

      // Reset du formulaire à blanc à chaque ouverture
      const form = document.getElementById('traitementForm');
      if (form) form.reset();

      $('#process-circ-id').val(id);
      $('#display-etape-ordre').text(ordre);
      $('#display-doc-titre').text($btn.data('doc-titre') || 'Document inconnu');
      $('#traiter-show-error').hide().text('');
      $('#traiter-show-success').hide().text('');

      // États initiaux par défaut (Puisque 'valide' est coché par défaut dans le HTML)
      $('#dec-valide').prop('checked', true);
      $('#document-modifie-section').show();
      $('#version-upload-section').hide();
      $('#delai-retour-section').hide();

      // Affichage de la modal Bootstrap
      new bootstrap.Modal(document.getElementById('modal-traiter-etape')).show();
    });

    // TRAITEMENT D'UNE ÉTAPE (Décision)
    $('#traitementForm').on('submit', async e => {
      e.preventDefault();
      const $form = $(e.currentTarget);
      const id = $('#process-circ-id').val();
      const $btnSubmit = $('#save-traiter-btn');

      if (!id) {
        CirculationUi.showError('Erreur : ID de circulation introuvable.');
        return;
      }

      // Utilisation de FormData pour supporter l'upload de fichier
      const formData = new FormData();
      const decision = $('input[name="decision"]:checked').val();
      const isDocumentModifie = $('input[name="is_document_modifie"]:checked').val();
      formData.append('decision', decision);
      formData.append('is_document_modifie', isDocumentModifie);
      formData.append('commentaire', $('#decision-commentaire').val());

      // Gestion conditionnelle des paramètres selon la décision
      if (decision === 'valide') {
        if (isDocumentModifie === 'oui') {
          const fileInput = document.getElementById('document-revision');
          if (fileInput && fileInput.files[0]) {
            formData.append('fichier', fileInput.files[0]);
          }
        }
      } else if (decision === 'retourne') {
        const delaiHeures = $('#delai_retour_heures').val();
        if (delaiHeures) {
          formData.append('delai_retour_heures', delaiHeures);
        }
      }

      try {
        CirculationService.validateDecision(formData);
        $btnSubmit.prop('disabled', true);
        let res = await CirculationService.traiterEtape(id, formData);
        CirculationUi.showSuccess(
          res.message || 'Décision enregistrée',
          '#traiter-show-success',
          '#traiter-form-loader'
        );
        setTimeout(async () => {
          const modalElement = document.getElementById('modal-traiter-etape');
          const modalInstance = bootstrap.Modal.getInstance(modalElement);
          if (modalInstance) modalInstance.hide();
          if (typeof CirculationController.loadCirculations === 'function') {
            await CirculationController.loadCirculations();
            $form[0].reset();
          } else {
            window.location.reload();
          }
        }, 1500);
      } catch (err) {
        console.error('Erreur traitement étape:', err);
        const errorMsg = err.data?.errors || err.data?.message || 'Erreur lors du traitement';
        CirculationUi.showError(errorMsg, '#traiter-show-error', '#traiter-form-loader');
      } finally {
        $btnSubmit.prop('disabled', false);
      }
    });
  },

  getCurrentParams() {
    return Object.fromEntries(new FormData($('#circ-search-form')[0]));
  },

  reindexEtapes() {
    const $items = $('#etapes-container .etape-item');
    $items.each((idx, el) => {
      const $el = $(el);
      $el.find('.col-md-1').text(`#${idx + 1}`);
      $el.attr('data-index', idx);
      $el.find('input, select').each(function () {
        const name = $(this).attr('name');
        if (name) {
          $(this).attr('name', name.replace(/etapes\[\d+\]/, `etapes[${idx}]`));
        }
      });
    });
    CirculationUi.etapeIndex = $items.length;
  }
};
