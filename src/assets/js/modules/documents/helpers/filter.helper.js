// modules/documents/helpers/filter.helper.js
export const FilterHelper = {
  typeMatrix: {},
  sousTypeMatrix: {},
  themeMatrix: {},

  // 🟢 Objets pour stocker le HTML initial complet de chaque select (Filtres et Modals)
  backups: {},

  init() {
    const typeEl = document.getElementById('type-cellule-matrix');
    const sousTypeEl = document.getElementById('soustype-type-matrix');
    const themeEl = document.getElementById('theme-cellule-matrix');

    if (typeEl) this.typeMatrix = JSON.parse(typeEl.textContent);
    if (sousTypeEl) this.sousTypeMatrix = JSON.parse(sousTypeEl.textContent);
    if (themeEl) this.themeMatrix = JSON.parse(themeEl.textContent);

    // 🟢 On effectue une sauvegarde à froid du DOM initial complet
    this.createBackup('#id_type_document');
    this.createBackup('#id_sous_type');
    this.createBackup('#id_theme');

    this.createBackup('#create-document-modal #type_document');
    this.createBackup('#create-document-modal #sous_type');
    this.createBackup('#create-document-modal #theme');
  },

  createBackup(selector) {
    const $el = $(selector);
    if ($el.length) {
      // On clone toutes les options d'origine pour pouvoir les réinjecter à la demande
      this.backups[selector] = $el.find('option').clone();
    }
  },

  /**
   * Restaure les options initiales d'un select avant application d'un nouveau filtre
   */
  restoreBackup(selector) {
    const $el = $(selector);
    if ($el.length && this.backups[selector]) {
      const currentValue = $el.val(); // Conserve la sélection courante si valide
      $el.empty().append(this.backups[selector].clone());
      $el.val(currentValue);
    }
  },

  /**
   * Filtre les thèmes et les types de documents en fonction de la cellule sélectionnée
   */
  filterByCellule(celluleId, typeSelectSelector, themeSelectSelector) {
    // 1. 🟢 On restaure d'abord l'état d'origine complet (Règle le problème de disparition)
    this.restoreBackup(typeSelectSelector);
    this.restoreBackup(themeSelectSelector);

    const $typeSelect = $(typeSelectSelector);
    const $themeSelect = $(themeSelectSelector);

    // 2. Filtrage des Types de Documents
    if ($typeSelect.length) {
      $typeSelect.find('option').each(function () {
        const val = this.value;
        if (!val) return; // Ignore le placeholder "-- Sélectionner --"

        const typeData = FilterHelper.typeMatrix[val];
        // Si une cellule est cochée ET que le type appartient à une AUTRE cellule -> on le retire
        if (celluleId && typeData && typeData.cellule_id !== '' && typeData.cellule_id !== celluleId) {
          $(this).remove();
        }
      });
      $typeSelect.trigger('change.select2');
    }

    // 3. Filtrage des Thèmes
    if ($themeSelect.length) {
      $themeSelect.find('option').each(function () {
        const val = this.value;
        if (!val) return;

        const themeData = FilterHelper.themeMatrix[val];
        if (celluleId && themeData && themeData.cellule_id !== '' && themeData.cellule_id !== celluleId) {
          $(this).remove();
        }
      });
      $themeSelect.trigger('change.select2');
    }
  },

  /**
   * Filtre les sous-types de documents en fonction du type sélectionné
   */
  filterBySpecification(typeId, sousTypeSelector) {
    // 1. 🟢 On restaure l'état complet
    this.restoreBackup(sousTypeSelector);

    const $sousTypeSelect = $(sousTypeSelector);
    if (!$sousTypeSelect.length) return;

    // 2. Application du filtre
    $sousTypeSelect.find('option').each(function () {
      const val = this.value;
      if (!val) return;

      const sousTypeData = FilterHelper.sousTypeMatrix[val];
      if (typeId && sousTypeData && sousTypeData.type_id !== typeId) {
        $(this).remove();
      }
    });

    $sousTypeSelect.trigger('change.select2');
  },

  /**
   * Réinitialise complètement les filtres d'un conteneur vers l'état d'origine globale
   */
  resetFilters(containerSelector) {
    if (containerSelector === '#document-search-form') {
      this.restoreBackup('#id_type_document');
      this.restoreBackup('#id_sous_type');
      this.restoreBackup('#id_theme');
      $('#id_cellule, #id_type_document, #id_sous_type, #id_theme').val('').trigger('change.select2');
    } else {
      this.restoreBackup('#create-document-modal #type_document');
      this.restoreBackup('#create-document-modal #sous_type');
      this.restoreBackup('#create-document-modal #theme');
      $(
        '#create-document-modal #cellule, #create-document-modal #type_document, #create-document-modal #sous_type, #create-document-modal #theme'
      )
        .val('')
        .trigger('change.select2');
    }
  }
};
