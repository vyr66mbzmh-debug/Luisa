/* NAV-091: return every user to their last main Luisa page and selection.
   One last module per account and one latest selection per module. No browsing history and no
   timestamps are kept. ADA keeps the preferences in private account storage (the page carries the
   current values and posts explicit changes with the session's CSRF token). The owner's static
   edition keeps them in this browser profile for this origin and path. */
(() => {
  'use strict';
  const script = document.currentScript;
  const module = script?.dataset.module || '';
  const base = new URL('./', script?.src || location.href);
  const PAGES = Object.freeze({skill: './', textbook: 'textbook-view.html', resources: 'teaching-chapters.html', papers: 'papers.html'});
  const meta = document.querySelector('meta[name="luisa-preferences"]');
  const ada = meta?.content === 'ada';
  const MAX_STATE = 12000;
  // Tab-session data that belongs to one signed-in account (or, on ADA, one sign-in).
  const TAB_KEYS = ['luisa-papers-v1', 'luisa-papers-exam-v1', 'luisa-lesson-return', 'luisa-resume-pending', 'luisa-nav-intent'];
  const localKey = 'luisa-preferences-v1:' + base.pathname;
  const parse = text => { try { const value = JSON.parse(text); return value && typeof value === 'object' && !Array.isArray(value) ? value : null; } catch { return null; } };
  const session = {
    get(key) { try { return sessionStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { sessionStorage.setItem(key, value); } catch { /* Storage can be disabled. */ } },
    remove(key) { try { sessionStorage.removeItem(key); } catch { /* Storage can be disabled. */ } }
  };
  // Isolate tab data when a different account (or a new ADA sign-in) uses this tab.
  const scope = ada ? (meta.dataset.scope || '') : 'owner';
  if (session.get('luisa-account-scope') !== scope) {
    for (const key of TAB_KEYS) session.remove(key);
    session.set('luisa-account-scope', scope);
  }
  const allowed = new Set(ada ? (meta.dataset.modules || '').split(',').filter(name => PAGES[name]) : Object.keys(PAGES));
  let stored;
  if (ada) stored = parse(meta.dataset.state) || {};
  else { try { stored = parse(localStorage.getItem(localKey)) || {}; } catch { stored = {}; } }
  const modules = stored.modules && typeof stored.modules === 'object' ? {...stored.modules} : {};
  let last = allowed.has(stored.last) ? stored.last : null;
  // A change posted just before leaving a page may still be in flight; the tab keeps it until confirmed.
  const pending = parse(session.get('luisa-resume-pending')) || {};
  for (const [name, value] of Object.entries(pending)) if (name === '_last') { if (allowed.has(value)) last = value; } else modules[name] = value;
  const written = new Map(Object.entries(modules).map(([name, value]) => [name, JSON.stringify(value)]));

  let touched = false;
  // Any user input on the page marks later state changes as the user's own (Luisa never dispatches these itself).
  for (const type of ['pointerdown', 'keydown', 'change', 'input']) document.addEventListener(type, () => { touched = true; }, true);
  // A click on a Luisa link is deliberate in-app navigation, so the destination never bounces elsewhere.
  document.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (!link || event.defaultPrevented) return;
    try {
      const url = new URL(link.href, location.href);
      if (url.origin === base.origin && url.pathname.startsWith(base.pathname)) session.set('luisa-nav-intent', url.pathname);
    } catch { /* Ignore malformed links. */ }
  }, true);

  let queue = [], sending = false;
  function remember(name, value) {
    const next = {...(parse(session.get('luisa-resume-pending')) || {}), [name]: value};
    session.set('luisa-resume-pending', JSON.stringify(next));
  }
  function confirmed(name, value) {
    const current = parse(session.get('luisa-resume-pending')) || {};
    if (JSON.stringify(current[name]) === JSON.stringify(value)) { delete current[name]; session.set('luisa-resume-pending', JSON.stringify(current)); }
  }
  async function flush() {
    if (sending) return;
    sending = true;
    try {
      while (queue.length) {
        const item = queue.shift();
        const body = new URLSearchParams({_csrf: meta.dataset.csrf || ''});
        if (item.name === '_last') body.set('last', item.value); else { body.set('module', item.name); body.set('state', JSON.stringify(item.value)); }
        const response = await fetch(new URL('preferences', base), {method: 'POST', body, keepalive: true, credentials: 'same-origin', redirect: 'error'});
        if (response.ok || response.status === 400 || response.status === 403) confirmed(item.name, item.value);
        if (!response.ok) break;
      }
    } catch { /* Resume is optional; the pending copy is retried on the next page in this tab. */ }
    finally { sending = false; }
  }
  function write(name, value) {
    if (ada) {
      remember(name, value);
      queue = queue.filter(item => item.name !== name);
      queue.push({name, value});
      flush();
      return;
    }
    try {
      const current = parse(localStorage.getItem(localKey)) || {};
      const next = {last: current.last, modules: {...(current.modules || {})}};
      if (name === '_last') next.last = value; else next.modules[name] = value;
      localStorage.setItem(localKey, JSON.stringify(next));
    } catch { /* Private browsing can disable storage. */ }
  }
  // Retry anything a previous page in this tab could not confirm.
  if (ada) for (const [name, value] of Object.entries(pending)) { queue.push({name, value}); }
  if (queue.length) flush();

  function save(name, value) {
    if (!/^(skill|textbook|resources|papers|exam)$/.test(name) || !value || typeof value !== 'object') return false;
    const text = JSON.stringify(value);
    if (text.length > MAX_STATE || written.get(name) === text) return false;
    written.set(name, text); modules[name] = JSON.parse(text);
    write(name, modules[name]);
    return true;
  }
  function visit(name) {
    if (!allowed.has(name) || last === name) return;
    last = name;
    write('_last', name);
  }

  // Ordinary entry: the root opened directly (sign-in, a bookmark, a new tab or a launch), not a
  // reload, Back/Forward, a hash destination or a click on a Luisa link such as By skill or Home.
  const intent = session.get('luisa-nav-intent');
  session.remove('luisa-nav-intent');
  const navigation = performance.getEntriesByType?.('navigation')?.[0]?.type || 'navigate';
  let referrer = null;
  try { referrer = document.referrer ? new URL(document.referrer) : null; } catch { referrer = null; }
  const fromLuisa = referrer && referrer.origin === base.origin && referrer.pathname.startsWith(base.pathname) &&
    !/\/(?:login|change-password|logout)$/.test(referrer.pathname);
  const params = new URLSearchParams(location.search);
  const explicitSkill = !ada && /\/by-skill(?:\.html)?\/?$/.test(location.pathname);
  const explicit = explicitSkill || Boolean(location.hash.length > 1 || [...params.keys()].some(key => key !== 'entry'));
  const entry = explicit ? 'explicit' : (intent === location.pathname || navigation === 'reload' || navigation === 'back_forward' || fromLuisa) ? 'internal' : 'ordinary';
  if (params.get('entry') === 'signin') { try { history.replaceState(history.state, '', location.pathname + location.hash); } catch { /* Keep the URL. */ } }

  let leaving = false;
  if (module === 'skill' && entry === 'ordinary' && last && last !== 'skill' && allowed.has(last)) {
    leaving = true;
    location.replace(new URL(PAGES[last], base).href);
  }
  function recordVisit() {
    if (leaving || !module) return;
    if (document.visibilityState === 'visible') visit(module);
    else document.addEventListener('visibilitychange', function once() { if (document.visibilityState === 'visible') { document.removeEventListener('visibilitychange', once); visit(module); } });
  }
  recordVisit();
  window.addEventListener('pageshow', event => { if (event.persisted) { leaving = false; recordVisit(); } });

  window.LUISA_RESUME = Object.freeze({
    edition: ada ? 'ada' : 'owner', module, entry,
    get leaving() { return leaving; },
    get: name => modules[name] ? JSON.parse(JSON.stringify(modules[name])) : null,
    save, visit,
    touched: () => touched,
    // Pupils on ADA: the course their current class implies (Further Maths for L6X, U6X, L6Y and U6Y).
    defaultCourse: ada && meta.dataset.defaultCourse ? meta.dataset.defaultCourse : null,
    lastModule: () => last
  });
})();
