/**
 * CRUD Helper
 * helpers/crud-helper.js
 * Initialize CRUD module dynamically
 * @param {Object} config
 */
import {
  loadModal,
  submitForm,
  fetchDatas,
  filteringDatas,
  refresh,
  clearSearch,
  showMessage,
  closeModal
} from './utils.js';
export function initCRUD(config) {
  const {
    moduleName,
    baseUrl,
    fetchUrl,
    formSelector,
    modalSelector,
    formContainerSelector,
    tableContainerSelector,
    searchFormSelector,
    searchInputSelector,
    clearBtnSelector
  } = config;
  // Initialize modal for create/update
  loadModal(modalSelector, formContainerSelector, baseUrl);
  // Submit form (create/update)
  submitForm(formSelector, baseUrl, fetchUrl, modalSelector);
  // Fetch initial data
  fetchDatas(fetchUrl, searchFormSelector, tableContainerSelector);
  filteringDatas(searchInputSelector, fetchUrl, searchFormSelector, tableContainerSelector);
  // Clear search field
  clearSearch(clearBtnSelector, searchInputSelector);
  // refresh
  refresh('#refresh-button', fetchUrl, searchFormSelector, tableContainerSelector);
  // Show success/error messages
  showMessage();
  // close modal
  closeModal(modalSelector);
}
