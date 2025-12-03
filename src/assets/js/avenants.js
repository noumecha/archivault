$(function () {
  initCRUD({
    moduleName: 'avenant',
    baseUrl: '/avenant/avenants/',
    fetchUrl: '/avenant/avenants/all/',
    formSelector: '#avenantForm',
    modalSelector: '#create-avenant-modal',
    formContainerSelector: '#avenant-form-content',
    tableContainerSelector: '#avenant-table-container',
    searchFormSelector: '#avenant-search-form',
    searchInputSelector: '#search,#id_bailleur',
    clearBtnSelector: '#clearSearch'
  });
});
