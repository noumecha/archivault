// helpers/utils.js

// Extraction sécurisée des variables injectées par Django
const userIdEl = document.getElementById('django-user-id');
const userRoleEl = document.getElementById('django-user-role');

if (userIdEl) {
  window.CURRENT_USER_ID = JSON.parse(userIdEl.textContent);
}
if (userRoleEl) {
  window.CURRENT_USER_ROLE = JSON.parse(userRoleEl.textContent);
}

/**
 * Gère le rendu universel de la pagination et des informations de compteurs
 * pour les listes interfacées avec DRF.
 * Affiche les boutons de pagination, les numéros de page, et les informations sur le nombre total d'éléments et la plage affichée.
 * Permet une expérience utilisateur cohérente et informative lors de la navigation dans les listes paginées.
 * @param {*} data - { count, page_size, current_page, next, previous }
 * @param {*} containerSelector - sélecteur du conteneur où les boutons de pagination seront rendus
 * @param {*} infoSelector - sélecteur du conteneur où les informations de compteurs seront affichées
 */
function renderPagination(data, containerSelector, infoSelector) {
  const $container = $(containerSelector);
  const $info = $(infoSelector);
  $container.empty();
  $info.empty();

  if (!data || !data.count || data.count === 0) return;

  const pageSize = data.page_size || 10;
  const totalPages = Math.ceil(data.count / pageSize);
  const currentPage = data.current_page || 1;

  const startEntry = (currentPage - 1) * pageSize + 1;
  const endEntry = Math.min(currentPage * pageSize, data.count);
  $info.text(`Affichage de ${startEntry} à ${endEntry} sur ${data.count} éléments`);

  if (totalPages <= 1) return;

  let html = `
    <li class="page-item ${!data.previous ? 'disabled' : ''}">
      <a class="page-link" href="#" data-page="${currentPage - 1}"><i class="ri-arrow-left-s-line"></i></a>
    </li>`;

  const delta = 1;
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
      html += `
        <li class="page-item ${currentPage === i ? 'active' : ''}">
          <a class="page-link" href="#" data-page="${i}">${i}</a>
        </li>`;
    } else if (i === currentPage - delta - 1 || i === currentPage + delta + 1) {
      html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
    }
  }

  html += `
    <li class="page-item ${!data.next ? 'disabled' : ''}">
      <a class="page-link" href="#" data-page="${currentPage + 1}"><i class="ri-arrow-right-s-line"></i></a>
    </li>`;

  $container.html(html);
}

/**
 * Réinitialise un formulaire en utilisant jQuery et synchronise Select2.
 * @param {*} formSelector
 */
