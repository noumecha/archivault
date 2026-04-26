// documents.ui.js
import { renderPagination } from '../../helpers/utils.js';

export const DocumentUI = {
  statusColors: {
    'en attente': 'bg-warning',
    'en traitement': 'bg-info',
    valide: 'bg-success',
    archive: 'bg-secondary'
  },

  preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  },

  highlight($el) {
    $el.addClass('bg-light');
  },

  unhighlight($el) {
    $el.removeClass('bg-light');
  },

  renderTable(response) {
    const tbody = $('#documents-tbody');
    tbody.empty();
    const docs = response.results || response;

    if (!docs || docs.length === 0) {
      tbody.html('<tr><td colspan="8" class="text-center">Aucun document trouvé</td></tr>');
      this.renderPagination(0);
      return;
    }

    const rows = docs.map(doc => this.createDocumentRow(doc)).join('');
    tbody.html(rows);
    this.renderPagination(response);
  },

  createDocumentRow(doc) {
    const statusColor = this.statusColors[doc.etat] || 'bg-secondary';
    return `
      <tr data-id="${doc.id}">
        <td><div class="form-check"><input class="form-check-input doc-checkbox" type="checkbox" value="${doc.id}"></div></td>
        <td><i class="ri-file-text-line ri-24px text-primary"></i></td>
        <td><span class="fw-medium">${doc.titre}</span></td>
        <td>${doc.type_document_display || '-'}</td>
        <td>${doc.theme_display || '-'}</td>
        <td><span class="badge rounded-pill ${statusColor}">${doc.etat_display}</span></td>
        <td>${new Date(doc.Date_creation).toLocaleDateString()}</td>
        <td>
          <div class="dropdown">
            <button class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ri-more-2-line"></i></button>
            <div class="dropdown-menu">
              <a href="/document/documents/${doc.id}/" class="dropdown-item"><i class="ri-eye-line me-1"></i>Voir</a>
              <a href="#" class="dropdown-item" data-action="edit" data-id="${doc.id}"><i class="ri-pencil-line me-1"></i>Modifier</a>
              <a href="#" class="dropdown-item text-danger" data-action="delete" data-id="${doc.id}"><i class="ri-delete-bin-line me-1"></i>Supprimer</a>
            </div>
          </div>
        </td>
      </tr>`;
  },

  renderPagination(data) {
    renderPagination(data, '#documents-pagination', '#pagination-info');
  },

  renderPreviews(files, $container) {
    $container.empty();
    files.forEach((file, index) => {
      $container.append(this.buildPreviewCard(file, index));
    });
  },

  buildPreviewCard(file, index) {
    const $col = $('<div class="col-3 mb-3"></div>');
    const $card = $('<div class="card p-1 h-100 text-center"></div>');
    const $body = $('<div></div>');

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      const $img = $('<img style="max-width:100%;max-height:80px;object-fit:cover;">');
      reader.onload = e => $img.attr('src', e.target.result);
      reader.readAsDataURL(file);
      $body.append($img);
    } else {
      $body.html(
        `<i class="ri-file-3-line ri-48px text-secondary"></i><br><small class="text-truncate d-block">${file.name}</small>`
      );
    }

    const $btn = $(
      '<button type="button" class="btn btn-sm btn-icon btn-outline-danger position-absolute top-0 end-0 m-1"><i class="ri-close-line"></i></button>'
    );
    $btn.on('click', () => $(document).trigger('file:remove', index));

    $card.append($btn, $body);
    $col.append($card);

    return $col;
  },

  updateProgress(percent) {
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
  },

  resetForm() {
    $('#upload-form')[0].reset();
    $('#file-input').val('');
    $('#previews').empty();
  }
};
