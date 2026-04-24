// helpers/utils.js

// standard function to reset form via dom or via jquery
function resetForm(formSelector) {
  const form = $(formSelector);
  if (form.length) {
    form[0].reset();
  } else {
    console.warn(`Form with selector "${formSelector}" not found.`);
  }
}

// function to set select2 on element of type select
function setSelect2(selector, placeholder, modalId) {
  if ($(selector).is('select')) {
    $(selector).select2({
      placeholder: placeholder,
      allowClear: true,
      dropdownParent: $(modalId)
    });
  }
}

// set the success message after form submission is successful
function setMessage(msg, id) {
  const msgBlock = $(id);
  msgBlock.stop(true, true).empty();
  if (Array.isArray(msg)) {
    const list = $('<ul></ul>');
    msg.forEach(m => list.append($('<li></li>').text(m.key + ': ' + m.value)));
    msgBlock.append(list);
  } else {
    msgBlock.append($('<p class="text-center mb-0"></p>').text(msg));
  }
  msgBlock.fadeIn().css('display', 'block');
  setTimeout(() => msgBlock.fadeOut(), 7000);
}

// form modal form inside another form
function ajaxModal(modalId, formnContainerId, formId, fetchUrl, selectItemId = null) {
  const modal = $(modalId);
  const formContainer = $(formnContainerId);
  const selectContainer = $(selectItemId);
  // Ouvrir le modal et charger le formulaire
  $(document).on('click', '[data-bs-target="' + modalId + '"]', function () {
    $.get(fetchUrl, function (data) {
      formContainer.html(data.html);
    });
  });
  // Gérer la soumission AJAX du formulaire
  $(document).on('submit', `${formId}`, function (e) {
    e.preventDefault();
    const form = $(this);
    const formData = form.serialize();
    // delete mask field that'are required but not visible
    $(form)
      .find(':input')
      .each(function () {
        if (!$(this).is(':visible')) {
          $(this).prop('required', false);
        }
      });
    // send ajax request
    $.ajax({
      url: fetchUrl,
      type: 'POST',
      data: formData,
      success: function (data) {
        if (data.success) {
          $(selectContainer).append(
            $('<option>', {
              value: data.id,
              text: data.text,
              selected: true
            })
          );
          $(formId).closest('form')[0].reset();
          id = '#form-success-' + modalId.replace('#', '');
          showAlertMessage(data.message, id);
        } else {
          id = '#form-error-' + modalId.replace('#', '');
          showAlertMessage(data.errors, id);
        }
      }
    });
  });
}

// loader functions
function startLoader(loaderId) {
  $(loaderId).removeClass('d-none');
}

function closeLoader(loaderId) {
  $(loaderId).addClass('d-none');
}

// function to load modal content
function loadModal(modalId, formContainer, baseUrl) {
  const formContent = $(formContainer);
  $(document).on('click', `[data-bs-target="${modalId}"]`, function (e) {
    e.preventDefault();
    let url = baseUrl;
    action = $(this).data('action');
    const id = $(this).data('id');
    btn = $('#save-btn');
    updateId = $('#update-id');
    btn.removeClass('btn-outline-primary btn-outline-success');
    if (action === 'update') {
      url = url + 'edit/' + id;
      updateId.val(id);
      btn.text('Mettre à jour');
      btn.addClass('btn-outline-success btn-outline-success');
    } else {
      url = url + 'form/';
      // Vérifier si on est dans un contexte de gestion de cellule
      const celluleId = $(this).data('cellule-id');
      console.log('cellule id', celluleId);
      btn.text('Enregistrer');
      btn.addClass('btn-outline-primary btn-outline-primary');
    }
    console.log('final url', url);
    console.log('id: ', id);
    $.get(url, function (data) {
      formContent.html(data.html);
    });
  });
}

