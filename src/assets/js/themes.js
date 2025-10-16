$(function () {
  // initialize modals for theme
  loadModal('#create-theme-modal', '#theme-form-content', '/theme/themes/'); // for create or update
  submitForm('#themeForm', '/theme/themes/', '/theme/themes/all/'); // save to db
  fetchDatas('/theme/themes/all/', '#theme-search-form', '#theme-table-container'); // initial fetching
  filteringDatas('#search', '/theme/themes/all/', '#theme-search-form', '#theme-table-container'); // filter themes dynamically
  clearSearch('#clearSearch', '#search'); // clear search input

  // show sucess messge or error message
  showMessage();
});
