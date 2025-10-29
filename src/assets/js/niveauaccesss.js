$(function () {
  initCRUD({
    moduleName: 'niveauaccess',
    baseUrl: '/niveauaccess/niveauaccesss/',
    fetchUrl: '/niveauaccess/niveauaccesss/all/',
    formSelector: '#niveauaccessForm',
    modalSelector: '#create-niveauaccess-modal',
    formContainerSelector: '#niveauaccess-form-content',
    tableContainerSelector: '#niveauaccess-table-container',
    searchFormSelector: '#niveauaccess-search-form',
    searchInputSelector: '#search',
    clearBtnSelector: '#clearSearch'
  });
});
