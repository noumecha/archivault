// modules/documents/helpers/drag-drop.helper.js
export const DragDropHelper = {
  init(controller) {
    const dropArea = $('#drop-area');
    const fileInput = $('#file-input');

    dropArea.on('click', e => {
      if (e.target !== fileInput[0]) fileInput.click();
    });

    fileInput.on('click', e => e.stopPropagation());

    dropArea.on('dragover', e => {
      e.preventDefault();
      dropArea.addClass('bg-light border-primary');
    });

    dropArea.on('dragleave drop', () => dropArea.removeClass('bg-light border-primary'));

    dropArea.on('drop', e => {
      e.preventDefault();
      const newFiles = e.originalEvent.dataTransfer.files;
      this.handleFileSelection(newFiles, controller);
    });

    fileInput.on('change', e => {
      this.handleFileSelection(e.target.files, controller);
      fileInput.val('');
    });
  },

  handleFileSelection(files, controller) {
    Array.from(files).forEach(file => {
      const exists = Array.from(controller.allFiles.files).some(f => f.name === file.name && f.size === file.size);
      if (!exists) {
        controller.allFiles.items.add(file);
      }
    });
    this.renderPreviews(controller.allFiles.files, controller);
  },

  renderPreviews(files, controller) {
    const container = $('#previews');
    container.empty();

    Array.from(files).forEach((file, index) => {
      const isImg = file.type.startsWith('image/');
      const reader = new FileReader();

      const cardHtml = `
      <div class="col-md-3 col-sm-6 mb-2" id="preview-${index}">
        <div class="card p-1 border shadow-none text-center h-100 position-relative">
          <button type="button"
                  class="btn btn-danger btn-xs position-absolute top-0 end-0 m-1 remove-file-btn"
                  data-index="${index}"
                  style="padding: 2px 5px; z-index: 10;">
            <i class="ri-close-line"></i>
          </button>
          <div style="height: 80px;" class="d-flex align-items-center justify-content-center bg-light rounded">
            ${isImg ? `<img id="img-${index}" class="img-fluid" style="max-height: 70px;">` : `<i class="ri-file-line ri-2x"></i>`}
          </div>
          <div class="small text-truncate mt-1 px-1" title="${file.name}" style="font-size: 10px;">
            ${file.name}
          </div>
        </div>
      </div>`;

      container.append(cardHtml);

      if (isImg) {
        reader.onload = e => $(`#img-${index}`).attr('src', e.target.result);
        reader.readAsDataURL(file);
      }
    });

    $('.remove-file-btn')
      .off()
      .on('click', e => {
        e.stopPropagation();
        const idx = $(e.currentTarget).data('index');
        this.removeFile(idx, controller);
      });
  },

  removeFile(index, controller) {
    const newDataTransfer = new DataTransfer();
    const files = controller.allFiles.files;

    for (let i = 0; i < files.length; i++) {
      if (i !== index) newDataTransfer.items.add(files[i]);
    }

    controller.allFiles = newDataTransfer;
    this.renderPreviews(controller.allFiles.files, controller);
  }
};
