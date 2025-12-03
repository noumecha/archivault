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
    searchInputSelector: '#search,#id_role,#id_cellule',
    clearBtnSelector: '#clearSearch'
  });
  /*/ URLs (assurez-vous que ces noms de routes sont corrects dans vos urls.py)
  const listUrl = '/utilisateurs/list/'; // URL pour lister les utilisateurs
  const formUrl = '/utilisateurs/'; // URL de base pour le formulaire (création/édition)

  // Conteneurs
  const tableContainer = '#utilisateur-table-container';
  const formContainer = '#utilisateur-form-content';
  const searchForm = '#utilisateur-search-form';
  const modalId = '#create-utilisateur-modal';

  // --- Initialisation de la page ---

  // 1. Charger la liste des utilisateurs au chargement de la page
  fetchDatas(listUrl, searchForm, tableContainer);

  // 2. Gérer les filtres et la recherche
  filteringDatas(searchForm + ' input, ' + searchForm + ' select', listUrl, searchForm, tableContainer);
  refresh('#refresh-button', listUrl, searchForm, tableContainer);
  clearSearch('#clearSearch', '#search');*/
});
