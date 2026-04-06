import { UserService } from './users.services.js';
import { UserUi } from './users.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const UserController = (function (Service, UI) {
  function init() {
    // Initialize user-related functionalities here
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
    /* For example, you can fetch and render the user list on page load
    Service.fetchAll().then(data => {
      UI.renderList('#user-table-container', data);
    });*/
  }

  return { init };
})(UserService, UserUi);
