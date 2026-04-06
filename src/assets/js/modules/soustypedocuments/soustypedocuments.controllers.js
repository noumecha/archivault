import { SousTypeDocumentSerivce } from './soustypedocuments.services.js';
import { SousTypeDocumentUI } from './soustypedocuments.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const SousTypeDocumentController = (function (Service, UI) {
  function init() {
    initCRUD({
      moduleName: 'soustypedocument',
      baseUrl: '/soustypedocument/soustypedocuments/',
      fetchUrl: '/soustypedocument/soustypedocuments/all/',
      formSelector: '#soustypedocumentForm',
      modalSelector: '#create-soustypedocument-modal',
      formContainerSelector: '#soustypedocument-form-content',
      tableContainerSelector: '#soustypedocument-table-container',
      searchFormSelector: '#soustypedocument-search-form',
      searchInputSelector: '#search,#id_type_document',
      clearBtnSelector: '#clearSearch'
    });
  }

  return { init };
})(SousTypeDocumentSerivce, SousTypeDocumentUI);
