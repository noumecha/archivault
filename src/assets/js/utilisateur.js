/*$(function () {
  // initialize modals for utilisateur
  loadModal('#create-utilisateur-modal', '#utilisateur-form-content', '/utilisateur/utilisateurs/'); // for create or update
  submitForm('#utilisateurForm', '/utilisateur/utilisateurs/', '/utilisateur/utilisateurs/all/'); // save to db
  fetchDatas('/utilisateur/utilisateurs/all/', '#utilisateur-search-form', '#utilisateur-table-container'); // initial fetching
  filteringDatas(
    '#search',
    '/utilisateur/utilisateurs/all/',
    '#utilisateur-search-form',
    '#utilisateur-table-container'
  ); // filter utilisateurs dynamically
  clearSearch('#clearSearch', '#search'); // clear search input

  // show sucess messge or error message
  showMessage();
});*/

$(function () {
  initCRUD({
    moduleName: 'utilisateur',
    baseUrl: '/utilisateur/utilisateurs/',
    fetchUrl: '/utilisateur/utilisateurs/all/',
    formSelector: '#utilisateurForm',
    modalSelector: '#create-utilisateur-modal',
    formContainerSelector: '#utilisateur-form-content',
    tableContainerSelector: '#utilisateur-table-container',
    searchFormSelector: '#utilisateur-search-form',
    searchInputSelector: '#search,#id-role,#id-cellule',
    clearBtnSelector: '#clearSearch'
  });
});
