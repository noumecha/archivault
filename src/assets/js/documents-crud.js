$(function () {
  initCRUD({
    moduleName: 'document',
    baseUrl: '/document/documents/',
    fetchUrl: '/document/documents/all/',
    formSelector: '#documentForm',
    modalSelector: '#create-document-modal',
    formContainerSelector: '#document-form-content',
    tableContainerSelector: '#document-table-container',
    searchFormSelector: '#document-search-form',
    searchInputSelector: '#search,#id_type_document,#id_sous_type,#id_etat,#id_profil_document,#id_theme,#id_bailleur',
    clearBtnSelector: '#clearSearch'
  });
});
