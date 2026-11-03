'use strict';
// A chapter return opens the chapter library; question/skill returns keep their existing view.
(() => {
  function openChapterView() {
    const selection = new URLSearchParams(location.hash.slice(1));
    if (selection.has('book') && /^\d+$/.test(selection.get('chapter') || '') && !selection.has('skill')) {
      location.replace('textbook-view.html' + location.hash);
    }
  }
  window.addEventListener('hashchange', openChapterView);
  openChapterView();
})();
