// modules/cellules/cellules.ui.js
export const CelluleUI = (function () {
  function renderList(container, data) {
    $(container).html(data.html);
  }

  function resetForm(formSelector) {
    $(formSelector)[0].reset();
  }

  function showMessage(message, selector) {
    const $msg = $(selector);
    $msg.text(message).fadeIn().delay(3000).fadeOut();
  }

  return { renderList, resetForm, showMessage };
})();