function resetForm(formSelector) {
  const $form = $(formSelector);
  if ($form.length) {
    $form[0].reset();
    if ($.fn.select2) {
      $form.find('select.select2-hidden-accessible').val(null).trigger('change.select2');
    }
  } else {
    console.warn(`Form with selector "${formSelector}" not found.`);
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

/**
 * Permet de gérer l'ouverture d'un modal avec un formulaire chargé dynamiquement à partir d'une URL, et la soumission de ce formulaire via AJAX. Utile pour les modals de création ou d'édition qui doivent être réutilisés avec des contenus différents.
 * @param {*} modalId - ID du modal à ouvrir
 * @param {*} formnContainerId - ID du conteneur où le formulaire sera injecté
 * @param {*} formId - ID du formulaire à soumettre
 * @param {*} fetchUrl - URL pour charger le formulaire et pour soumettre les données
 * @param {*} selectItemId - ID d'un élément select à mettre à jour après la soumission (optionnel)
 */
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

/**
 * Permet de montrer un loader en supprimant la classe 'd-none' de l'élément spécifié. Utile pour indiquer le début d'un processus de chargement ou d'une action asynchrone, en affichant un loader visuel pendant le traitement.
 * @param {*} loaderId
 */
function startLoader(loaderId) {
  $(loaderId).removeClass('d-none');
}

/**
 * Permet de cacher un loader en ajoutant la classe 'd-none' à l'élément spécifié. Utile pour indiquer la fin d'un processus de chargement ou d'une action asynchrone, en masquant le loader qui était affiché pendant le traitement.
 * @param {*} loaderId
 */
function closeLoader(loaderId) {
  $(loaderId).addClass('d-none');
}

/**
 * Permet de charger dynamiquement le contenu d'un modal à partir d'une URL, en fonction de l'action (création ou mise à jour) et des données associées. Gère également la configuration du bouton de sauvegarde et la réinitialisation du champ d'identifiant pour les mises à jour.
 * Utile pour les modals de formulaire qui doivent être réutilisés pour créer ou éditer des éléments, en assurant que le contenu et les actions sont adaptés à chaque contexte.
 * @param {*} modalId
 * @param {*} formContainer
 * @param {*} baseUrl
 */
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

/**
 * Permet de réinitialiser les champs d'un formulaire et de vider les messages d'erreur/succès associés à la fermeture d'un modal.
 * Utile pour s'assurer que le formulaire est propre à chaque ouverture du modal, en évitant que les données précédentes ou les messages d'erreur ne persistent.
 * @param {*} modalId
 */
function closeModal(modalId) {
  $(document).on('hidden.bs.modal', modalId, function () {
    x = $('#update-id').val('');
    console.log('modal closed with the id : ', x.val());
  });
}

/**
 * Permet de réinitialiser le champ de recherche et de déclencher l'événement de changement pour rafraîchir les résultats affichés.
 * @param {*} clearButton
 * @param {*} searchInput
 */
function clearSearch(clearButton, searchInput) {
  $(clearButton).on('click', function () {
    $(searchInput).val('').trigger('change');
  });
}

/**
 * Permet de filtrer les données d'une liste en fonction de l'entrée de recherche, avec un délai pour éviter les requêtes à chaque frappe.
 * Utilise la fonction fetchDatas pour récupérer les données filtrées à partir de l'API et les afficher dans le conteneur spécifié.
 * @param {*} searchInputSelector
 * @param {*} url
 * @param {*} formId
 * @param {*} containerId
 */
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

/**
 * Récupère les données à partir d'une URL et les affiche dans un conteneur spécifié.
 * @param {*} url
 * @param {*} formId
 * @param {*} containerId
 */
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

/**
 * Soumet un formulaire et gère la réponse. Permet de traiter à la fois les formulaires avec des champs de type file (en utilisant FormData) et les formulaires classiques (en utilisant serialize).
 * Affiche les messages de succès ou d'erreur dans des conteneurs spécifiques, et gère la fermeture du modal si nécessaire.
 * @param {*} formId
 * @param {*} baseUrl
 * @param {*} fetchUrl
 * @param {*} modalId
 */
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

/**
 * Formate une clé de champ d'erreur en un format plus lisible pour l'utilisateur, en gérant les clés imbriquées et les indices de tableaux.
 * Exemples :
 * - "etapes.0.titre_etape" → "Etapes → #1 → Titre Etape"
 * - "document" → "Document"
 * @param {*} path
 * @returns
 */
function formatFriendlyKey(path) {
  return path
    .split('.')
    .map(part => {
      if (!isNaN(part)) {
        return `#${parseInt(part) + 1}`;
      }
      return part.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    })
    .join(' → ');
}

/**
 * Fonction récursive pour parser les erreurs d'une réponse API et les afficher de manière lisible
 * dans une liste HTML. Gère les erreurs sous forme de string, d'objets ou de tableaux, avec un formatage clair des clés.
 * @param {*} errors
 * @param {*} list
 * @param {*} parentKey
 * @returns
 */
function parseErrors(errors, list, parentKey = '') {
  if (typeof errors === 'string') {
    const friendlyKey = formatFriendlyKey(parentKey);
    list.append($('<li></li>').text(friendlyKey ? `${friendlyKey}: ${errors}` : errors));
    return;
  }
  if (Array.isArray(errors)) {
    errors.forEach(error => {
      parseErrors(error, list, parentKey);
    });
    return;
  }
  if (typeof errors === 'object' && errors !== null) {
    Object.keys(errors).forEach(key => {
      const newKey = parentKey ? `${parentKey}.${key}` : key;
      parseErrors(errors[key], list, newKey);
    });
  }
}

/***
 * Affiche un message d'alerte dans un conteneur donné, avec gestion intelligente des erreurs
 * et option de loader. Le message peut être une string simple ou un objet d'erreurs complexe.
 * Le conteneur doit être prévu pour accueillir des messages (ex: div d'alerte dans un modal).
 * Le loader, s'il est fourni, sera affiché pendant 5 secondes pour indiquer un traitement en cours.
 * Les messages d'erreur complexes (objets ou tableaux) seront formatés de manière lisible pour l'utilisateur.
 * Les messages simples seront affichés tels quels.
 * Après affichage, le message disparaîtra automatiquement après 5 secondes.
 */
function showAlertMessage(msg, id, loader = null) {
  const msgBlock = $(id);
  msgBlock.stop(true, true).empty();
  const list = $('<ul></ul>');
  if (typeof msg === 'object' && msg !== null) {
    parseErrors(msg, list);
    msgBlock.append(list);
  } else {
    msgBlock.append($('<p class="text-center mb-0"></p>').text(msg));
  }
  if (loader) {
    startLoader(loader);
    setTimeout(() => {
      closeLoader(loader);
    }, 5000);
  }
  msgBlock.fadeIn().css('display', 'block');
  setTimeout(() => {
    msgBlock.fadeOut();
  }, 5000);
}

/**
 * Affiche un message dans un conteneur donné. Le message peut être une string ou un tableau de messages.
 * Le conteneur doit être prévu pour accueillir des messages (ex: div d'alerte dans un modal).
 * Le message disparaîtra automatiquement après 5 secondes.
 * @param {*} container
 */
function showMessage(container = $('#message-show')) {
  console.log('container ', container);
  container.fadeIn().css('display', 'block');
  setTimeout(() => container.fadeOut(), 5000);
}

/**
 * Permet de montrer ou cacher dynamiquement un champ de formulaire en fonction de la valeur sélectionnée dans un autre champ (ex: dropdown).
 * Utile pour les formulaires avec des champs conditionnels.
 * Le champ cible sera affiché et rendu requis uniquement lorsque la valeur sélectionnée correspond à celle spécifiée, sinon il sera caché et non requis.
 * @param {*} mainSelector
 * @param {*} targetSelector
 * @param {*} valueToShow
 */
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

/**
 * Récupère la valeur d'un cookie par son nom.
 * @param {*} name
 * @returns
 */
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

/**
 * Fonction reutilisatble pour le toogle check
 * @params selectCounterSelector, bulkActionsContainerSelector
 */
function toggleBulkButton(selectCounterSelector, bulkActionsContainerSelector) {
  const selectedCount = $(selectCounterSelector).length;
  if (selectedCount > 0) {
    $(bulkActionsContainerSelector).removeClass('d-none');
    $('#selected-count').text(selectedCount);
  } else {
    $(bulkActionsContainerSelector).addClass('d-none');
  }
}

/**
 * Affiche un toast de notification avec un message donné, un type de style (success, danger, info), et une durée d'affichage personnalisable.
 * Le toast doit être défini dans le HTML avec l'ID spécifié (par défaut #toast-container) et doit contenir un élément avec la classe .toast-body pour le message.
 * Exemple d'utilisation : showToast("Opération réussie", "success");
 * @param {*} message
 * @param {*} type
 * @param {*} toastId
 * @param {*} delay
 * @returns
 */
function showToast(message, type = 'info', toastId = '#toast-container', delay = 5000) {
  const $toastEl = $(toastId);
  if ($toastEl.length === 0) {
    console.error('Toast container non trouvé :', toastId);
    return;
  }
  const $toastBody = $toastEl.find('.toast-body');

  $toastBody.text(message);
  $toastEl.removeClass('bg-success bg-danger bg-info').addClass(`bg-${type}`);

  const toast = new bootstrap.Toast($toastEl[0], { delay: delay });
  toast.show();
}

/**
 *
 * @param {*} modalId
 * function for closing modals properly
 */
function closeBootstrapModal(modalId) {
  const modalElement = document.getElementById(modalId);
  const modalInstance = bootstrap.Modal.getInstance(modalElement);
  if (modalInstance) modalInstance.hide();
}

/**
 * function pour simuler la desactivation d'un élément
 * @param {*} selector
 */
function disableElement(selector) {
  const element = $(selector);
  if (element.length) {
    element.css({
      'pointer-events': 'none',
      'background-color': '#e9ecef',
      cursor: 'not-allowed'
    });
    element.attr('tabindex', '-1');
    element.trigger('change');
  }
}

/**
 * function pour simuler l'activation d'un élément
 * @param {*} selector
 */
function enableElement(selector) {
  const element = $(selector);
  if (element.length) {
    element.css({ 'pointer-events': '', 'background-color': '', cursor: 'default' });
  }
}

/**
 * fonction pour définir dynamiquement la valeur d'un champ select2, avec option de créer une nouvelle option si le texte est fourni. Permet de mettre à jour la sélection d'un select2 après une action AJAX, en ajoutant une nouvelle option au besoin et en déclenchant l'événement 'change' pour assurer que l'interface se mette à jour correctement.
 * Exemple d'utilisation : setSelect2Value('my-select', 'new_value', 'New Option');
 * @param {*} selectId
 * @param {*} value
 * @param {*} text
 * @returns
 */
function setSelect2Value(selectId, value, text = null) {
  if (!value) return;

  const $select = $(`#${selectId}`);
  if (!$select.length) return;

  // Si le texte est fourni, créer l'option
  if (text) {
    const option = new Option(text, value, true, true);
    $select.append(option);
  } else {
    $select.val(value);
  }

  $select.trigger('change');
}

/**
 * Initialise Select2 sur un élément de type select, avec un placeholder personnalisé et une configuration pour les modals Bootstrap.
 * Permet d'assurer que les dropdowns de Select2 s'affichent correctement à l'intérieur des modals, en utilisant l'option dropdownParent pour éviter les problèmes de z-index et de positionnement.
 * Exemple d'utilisation : setSelect2('.my-select', 'Choisissez une option', '#myModal');
 * @param {*} selector
 * @param {*} placeholder
 * @param {*} modalId
 */
function setSelect2(selector, placeholder, modalId) {
  if ($(selector).is('select')) {
    $(selector).select2({
      placeholder: placeholder,
      allowClear: true,
      dropdownParent: $(modalId)
    });
  }
}

/**
 * Initialise Select2 sur tous les éléments valides et visibles d'un conteneur
 * @param {*} container - sélecteur du conteneur dans lequel initialiser les champs Select2 (par défaut 'body' pour tout le document)
 */
export function initSelect2Fields(container = 'body') {
  if ($.fn.select2 && $.fn.select2.amd) {
    $.fn.select2.defaults.set('language', {
      noResults: function () {
        return 'Aucun résultat trouvé';
      },
      searching: function () {
        return 'Recherche en cours…';
      },
      removeAllItems: function () {
        return 'Tout supprimer';
      }
    });
  }
  $(container)
    .find('select')
    .filter(':visible')
    .not('.select2-hidden-accessible')
    .each(function () {
      const $select = $(this);
      const placeholder = $select.find('option:first').text() || 'Sélectionnez une option';
      const $parentModal = $select.closest('.modal');

      $select.select2({
        placeholder: placeholder,
        allowClear: true,
        dropdownParent: $parentModal.length ? $parentModal : null,
        width: '100%'
      });
    });
}

/**
 * Observe le DOM et les événements de Modals pour initialiser Select2 automatiquement
 */
export function watchAndInitSelect2() {
  initSelect2Fields('body');
  $(document).on('shown.bs.modal', '.modal', function () {
    const $modal = $(this);
    initSelect2Fields($modal);
  });
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.nodeType === 1) {
          const $node = $(node);
          if ($node.is('select') || $node.find('select').length > 0) {
            initSelect2Fields($node);
          }
        }
      });
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
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
  showToast,
  renderPagination,
  closeBootstrapModal,
  disableElement,
  enableElement
};
