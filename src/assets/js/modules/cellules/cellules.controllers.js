import { CelluleService } from './cellules.services.js';
import { CelluleUI } from './cellules.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const CelluleController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'cellule',
      baseUrl: '/cellule/cellules/',
      fetchUrl: '/cellule/cellules/all/',
      formSelector: '#celluleForm',
      modalSelector: '#create-cellule-modal',
      formContainerSelector: '#cellule-form-content',
      tableContainerSelector: '#cellule-table-container',
      searchFormSelector: '#cellule-search-form',
      searchInputSelector: '#search',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(CelluleService, CelluleUI);
