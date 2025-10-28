/*$(function () {
  // initialize modals for cellule
  loadModal('#create-cellule-modal', '#cellule-form-content', '/cellule/cellules/'); // for create or update
  submitForm('#celluleForm', '/cellule/cellules/', '/cellule/cellules/all/'); // save to db
  fetchDatas('/cellule/cellules/all/', '#cellule-search-form', '#cellule-table-container'); // initial fetching
  filteringDatas('#search', '/cellule/cellules/all/', '#cellule-search-form', '#cellule-table-container'); // filter cellules dynamically
  clearSearch('#clearSearch', '#search'); // clear search input

  // show sucess messge or error message
  showMessage();
});*/

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
