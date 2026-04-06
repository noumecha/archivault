import { TypeDocumentService } from './typedocuments.services.js';
import { TypeDocumentUI } from './typedocuments.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const TypeDocumentController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'typedocument',
      baseUrl: '/typedocument/typedocuments/',
      fetchUrl: '/typedocument/typedocuments/all/',
      formSelector: '#typedocumentForm',
      modalSelector: '#create-typedocument-modal',
      formContainerSelector: '#typedocument-form-content',
      tableContainerSelector: '#typedocument-table-container',
      searchFormSelector: '#typedocument-search-form',
      searchInputSelector: '#search',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(TypeDocumentService, TypeDocumentUI);
