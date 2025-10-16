$(function () {
  // initialize modals for typedocument
  loadModal('#create-typedocument-modal', '#typedocument-form-content', '/typedocument/typedocuments/'); // for create or update
  submitForm('#typedocumentForm', '/typedocument/typedocuments/', '/typedocument/typedocuments/all/'); // save to db
  fetchDatas('/typedocument/typedocuments/all/', '#typedocument-search-form', '#typedocument-table-container'); // initial fetching
  filteringDatas(
    '#search',
    '/typedocument/typedocuments/all/',
    '#typedocument-search-form',
    '#typedocument-table-container'
  ); // filter typedocuments dynamically
  clearSearch('#clearSearch', '#search'); // clear search input

  // show sucess messge or error message
  showMessage();
});
