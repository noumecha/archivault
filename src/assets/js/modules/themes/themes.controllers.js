import { ThemeService } from './themes.services.js';
import { ThemeUI } from './themes.ui.js';
import { initCRUD } from '../../helpers/crud-helper.js';

export const ThemeController = (function (Service, UI) {
  function init() {
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
  }

  return { init };
})(ThemeService, ThemeUI);
