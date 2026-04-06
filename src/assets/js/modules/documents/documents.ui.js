// documents.ui.js
export const DocumentUI = (function () {
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight($el) {
    $el.addClass('bg-light');
  }

  function unhighlight($el) {
    $el.removeClass('bg-light');
  }

  function renderPreviews(files, $container) {
    $container.empty();

    files.forEach((file, index) => {
      $container.append(buildPreviewCard(file, index));
    });
  }

  function buildPreviewCard(file, index) {
    const $col = $('<div class="col-3 mb-3"></div>');
    const $card = $('<div class="card p-1 h-100 text-center"></div>');
    const $body = $('<div></div>');

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      const $img = $('<img style="max-width:100%;max-height:120px;">');
      reader.onload = e => $img.attr('src', e.target.result);
      reader.readAsDataURL(file);
      $body.append($img);
    } else {
      const ext = file.name.split('.').pop().toUpperCase();
      $body.html(`<p><strong>${ext}</strong><br><small>${file.name}</small></p>`);
    }

    const $btn = $('<button class="btn btn-sm btn-outline-danger w-100 mt-2">Supprimer</button>');
    $btn.on('click', () => $(document).trigger('file:remove', index));

    $card.append($body, $btn);
    $col.append($card);

    return $col;
  }

  function updateProgress(percent) {
    const $container = $('#progress-container');
    const $bar = $('#upload-progress');

    $container.show();
    $bar.css('width', percent + '%').text(Math.round(percent) + '%');

    if (percent >= 100) {
      setTimeout(() => {
        $container.hide();
        $bar.css('width', '0%');
      }, 1500);
    }
  }

  function resetForm() {
    $('#upload-form')[0].reset();
    $('#file-input').val('');
    $('#previews').empty();
  }

  return {
    preventDefaults,
    highlight,
    unhighlight,
    renderPreviews,
    updateProgress,
    resetForm
  };
})();
