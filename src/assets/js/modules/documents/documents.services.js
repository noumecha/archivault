// documents.services.js
export const DocumentService = (function () {
  function checkConflict(file) {
    return $.get(`/check-document/?filename=${encodeURIComponent(file.name)}`);
  }

  function upload(formData, onProgress) {
    return $.ajax({
      url: '/api/upload/',
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      xhr: function () {
        const xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener('progress', function (e) {
          if (e.lengthComputable) {
            onProgress((e.loaded / e.total) * 100);
          }
        });
        return xhr;
      }
    });
  }

  return {
    checkConflict,
    upload
  };
})();
