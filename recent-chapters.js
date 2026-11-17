// Resume links use the catalogue's canonical teaching route on this edition.
(() => {
  const settings = document.querySelector('meta[name="recent-chapters"]');
  if (!settings || !window.LUISA_TEACHING) return;
  const chapters = new Map();
  for (const [book, volume] of Object.entries(LUISA_TEACHING)) {
    for (const chapter of volume.chapters) {
      if (chapter.slides) chapters.set(book + ':' + chapter.number, {book, volume, chapter});
    }
  }
  const storageKey = 'recent-chapters-v1:' + new URL('.', location.href).pathname + ':' + settings.content;
  function readLocal() {
    try {
      const data = JSON.parse(localStorage.getItem(storageKey));
      return Array.isArray(data) ? data.filter(valid).slice(0, 4) : [];
    } catch { return []; }
  }
  function valid(row) {
    return row && chapters.has(row.key) && Number.isSafeInteger(row.slide) && row.slide > 0;
  }
  function current(slide) {
    const url = new URL(location.href);
    if (url.pathname.endsWith('/pure1-native-viewer.html')) {
      const key = 'maths-pure-year-1:' + url.searchParams.get('chapter');
      if (chapters.has(key)) return {key, slide};
    }
    for (const [key, item] of chapters) {
      const link = new URL(item.chapter.slides, document.baseURI);
      if (link.pathname === url.pathname && ['book','chapter'].every(k => link.searchParams.get(k) === url.searchParams.get(k))) {
        return {key,slide};
      }
    }
  }
  const teacher = settings.content === 'teacher';
  let queued, writing = false;
  async function syncLatest() {
    if (writing) return;
    writing = true;
    try {
      while (queued) {
        const row = queued;
        queued = null;
        const data = new URLSearchParams({key:row.key, slide:row.slide, _csrf:settings.dataset.csrf});
        const response = await fetch('recent-chapters', {method:'POST', body:data, keepalive:true});
        if (!response.ok) break;
      }
    } catch { /* Resume remains optional when the network is interrupted. */ }
    finally { writing = false; }
  }
  function remember(slide) {
    const row = current(slide);
    if (!valid(row)) return;
    if (teacher) {
      queued = row;
      syncLatest();
      return;
    }
    try { localStorage.setItem(storageKey, JSON.stringify([row,...readLocal().filter(item => item.key !== row.key)].slice(0,4))); }
    catch { /* Private browsing can disable storage. */ }
  }
  function render(rows) {
    const shelf = document.getElementById('recent-chapters');
    if (!shelf) return;
    const nav = shelf.querySelector('nav');
    nav.replaceChildren();
    for (const row of rows.filter(valid).slice(0,4)) {
      const {book,volume,chapter} = chapters.get(row.key);
      const url = new URL(chapter.slides, document.baseURI);
      url.searchParams.set('slide',row.slide);
      const card = document.createElement('a');
      card.href = url.href;
      card.className = book.includes('core') ? 'recent-core' : book.includes('applied') ? 'recent-applied' : 'recent-pure';
      for (const [tag, text] of [['small',volume.title],['strong',chapter.title],['span','Resume slide ' + row.slide + ' →']]) {
        const label = document.createElement(tag);
        label.textContent = text;
        card.append(label);
      }
      nav.append(card);
    }
    shelf.hidden = !nav.childElementCount;
  }
  window.addEventListener('luisa-slide', e => remember(e.detail));
  async function refresh() {
    if (!document.getElementById('recent-chapters')) return;
    if (!teacher) return render(readLocal());
    try {
      const response = await fetch('recent-chapters', {cache:'no-store'});
      if (response.ok) render(await response.json());
    } catch { /* Leave the catalogue available. */ }
  }
  window.addEventListener('pageshow', refresh);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  if (!teacher) window.addEventListener('storage', e => { if (e.key === storageKey) refresh(); });
})();
