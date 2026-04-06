$(function () {
  /* ---------------------------------------------------------
    ELEMENTS
  --------------------------------------------------------- */
  const dropArea = $('#drop-area')[0];
  const fileInput = $('#file-input')[0];
  const browseBtn = $('#browse-btn');
  const previews = $('#previews')[0];
  const uploadForm = $('#upload-form');

  /* ---------------------------------------------------------
    HELPERS
  --------------------------------------------------------- */

  // Prevent default behavior for drag & drop
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  // Create a new DataTransfer object with given file list (used for add/remove)
  function buildFileList(exceptIndex = null) {
    const dt = new DataTransfer();
    Array.from(fileInput.files).forEach((file, idx) => {
      if (idx !== exceptIndex) dt.items.add(file);
    });
    return dt;
  }

  // Check if file is an image
  function isImage(file) {
    return file.type.startsWith('image/');
  }

  /* ---------------------------------------------------------
    DRAG & DROP HANDLERS
  --------------------------------------------------------- */

  // Add/remove highlight on drag
  const highlight = () => dropArea.classList.add('bg-light');
  const unhighlight = () => dropArea.classList.remove('bg-light');

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => dropArea.addEventListener(evt, preventDefaults));

  ['dragenter', 'dragover'].forEach(evt => dropArea.addEventListener(evt, highlight));

  ['dragleave', 'drop'].forEach(evt => dropArea.addEventListener(evt, unhighlight));

  // Handle dropped files
  dropArea.addEventListener('drop', e => {
    const dt = new DataTransfer();
    Array.from(e.dataTransfer.files).forEach(f => dt.items.add(f));
    fileInput.files = dt.files;
    renderPreviews();
  });

  /* ---------------------------------------------------------
    FILE INPUT EVENTS
  --------------------------------------------------------- */

  browseBtn.on('click', () => fileInput.click());
  fileInput.addEventListener('change', renderPreviews);

  /* ---------------------------------------------------------
    PREVIEW RENDERING
  --------------------------------------------------------- */

  function renderPreviews() {
    previews.innerHTML = '';

    Array.from(fileInput.files).forEach((file, index) => {
      previews.appendChild(buildPreviewCard(file, index));
    });
  }

  // Build a single preview card
  function buildPreviewCard(file, index) {
    const col = document.createElement('div');
    col.className = 'col-3 mb-3';

    const card = document.createElement('div');
    card.className = 'card p-1 h-100 text-center';

    const body = document.createElement('div');

    if (isImage(file)) {
      addImagePreview(file, body);
    } else {
      addFilePreview(file, body);
    }

    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn btn-sm btn-outline-danger w-100 mt-2';
    removeBtn.textContent = 'Supprimer';
    removeBtn.onclick = () => removeFile(index);

    card.append(body, removeBtn);
    col.appendChild(card);

    return col;
  }

  function addImagePreview(file, body) {
    const img = document.createElement('img');
    img.style.maxWidth = '100%';
    img.style.maxHeight = '120px';

    const reader = new FileReader();
    reader.onload = e => (img.src = e.target.result);
    reader.readAsDataURL(file);

    body.appendChild(img);
  }

  function addFilePreview(file, body) {
    const ext = file.name.split('.').pop().toUpperCase();
    body.innerHTML = `
      <p class="mt-2">
        <strong>${ext}</strong><br>
        <small>${file.name}</small>
      </p>
    `;
  }

  /* ---------------------------------------------------------
    REMOVE FILE
  --------------------------------------------------------- */

  function removeFile(index) {
    const newList = buildFileList(index);
    fileInput.files = newList.files;
    renderPreviews();
  }

  /* ---------------------------------------------------------
    FORM VALIDATION
  --------------------------------------------------------- */

  let conflictQueue = []; // { file, existingDoc }
  let uploadQueue = []; // files sans conflit
  let currentConflict = null; // conflit en cours

  uploadForm.on('submit', function (e) {
    e.preventDefault();

    const files = [...fileInput.files];
    if (!files.length) {
      showAlertMessage('Ajoutez au moins un fichier', '#form-error');
      return;
    }

    conflictQueue = [];
    uploadQueue = [];

    Promise.all(files.map(f => checkFileConflict(f))).then(() => {
      // Si aucun conflit → envoi direct
      if (conflictQueue.length === 0) {
        submitFinalForm();
      } else {
        // traiter le premier conflit
        showNextConflict();
      }
    });
  });

  function checkFileConflict(file) {
    return fetch(`/check-document/?filename=${encodeURIComponent(file.name)}`)
      .then(r => r.json())
      .then(data => {
        if (data.exists) {
          conflictQueue.push({
            file: file,
            existing: data
          });
        } else {
          uploadQueue.push(file);
        }
      });
  }

  function showNextConflict() {
    if (conflictQueue.length === 0) {
      submitFinalForm();
      return;
    }
    currentConflict = conflictQueue.shift();

    $('#dup-text').text(`Le document "${currentConflict.existing.titre}" existe déjà. Que souhaitez-vous faire ?`);

    $('#duplicateDocumentModal').modal('show');
  }

  let actions = []; // { file, action, documentId }
  $('#btn-version')
    .off()
    .on('click', function () {
      actions.push({
        file: currentConflict.file,
        action: 'version',
        documentId: currentConflict.existing.document_id
      });
      $('#duplicateDocumentModal').modal('hide');
      showNextConflict();
    });

  $('#btn-overwrite')
    .off()
    .on('click', function () {
      actions.push({
        file: currentConflict.file,
        action: 'overwrite',
        documentId: currentConflict.existing.document_id
      });
      $('#duplicateDocumentModal').modal('hide');
      showNextConflict();
    });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function resetForm(formId) {
    const $form = $(formId);
    if (!$form.length) return;
    $form[0].reset();
  }

  function resetUploadForm(formId) {
    resetForm(formId);

    $('#file-input').val('');
    $('#previews').empty();

    actions = [];
    uploadQueue = [];
    conflictQueue = [];
    currentConflict = null;
  }

  function submitFinalForm() {
    const formData = new FormData(uploadForm[0]);
    // ⚠️ Supprimer les fichiers auto-inclus par le FormData natif
    formData.delete('fichiers');

    // Fichiers sans conflit → action implicite "create"
    uploadQueue.forEach(f => {
      formData.append('fichiers', f);
    });

    // Fichiers avec conflit + action choisie
    actions.forEach(a => {
      formData.append('fichiers', a.file); // ← même nom
      formData.append(
        'actions[]',
        JSON.stringify({
          name: a.file.name,
          action: a.action,
          documentId: a.documentId
        })
      );
    });

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload/');
    xhr.withCredentials = true;
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

    xhr.upload.addEventListener('progress', function (e) {
      if (e.lengthComputable) {
        updateProgressBar((e.loaded / e.total) * 100);
      }
    });

    xhr.onload = function () {
      try {
        const data = JSON.parse(xhr.responseText);
        if (data.success) {
          showAlertMessage(data.message, '#form-success');
          resetUploadForm('#upload-form');
        } else {
          console.error('Erreur serveur:', data);
          showAlertMessage(JSON.stringify(data.errors || data.message || 'Erreur inconnue'), '#form-error');
        }
      } catch (err) {
        console.error('Erreur innatendue :', err);
        showAlertMessage('Erreur inattendue (voir console)', '#form-error');
      }
    };

    xhr.onerror = function () {
      showAlertMessage('Erreur réseau', '#form-error');
    };

    xhr.send(formData);
  }

  function updateProgressBar(percent) {
    const container = document.getElementById('progress-container');
    const bar = document.getElementById('upload-progress');

    container.style.display = 'block';
    bar.style.width = percent + '%';
    bar.innerText = Math.round(percent) + '%';

    // Masquer une fois terminé
    if (percent >= 100) {
      setTimeout(() => {
        container.style.display = 'none';
        bar.style.width = '0%';
      }, 1500);
    }
  }

  /* ---------------------------------------------------------
    DYNAMIC FILTERING: TYPE → SOUS-TYPE
  --------------------------------------------------------- */

  $(document).on('change', '#id_type_document', function () {
    const typeId = $(this).val();
    const sousType = $('#id_sous_type');

    sousType.empty().trigger('change');

    if (!typeId) return;

    $.ajax({
      url: '/soustypes/',
      data: { type_id: typeId },
      success: data => {
        sousType.append('<option value="">---------</option>');
        data.forEach(item => {
          sousType.append(new Option(item.text, item.id));
        });
        sousType.trigger('change');
      },
      error: err => console.error('Erreur chargement sous-types :', err)
    });
  });
});
