import { BailleurService } from './bailleurs.services.js';
import { BailleurUI } from './bailleurs.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const BailleurController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'bailleur',
      baseUrl: '/bailleur/bailleurs/',
      fetchUrl: '/bailleur/bailleurs/all/',
      formSelector: '#bailleurForm',
      modalSelector: '#create-bailleur-modal',
      formContainerSelector: '#bailleur-form-content',
      tableContainerSelector: '#bailleur-table-container',
      searchFormSelector: '#bailleur-search-form',
      searchInputSelector: '#search',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(BailleurService, BailleurUI);
