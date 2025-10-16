$(function () {
  // initialize modals for soustypedocument
  loadModal('#create-soustypedocument-modal', '#soustypedocument-form-content', '/soustypedocument/soustypedocuments/'); // for create or update
  submitForm(
    '#soustypedocumentForm',
    '/soustypedocument/soustypedocuments/',
    '/soustypedocument/soustypedocuments/all/'
  ); // save to db
  fetchDatas(
    '/soustypedocument/soustypedocuments/all/',
    '#soustypedocument-search-form',
    '#soustypedocument-table-container'
  ); // initial fetching
  filteringDatas(
    '#search',
    '/soustypedocument/soustypedocuments/all/',
    '#soustypedocument-search-form',
    '#soustypedocument-table-container'
  ); // filter soustypedocuments dynamically
  clearSearch('#clearSearch', '#search'); // clear search input

  // show sucess messge or error message
  showMessage();
});
