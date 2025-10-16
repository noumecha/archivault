$(function () {
    // initialize modals for utilisateur
    loadModal('#create-utilisateur-modal', '#utilisateur-form-content', '/utilisateur/utilisateurs/') // for create or update
    submitForm('#utilisateurForm', '/utilisateur/utilisateurs/', '/utilisateur/utilisateurs/all/') // save to db
    fetchDatas('/utilisateur/utilisateurs/all/', '#utilisateur-search-form', '#utilisateur-table-container') // initial fetching
    filteringDatas('#search', '/utilisateur/utilisateurs/all/', '#utilisateur-search-form', '#utilisateur-table-container') // filter utilisateurs dynamically
    clearSearch('#clearSearch', '#search') // clear search input

    // show sucess messge or error message 
    showMessage()
});
