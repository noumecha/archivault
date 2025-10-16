$(function () {
  console.log('works');
  // initialize modals for niveauaccess
  loadModal('#create-niveauaccess-modal', '#niveauaccess-form-content', '/niveauaccess/niveauaccesss/'); // for create or update
  submitForm('#niveauaccessForm', '/niveauaccess/niveauaccesss/', '/niveauaccess/niveauaccesss/all/'); // save to db
  fetchDatas('/niveauaccess/niveauaccesss/all/', '#niveauaccess-search-form', '#niveauaccess-table-container'); // initial fetching
  filteringDatas(
    '#search',
    '/niveauaccess/niveauaccesss/all/',
    '#niveauaccess-search-form',
    '#niveauaccess-table-container'
  ); // filter niveauaccesss dynamically
  clearSearch('#clearSearch', '#search'); // clear search input

  // show sucess messge or error message
  showMessage();
});
