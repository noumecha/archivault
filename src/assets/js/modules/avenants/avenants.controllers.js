import { AvenantService } from './avenants.services.js';
import { AvenantUI } from './avenants.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const AvenantController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'avenant',
      baseUrl: '/avenant/avenants/',
      fetchUrl: '/avenant/avenants/all/',
      formSelector: '#avenantForm',
      modalSelector: '#create-avenant-modal',
      formContainerSelector: '#avenant-form-content',
      tableContainerSelector: '#avenant-table-container',
      searchFormSelector: '#avenant-search-form',
      searchInputSelector: '#search,#id_bailleur',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(AvenantService, AvenantUI);
