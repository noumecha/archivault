$(function () {
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
});