// when the modal is closed set id to null
function closeModal(modalId) {
  $(document).on('hidden.bs.modal', modalId, function () {
    x = $('#update-id').val('');
    console.log('modal closed with the id : ', x.val());
  });
}

// clearing search form
function clearSearch(clearButton, searchInput) {
  $(clearButton).on('click', function () {
    $(searchInput).val('').trigger('change');
  });
}

// function for filter actualites dynamically with filters
function filteringDatas(searchInputSelector, url, formId, containerId) {
  $(searchInputSelector).on('change keyup', function (e) {
    e.preventDefault();
    // clear any previous timeout
    clearTimeout($(this).data('timer'));
    $(this).data('timer', setTimeout(fetchDatas(url, formId, containerId), 500));
  });
}

// when refresh run fetchDatas function
function refresh(refreshBtn, url, formId, containerId) {
  $(refreshBtn).on('click', function () {
    fetchDatas(url, formId, containerId);
  });
}

function fetchDatas(url, formId = null, containerId) {
  const formData = formId ? $(formId).serialize() : '';
  const table_container = $('#data-table');
  startLoader($('#table-loader'));
  table_container.hide();
  $.ajax({
    url: url,
    data: formData,
    type: 'GET',
    beforeSend: function () {
      closeLoader('#table-loader');
    },
    success: function (data) {
      if (data.success) {
        $(containerId).html(data.html);
      } else {
        console.error('Error occurred while fetching data : ', data.message);
      }
    },
    error: function (xhr, status, error) {
      console.error('AJAX Error:', error);
    },
    complete: function () {
      closeLoader('#table-loader');
      table_container.show();
    }
  });
}

// function to handle form submission
function submitForm(formId, baseUrl, fetchUrl, modalId = null) {
  $(document).on('submit', formId, function (e) {
    e.preventDefault();
    let url = baseUrl;
    const form = $(this);
    const list = $(this).data('list-id');
    const listId = $('#' + list);
    let formData;
    let ajaxOptions = {};
    // getting input of type file
    const fileInput = form.find('input[type="file"]');
    if (fileInput.length > 0 && fileInput[0].files.length > 0) {
      formData = new FormData(form[0]);
      ajaxOptions = {
        processData: false,
        contentType: false
      };
    } else {
      formData = form.serialize();
    }
    console.log('formdata : ', formData);
    const saveUrl = $('#save-btn').text() === 'Mettre à jour' ? url + 'update/' : url;
    const updateId = $('#update-id').val();
    // Send AJAX request
    $.ajax(
      Object.assign(
        {
          url: saveUrl + (updateId ? updateId : ''),
          type: 'POST',
          data: formData,
          success: function (data) {
            if (data.success) {
              if (listId && listId.length && data.data) {
                listId.append($('<option>', { value: data.data.id, text: data.data.text, selected: true }));
                const successId = form.find(`[data-success-id]`);
                showAlertMessage(data.message, successId);
                const modalInstance = bootstrap.Modal.getInstance(document.querySelector(modalId));
                modalInstance.hide();
              } else {
                showAlertMessage(data.message, '#form-success');
                form.closest('form')[0].reset();
              }
            } else {
              console.error('Error occurred on submit : ', data.message);
              const errorId = form.find(`[data-error-id]`);
              showAlertMessage(data.errors, errorId);
              showAlertMessage(data.errors, '#form-error');
              console.log('data : ', data);
            }
          }
        },
        ajaxOptions
      )
    );
    $('#update-id').val('');
  });
}

