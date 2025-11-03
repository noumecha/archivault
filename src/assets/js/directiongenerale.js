$(function () {
  initCRUD({
    moduleName: 'directiongenerale',
    baseUrl: '/directiongenerale/directiongenerales/',
    fetchUrl: '/directiongenerale/directiongenerales/all/',
    formSelector: '#directiongeneraleForm',
    modalSelector: '#create-directiongenerale-modal',
    formContainerSelector: '#directiongenerale-form-content',
    tableContainerSelector: '#directiongenerale-table-container',
    searchFormSelector: '#directiongenerale-search-form',
    searchInputSelector: '#search',
    clearBtnSelector: '#clearSearch'
  });
});
