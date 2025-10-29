$(function () {
  initCRUD({
    moduleName: 'theme',
    baseUrl: '/theme/themes/',
    fetchUrl: '/theme/themes/all/',
    formSelector: '#themeForm',
    modalSelector: '#create-theme-modal',
    formContainerSelector: '#theme-form-content',
    tableContainerSelector: '#theme-table-container',
    searchFormSelector: '#theme-search-form',
    searchInputSelector: '#search',
    clearBtnSelector: '#clearSearch'
  });
});
