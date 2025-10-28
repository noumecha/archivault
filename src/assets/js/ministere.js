$(function () {
  initCRUD({
    moduleName: 'ministere',
    baseUrl: '/ministere/ministeres/',
    fetchUrl: '/ministere/ministeres/all/',
    formSelector: '#ministereForm',
    modalSelector: '#create-ministere-modal',
    formContainerSelector: '#ministere-form-content',
    tableContainerSelector: '#ministere-table-container',
    searchFormSelector: '#ministere-search-form',
    searchInputSelector: '#search',
    clearBtnSelector: '#clearSearch'
  });
});
