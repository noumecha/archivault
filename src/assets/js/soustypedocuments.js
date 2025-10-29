$(function () {
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
});
