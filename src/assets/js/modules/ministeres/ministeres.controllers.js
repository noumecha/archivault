import { MinistereService } from './ministeres.services.js';
import { MinistereUI } from './ministeres.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const MinistereController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'ministere',
      baseUrl: '/ministere/ministeres/',
      fetchUrl: '/ministere/ministeres/all/',
      formSelector: '#ministereForm',
      modalSelector: '#create-ministere-modal',
      formContainerSelector: '#ministere-form-content',
      tableContainerSelector: '#ministere-table-container',
      searchFormSelector: '#ministere-search-form',
      searchInputSelector: '#search',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(MinistereService, MinistereUI);
