$(function () {
  initCRUD({
    moduleName: 'bailleur',
    baseUrl: '/bailleur/bailleurs/',
    fetchUrl: '/bailleur/bailleurs/all/',
    formSelector: '#bailleurForm',
    modalSelector: '#create-bailleur-modal',
    formContainerSelector: '#bailleur-form-content',
    tableContainerSelector: '#bailleur-table-container',
    searchFormSelector: '#bailleur-search-form',
    searchInputSelector: '#search',
    clearBtnSelector: '#clearSearch'
  });
});
