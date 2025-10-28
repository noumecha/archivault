$(function () {
  initCRUD({
    moduleName: 'division',
    baseUrl: '/division/divisions/',
    fetchUrl: '/division/divisions/all/',
    formSelector: '#divisionForm',
    modalSelector: '#create-division-modal',
    formContainerSelector: '#division-form-content',
    tableContainerSelector: '#division-table-container',
    searchFormSelector: '#division-search-form',
    searchInputSelector: '#search',
    clearBtnSelector: '#clearSearch'
  });
});
