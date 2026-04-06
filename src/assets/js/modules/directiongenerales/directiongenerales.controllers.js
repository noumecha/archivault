import { DirectionGeneraleService } from './directiongenerales.services.js';
import { DirectionGeneraleUI } from './directiongenerales.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const DirectionGeneraleController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'directiongenerale',
      baseUrl: '/directiongenerale/directiongenerales/',
      fetchUrl: '/directiongenerale/directiongenerales/all/',
      formSelector: '#directiongeneraleForm',
      modalSelector: '#create-directiongenerale-modal',
      formContainerSelector: '#directiongenerale-form-content',
      tableContainerSelector: '#directiongenerale-table-container',
      searchFormSelector: '#directiongenerale-search-form',
      searchInputSelector: '#search',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(DirectionGeneraleService, DirectionGeneraleUI);
