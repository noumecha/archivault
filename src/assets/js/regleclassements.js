$(function () {
  console.log('works');
  // initialize modals for regleclassement
  loadModal('#create-regleclassement-modal', '#regleclassement-form-content', '/regleclassement/regleclassements/'); // for create or update
  submitForm('#regleclassementForm', '/regleclassement/regleclassements/', '/regleclassement/regleclassements/all/'); // save to db
  fetchDatas(
    '/regleclassement/regleclassements/all/',
    '#regleclassement-search-form',
    '#regleclassement-table-container'
  ); // initial fetching
  filteringDatas(
    '#search',
    '/regleclassement/regleclassements/all/',
    '#regleclassement-search-form',
    '#regleclassement-table-container'
  ); // filter regleclassements dynamically
  clearSearch('#clearSearch', '#search'); // clear search input

  // show sucess messge or error message
  showMessage();
});
