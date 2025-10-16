$(function () {
  const dropArea = document.getElementById('drop-area');
  const fileInput = document.getElementById('file-input');
  const browseBtn = document.getElementById('browse-btn');
  const previews = document.getElementById('previews');
  const uploadForm = document.getElementById('upload-form');

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    dropArea.addEventListener(evt, preventDefaults, false);
  });

  ['dragenter', 'dragover'].forEach(evt => {
    dropArea.addEventListener(evt, () => dropArea.classList.add('bg-light'), false);
  });
  ['dragleave', 'drop'].forEach(evt => {
    dropArea.addEventListener(evt, () => dropArea.classList.remove('bg-light'), false);
  });

  dropArea.addEventListener('drop', handleDrop, false);
  browseBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', handleFiles, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    fileInput.files = filesToDataTransfer(files).files; // set input.files
    handleFiles();
  }

  function filesToDataTransfer(files) {
    // utility to create a DataTransfer object for setting input.files
    const dt = new DataTransfer();
    for (let i = 0; i < files.length; i++) dt.items.add(files[i]);
    return dt;
  }

  function handleFiles() {
    previews.innerHTML = '';
    const files = fileInput.files;
    for (let i = 0; i < files.length; i++) {
      previewFile(files[i], i);
    }
  }

  function previewFile(file, i) {
    const col = document.createElement('div');
    col.className = 'col-3 mb-3';
    const card = document.createElement('div');
    card.className = 'card p-1 h-100';
    const body = document.createElement('div');
    body.className = 'text-center';
    // image preview if image
    if (file.type.startsWith('image/')) {
      const img = document.createElement('img');
      img.style.maxWidth = '100%';
      img.style.maxHeight = '120px';
      const reader = new FileReader();
      reader.onload = function (e) {
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
      body.appendChild(img);
    } else {
      // icon + filename
      const ext = file.name.split('.').pop().toUpperCase();
      const p = document.createElement('p');
      p.className = 'mt-2';
      p.innerHTML = `<strong>${ext}</strong><br><small>${file.name}</small>`;
      body.appendChild(p);
    }

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-sm btn-outline-danger w-100 mt-2';
    removeBtn.textContent = 'Supprimer';
    removeBtn.addEventListener('click', function () {
      removeFileAtIndex(i);
    });

    card.appendChild(body);
    card.appendChild(removeBtn);
    col.appendChild(card);
    previews.appendChild(col);
  }

  function removeFileAtIndex(index) {
    const dt = new DataTransfer();
    const files = fileInput.files;
    for (let i = 0; i < files.length; i++) {
      if (i === index) continue;
      dt.items.add(files[i]);
    }
    fileInput.files = dt.files;
    handleFiles();
  }

  // On submit, normal form submit; input[name=fichiers] already populated
  uploadForm.addEventListener('submit', function (e) {
    // leave default submit to server; but we can validate before
    if (!fileInput.files.length) {
      e.preventDefault();
      alert("Ajoutez au moins un fichier avant d'enregistrer.");
      return false;
    }
    // else default submit (multipart/form-data)
  });
});
