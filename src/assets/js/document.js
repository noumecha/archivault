$(function () {

    // initialize modals for document
    loadModal('#create-document-modal', '#document-form-content', '/document/documents/') // for create or update
    submitForm('#documentForm', '/document/documents/', '/document/documents/all/') // save to db
    fetchDatas('/document/documents/all/', '#document-search-form', '#document-table-container') // initial fetching
    filteringDatas('#search', '/document/documents/all/', '#document-search-form', '#document-table-container') // filter documents dynamically
    clearSearch('#clearSearch', '#search') // clear search input

    // show sucess messge or error message 
    showMessage()
});