// set the success message after form submission is successful
function showAlertMessage(msg, id, loader = null) {
  const msgBlock = $(id);
  msgBlock.stop(true, true).empty();
  if (typeof msg === 'object' && !Array.isArray(msg)) {
    // Handle JSON object with fields and arrays of messages
    const list = $('<ul></ul>');
    Object.keys(msg).forEach(key => {
      msg[key].forEach(error => {
        if (key === '__all__') {
          list.append($('<li></li>').text(error)); // Don't show the '__all__' key
        } else {
          list.append($('<li></li>').text(`${key}: ${error.message || error}`));
        }
      });
    });
    msgBlock.append(list);
  } else {
    // Handle string messages
    msgBlock.append($('<p class="text-center mb-0"></p>').text(msg));
  }

  if (loader) {
    startLoader(loader);
    setTimeout(() => closeLoader(loader), 5000);
  }
  msgBlock.fadeIn().css('display', 'block');
  setTimeout(() => msgBlock.fadeOut(), 5000);
}

// show message
function showMessage(container = $('#message-show')) {
  console.log('container ', container);
  container.fadeIn().css('display', 'block');
  setTimeout(() => container.fadeOut(), 5000);
}

// function to toogle visibility and required attribute of fields in form base on another field value
function setVisible(mainSelector, targetSelector = null, valueToShow = null) {
  // on change
  if (mainSelector) {
    $(document).on('change', mainSelector, function () {
      const selectedValue = $(this).val();
      if (selectedValue === valueToShow) {
        $(targetSelector).closest('.form-group').show();
        $(targetSelector).prop('required', true);
      } else {
        $(targetSelector).closest('.form-group').hide();
        $(targetSelector).prop('required', false);
        $(targetSelector).val('').trigger('change');
      }
    });
  } else {
    // hide all required field that are in a form-group that is hidden
    $('form')
      .find(':input')
      .each(function () {
        if (!$(this).is(':visible')) {
          $(this).prop('required', false);
        }
      });
  }
}

function toogleFormset(selectElement, value = null, formsetToShow, formsetToHide) {
  if (selectElement) {
    $(document).on('change', selectElement, function () {
      const selectedValue = $(this).val();
      if (selectedValue === value) {
        $(formsetToShow).show();
        $(formsetToHide).hide();
      } else if (selectedValue === '1' || selectedValue === '2') {
        // If the value is the other specific value (1 or 2), hide the opposite formset
        $(formsetToShow).hide();
        $(formsetToHide).show();
      } else {
        // If the value is neither "1" nor "2", show both formsets
        $(formsetToShow).show();
        $(formsetToHide).show();
      }
    });

    // Trigger the change event on page load to handle initial state
    $(selectElement).trigger('change');
  } else {
    // If no selectElement is provided, show both formsets by default
    $(formsetToShow).show();
    $(formsetToHide).show();
  }
}

// function disabledCSS
function disabledCSS(el) {
  el.css({
    'background-color': '#e9ecef',
    'pointer-events': 'none',
    opacity: '1'
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// reusable toogleBulk Button function
function toggleBulkButton(selectCounterSelector, bulkActionsContainerSelector) {
  const selectedCount = $(selectCounterSelector).length;
  if (selectedCount > 0) {
    $(bulkActionsContainerSelector).removeClass('d-none');
    $(`${selectCounterSelector}, #selected-count`).text(selectedCount);
  } else {
    $(bulkActionsContainerSelector).addClass('d-none');
  }
}

// reusable function for showing toast base on his id , message and type (success, error, info) with a timeout
function showToast(toastId = '#toast-container', message, type = 'info', delay = 5000) {
  const $toastEl = $(toastId);
  const $toastBody = $toastEl.find('.toast-body');

  $toastBody.text(message);
  $toastEl.removeClass('bg-success bg-danger bg-info').addClass(`bg-${type}`);

  const toast = new bootstrap.Toast($toastEl[0], { delay: delay });
  toast.show();
}

// export
export {
  showMessage,
  showAlertMessage,
  setMessage,
  setSelect2,
  ajaxModal,
  loadModal,
  closeModal,
  clearSearch,
  filteringDatas,
  refresh,
  fetchDatas,
  submitForm,
  setVisible,
  toogleFormset,
  disabledCSS,
  getCookie,
  startLoader,
  closeLoader,
  toggleBulkButton,
  resetForm,
  showToast
};
