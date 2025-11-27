$(function () {
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
});
