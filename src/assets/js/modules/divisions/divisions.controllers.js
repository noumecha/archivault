import { DivisionService } from './divisions.services.js';
import { DivisionUI } from './divisions.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const DivisionController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'division',
      baseUrl: '/division/divisions/',
      fetchUrl: '/division/divisions/all/',
      formSelector: '#divisionForm',
      modalSelector: '#create-division-modal',
      formContainerSelector: '#division-form-content',
      tableContainerSelector: '#division-table-container',
      searchFormSelector: '#division-search-form',
      searchInputSelector: '#search',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(DivisionService, DivisionUI);
