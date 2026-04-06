// documents/documents.states.js
export const DocumentState = (function () {
  let state = {
    conflictQueue: [],
    uploadQueue: [],
    currentConflict: null,
    actions: []
  };

  function reset() {
    state.conflictQueue = [];
    state.uploadQueue = [];
    state.currentConflict = null;
    state.actions = [];
  }

  return {
    get: () => state,
    reset
  };
})();
