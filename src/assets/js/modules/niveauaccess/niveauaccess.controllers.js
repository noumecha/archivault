import { NiveauAccessService } from './niveauaccess.services.js';
import { NiveauAccessUI } from './niveauaccess.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const NiveauAccessController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'niveauaccess',
      baseUrl: '/niveauaccess/niveauaccesss/',
      fetchUrl: '/niveauaccess/niveauaccesss/all/',
      formSelector: '#niveauaccessForm',
      modalSelector: '#create-niveauaccess-modal',
      formContainerSelector: '#niveauaccess-form-content',
      tableContainerSelector: '#niveauaccess-table-container',
      searchFormSelector: '#niveauaccess-search-form',
      searchInputSelector: '#search',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(NiveauAccessService, NiveauAccessUI);
