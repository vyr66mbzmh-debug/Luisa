'use strict';
(async () => {
  const $ = id => document.getElementById(id);
  const storageKey = 'luisa-papers-v1';
  const pageSize = 8;
  // Keep these identical to the question library renderer in app.js.
  const mathMacros = {"\\p":"\\mathrm P(#1)",'\\cosec':'\\operatorname{cosec}','\\cosech':'\\operatorname{cosech}','\\sech':'\\operatorname{sech}','\\coth':'\\operatorname{coth}','\\arcosech':'\\operatorname{arcosech}','\\arcsech':'\\operatorname{arcsech}','\\arsech':'\\operatorname{arsech}','\\arcoth':'\\operatorname{arcoth}','\\arsinh':'\\operatorname{arsinh}','\\arcosh':'\\operatorname{arcosh}','\\artanh':'\\operatorname{artanh}','\\Real':'\\operatorname{Re}','\\Imag':'\\operatorname{Im}','\\ssum':'\\sum_{r=1}^{#1}#2','\\arraystretch':'1'};
  const catalogue = [], skills = [], rows = new Map(), contentCache = new Map(), sourceCounts = new Map();
  let selected = [], chosenSkills = new Set(), chosenTopics = new Set(), page = 0, browseOpen = false;
  let operation = null, browseOperation = null, printing = false, persistEnabled = false;
  function status(message, error = false) {
    $('papers-status').textContent = message;
    $('papers-status').classList.toggle('error', error);
  }
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function renderMath(root) {
    for (const node of root.querySelectorAll('[data-math]')) {
      window.katex.render(node.dataset.math, node, {displayMode: node.dataset.display === 'true', throwOnError: true, strict: 'error', macros: {...mathMacros}});
    }
  }
  const sourceLabel = row => row.sourceKind === 'practice-booklet'
    ? `Source: Practice Booklet · Chapter ${row.chapterNumber} · ${row.subchapterTitle} · ${/^\d/.test(row.questionLabel) ? 'Q' : ''}${row.questionLabel}`
    : `Source: Luisa ${row.skillCode} Q${row.number}`;
  const contextLabel = row => `${row.courseTitle} · ${row.bookTitle} · ${row.topicTitle}`;
  function persist() {
    if (!persistEnabled) return;
    try {
      sessionStorage.setItem(storageKey, JSON.stringify({version: 1, source: $('papers-source').value, selected: selected.map(row => row.id), course: $('papers-course').value, book: $('papers-book').value, topics: [...chosenTopics], skills: [...chosenSkills], count: $('papers-count').value}));
    } catch (_) { $('papers-selection-note').textContent = 'Your selection is held on this page. Browser session storage is unavailable.'; }
  }
  function sourceMatches(row) {
    const source = $('papers-source').value;
    return source === 'both' || row.sourceKind === source;
  }
  function skillCount(skill) {
    return sourceCounts.get(`${$('papers-source').value}/${skill.key}`) || 0;
  }
  function filteredSkills() {
    return skills.filter(s => skillCount(s) > 0 && (!$('papers-course').value || s.courseId === $('papers-course').value) && (!$('papers-book').value || s.bookKey === $('papers-book').value) && (!chosenTopics.size || chosenTopics.has(s.topicKey)));
  }
  function pool() {
    const included = new Set(filteredSkills().filter(s => !chosenSkills.size || chosenSkills.has(s.key)).map(s => s.key));
    return catalogue.filter(row => sourceMatches(row) && row.skillKeys.some(key => included.has(key)));
  }
  function options(id, label, choices, wanted = '') {
    const select = $(id);
    select.replaceChildren(new Option(label, ''), ...choices.map(([value, title]) => new Option(title, value)));
    select.value = choices.some(([value]) => value === wanted) ? wanted : '';
  }
  function refreshFilters(wantedBook = '') {
    const courses = window.FMQ_LIBRARY.courses.filter(c => !$('papers-course').value || c.id === $('papers-course').value);
    options('papers-book', 'All books', courses.flatMap(c => c.books.map(b => [`${c.id}/${b.id}`, b.title])), wantedBook);
    const topicMap = new Map();
    for (const skill of skills) {
      if (!skillCount(skill) || ($('papers-course').value && skill.courseId !== $('papers-course').value) || ($('papers-book').value && skill.bookKey !== $('papers-book').value)) continue;
      topicMap.set(skill.topicKey, {key: skill.topicKey, title: skill.topicTitle, bookTitle: skill.bookTitle});
    }
    const topics = [...topicMap.values()];
    chosenTopics = new Set([...chosenTopics].filter(key => topics.some(t => t.key === key)));
    $('papers-topics').replaceChildren(...topics.map(t => {
      const label = element('label', undefined, 'topic-choice');
      const input = document.createElement('input'); input.type = 'checkbox'; input.value = t.key; input.checked = chosenTopics.has(t.key);
      const text = element('span', t.title); text.append(element('small', t.bookTitle));
      label.append(input, text); return label;
    }));
    const visible = filteredSkills();
    chosenSkills = new Set([...chosenSkills].filter(key => visible.some(s => s.key === key)));
    $('papers-skills').replaceChildren(...visible.map(s => {
      const label = element('label', undefined, 'skill-choice');
      const input = document.createElement('input'); input.type = 'checkbox'; input.value = s.key; input.checked = chosenSkills.has(s.key);
      const text = element('span', `${s.code} · ${s.title}`);
      text.append(element('small', `${s.bookTitle} · ${skillCount(s)} questions`));
      label.append(input, text); return label;
    }));
    updatePool();
  }
  function updatePool() {
    cancelLoading();
    const count = pool().length;
    $('papers-pool-count').textContent = `${count.toLocaleString()} questions in this pool`;
    $('papers-count').max = String(count);
    page = 0; updateControls(); persist();
    if (browseOpen) renderBrowse();
  }
  function updateControls() {
    const busy = Boolean(operation) || printing;
    $('papers-generate').disabled = busy || !pool().length;
    $('papers-regenerate').disabled = busy || !selected.length || !pool().length;
    $('papers-clear').disabled = busy || !selected.length;
    $('papers-print').disabled = busy || !selected.length || !window.LUISA_PAPERS_PRINT;
    $('papers-cancel').hidden = !operation;
    $('papers-selected').setAttribute('aria-busy', String(Boolean(operation)));
    document.querySelectorAll('[data-add], [data-remove]').forEach(button => { button.disabled = busy; });
  }
  function cancelLoading(announce = true) {
    if (!operation) return;
    operation.abort(); operation = null; updateControls();
    if (announce) status('Loading cancelled. Your previous paper has been kept.');
  }
  async function loadRow(descriptor, signal) {
    if (rows.has(descriptor.id)) return rows.get(descriptor.id);
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    const practice = descriptor.sourceKind === 'practice-booklet';
    const dataPath = practice ? descriptor.dataPath : `content/${encodeURIComponent(descriptor.skillId)}.json`;
    let content = contentCache.get(dataPath);
    if (!content) {
      content = !practice && window.FMQ_CONTENT?.[descriptor.skillId];
      if (!content) {
        const response = await fetch(new URL(dataPath, document.baseURI), {signal});
        if (!response.ok) throw new Error(`Could not load ${sourceLabel(descriptor)}. Check your connection and try again.`);
        content = await response.json();
      }
      if (practice && content.schemaVersion === 1) content = content.questions;
      if (!Array.isArray(content)) throw new Error('The question source has invalid data.');
      contentCache.set(dataPath, content);
    }
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    const question = content.find(q => practice ? q.id === descriptor.id : String(q.number) === String(descriptor.number) && !q.reference);
    if (!question?.question || (question.contextHtml !== undefined && typeof question.contextHtml !== 'string') || !Array.isArray(question.steps) || !question.steps.length || question.steps.some(step => typeof step !== 'string' || !step.trim()) || (question.hints !== undefined && (!Array.isArray(question.hints) || question.hints.some(hint => typeof hint !== 'string')))) {
      throw new Error(`${sourceLabel(descriptor)} has incomplete content. Your previous paper has been kept.`);
    }
    const row = Object.freeze({...descriptor, question: question.question, contextHtml: question.contextHtml || '', steps: Object.freeze([...question.steps]), hints: Object.freeze([...(question.hints || [])]), source: Object.freeze({kind: practice ? 'practice-booklet' : 'skill-question', courseId: descriptor.courseId, bookId: descriptor.bookId, topicId: descriptor.topicId, skillId: descriptor.skillId || null, questionId: question.id || null, questionNumber: practice ? descriptor.questionLabel : question.number, chapterId: descriptor.chapterId || null, subchapterId: descriptor.subchapterId || null, practiceBookletQuestionId: practice ? descriptor.id : null})});
    rows.set(row.id, row); return row;
  }
  function fillPreview(container, row) {
    container.innerHTML = (row.contextHtml || '') + row.question;
    try { renderMath(container); }
    catch (_) { container.replaceChildren(element('p', 'This mathematical preview could not be rendered. Reload the page before printing.', 'preview-error')); }
  }
  function updateSelection() {
    $('papers-selected-count').textContent = selected.length.toLocaleString();
    $('papers-empty').hidden = Boolean(selected.length);
    $('papers-selected').replaceChildren(...selected.map(row => {
      const li = element('li', undefined, 'selected-item');
      const details = document.createElement('details');
      const summary = element('summary', sourceLabel(row));
      summary.append(element('small', `${contextLabel(row)} · ${row.skillTitle}`));
      const preview = element('div', undefined, 'math-content selected-preview');
      details.append(summary, preview);
      details.addEventListener('toggle', () => { if (details.open && !preview.childNodes.length) fillPreview(preview, row); });
      const remove = element('button', 'Remove', 'remove-question'); remove.type = 'button'; remove.dataset.remove = row.id;
      remove.setAttribute('aria-label', `Remove ${sourceLabel(row)} from ${row.bookTitle}`);
      li.append(details, remove); return li;
    }));
    syncAddButtons(); updateControls(); persist();
  }
  function syncAddButtons() {
    const ids = new Set(selected.map(row => row.id));
    document.querySelectorAll('[data-add]').forEach(button => {
      const included = ids.has(button.dataset.add);
      button.textContent = included ? 'Remove from paper' : 'Add to paper';
      button.setAttribute('aria-pressed', String(included));
    });
  }
  async function setSelection(descriptors, message) {
    cancelLoading(false);
    const controller = new AbortController(); operation = controller; updateControls();
    status(`Loading ${descriptors.length} questions…`);
    try {
      const next = [];
      for (const descriptor of descriptors) {
        next.push(await loadRow(descriptor, controller.signal));
        if (next.length % 20 === 0) status(`Loading questions: ${next.length} of ${descriptors.length}…`);
      }
      if (operation !== controller) return;
      selected = next; operation = null; updateSelection(); status(message);
    } catch (error) {
      if (operation !== controller) return;
      operation = null; updateControls();
      if (error.name !== 'AbortError') status(error.message || 'The questions could not be loaded. Try again.', true);
    }
  }
  function generate() {
    if (operation || printing) return;
    const candidates = pool(), count = Number($('papers-count').value);
    if (!Number.isInteger(count) || count < 1 || count > candidates.length) {
      status(`Choose a whole number from 1 to ${candidates.length.toLocaleString()} for this question pool.`, true);
      $('papers-count').focus(); return;
    }
    // Partial Fisher–Yates sampling, without replacement.
    for (let i = 0; i < count; i++) {
      const j = i + Math.floor(Math.random() * (candidates.length - i));
      [candidates[i], candidates[j]] = [candidates[j], candidates[i]];
    }
    const next = candidates.slice(0, count), previous = new Set(selected.map(row => row.id));
    if (count < candidates.length && next.length === selected.length && next.every(row => previous.has(row.id))) next[count - 1] = candidates[count];
    setSelection(next, `${count} questions selected. Review your paper or choose Preview & print.${count === candidates.length ? ' Every question in this pool is included.' : ''}`);
  }
  async function renderBrowse() {
    browseOperation?.abort();
    const controller = new AbortController(); browseOperation = controller;
    const candidates = pool(), total = Math.ceil(candidates.length / pageSize);
    page = Math.min(page, Math.max(0, total - 1));
    $('papers-browser').hidden = false;
    $('papers-previous').disabled = page === 0;
    $('papers-next').disabled = page + 1 >= total;
    $('papers-page').textContent = total ? `Page ${page + 1} of ${total} · ${candidates.length.toLocaleString()} questions` : 'No questions in this pool';
    const target = $('papers-questions'); target.setAttribute('aria-busy', 'true');
    target.replaceChildren(element('p', candidates.length ? 'Loading question previews…' : 'Choose another topic or skill to find questions.'));
    try {
      const loaded = [];
      for (const row of candidates.slice(page * pageSize, (page + 1) * pageSize)) loaded.push(await loadRow(row, controller.signal));
      if (browseOperation !== controller) return;
      if (loaded.length) target.replaceChildren(...loaded.map(row => {
        const card = element('article', undefined, 'question-card');
        card.append(element('h3', sourceLabel(row), 'source-label'), element('p', `${contextLabel(row)} · ${row.skillTitle}`, 'question-context'));
        const preview = element('div', undefined, 'math-content'); fillPreview(preview, row);
        const add = element('button', 'Add to paper'); add.type = 'button'; add.dataset.add = row.id;
        add.setAttribute('aria-label', `Add or remove ${sourceLabel(row)} from ${row.bookTitle}`);
        card.append(preview, add); return card;
      }));
      syncAddButtons(); updateControls();
    } catch (error) {
      if (browseOperation !== controller) return;
      target.replaceChildren(element('p', error.message || 'Previews could not be loaded. Use Browse questions to retry.', 'preview-error'));
      status('Question previews could not be loaded. Check your connection, then choose Browse questions to retry.', true);
    } finally { if (browseOperation === controller) target.setAttribute('aria-busy', 'false'); }
  }
  try {
    if (!window.FMQ_LIBRARY?.courses?.length) throw new Error('The question library is unavailable. Reload this page to try again.');
    status('Loading the Edexcel question catalogue…');
    const response = await fetch(new URL('textbook-catalogue.json', document.baseURI));
    if (!response.ok) throw new Error('The Edexcel catalogue could not be loaded. Check your connection and reload.');
    const textbook = await response.json();
    if (!Array.isArray(textbook.questions) || !textbook.questions.length) throw new Error('The Edexcel catalogue is unavailable. Reload the page to try again.');
    // Reuse the question-level eligibility already used by By textbook. Some
    // skills mix eligible and other-board questions, so a skill flag is insufficient.
    const edexcelIds = new Set(textbook.questions.map(q => `${q.skill}/${q.question}`));
    const ids = new Set(), skillIndex = new Map();
    for (const course of window.FMQ_LIBRARY.courses) for (const book of course.books) for (const topic of book.topics) for (const skill of topic.skills) {
      if (skill.reference || skill.available === false) continue;
      const eligible = skill.questions.filter(q => !q.reference && edexcelIds.has(`${skill.id}/${q.number}`));
      const key = `${course.id}/${book.id}/${topic.id}/${skill.id}`;
      const metadata = {key, topicTitle: topic.title, courseId: course.id, bookKey: `${course.id}/${book.id}`, topicKey: `${course.id}/${book.id}/${topic.id}`, code: skill.code, title: skill.title, bookTitle: book.title, count: eligible.length};
      skills.push(metadata); skillIndex.set(`${course.id}/${book.id}/${skill.id}`, {...metadata, courseTitle: course.title, bookId: book.id, topicId: topic.id, topicTitle: topic.title, skillId: skill.id});
      for (const question of eligible) {
        const id = `${key}/q${question.number}`;
        if (ids.has(id)) continue;
        ids.add(id);
        catalogue.push(Object.freeze({id, sourceKind: 'luisa', skillKeys: Object.freeze([key]), number: question.number, courseId: course.id, bookId: book.id, topicId: topic.id, skillId: skill.id, skillKey: key, courseTitle: course.title, bookTitle: book.title, topicTitle: topic.title, skillCode: skill.code, skillTitle: skill.title}));
      }
    }
    const practiceResponse = await fetch(new URL('practice-catalogue.json', document.baseURI));
    if (!practiceResponse.ok) throw new Error('The Practice Booklet catalogue could not be loaded. Check your connection and reload.');
    const practiceCatalogue = await practiceResponse.json();
    if (practiceCatalogue.version !== 1 || !Array.isArray(practiceCatalogue.questions)) throw new Error('The Practice Booklet catalogue is invalid.');
    for (const item of practiceCatalogue.skills || []) {
      const course = window.FMQ_LIBRARY.courses.find(c => c.id === item.courseId);
      const book = course?.books.find(b => b.id === item.bookId);
      const topic = book?.topics.find(t => t.id === item.topicId) || (book && item.topicId?.startsWith('practice-topic-') && item.topicTitle ? {id: item.topicId, title: item.topicTitle} : null);
      const indexKey = `${item.courseId}/${item.bookId}/${item.id}`;
      if (!topic || !item.id?.startsWith('practice-') || skillIndex.has(indexKey)) throw new Error('A Practice Booklet skill is invalid.');
      const key = `${item.courseId}/${item.bookId}/${item.topicId}/${item.id}`;
      const metadata = {key, courseId: course.id, bookId: book.id, bookKey: `${course.id}/${book.id}`, topicKey: `${course.id}/${book.id}/${topic.id}`, topicId: topic.id, topicTitle: topic.title, courseTitle: course.title, bookTitle: book.title, code: item.code, title: item.title};
      skills.push(metadata); skillIndex.set(indexKey, metadata);
    }
    for (const q of practiceCatalogue.questions) {
      const mapped = Array.isArray(q.skillIds) && q.skillIds.map(id => skillIndex.get(`${q.courseId}/${q.bookId}/${id}`));
      if (!q.id?.startsWith('practice/') || ids.has(q.id) || !mapped?.length || mapped.some(s => !s) || !/^content\/practice\/[a-z0-9/-]+\.json$/.test(q.dataPath) || !q.chapterNumber || !q.subchapterId || !q.subchapterTitle || !q.questionLabel || q.board !== 'Edexcel') throw new Error('A Practice Booklet source is incomplete or unverified.');
      const first = mapped[0];
      ids.add(q.id);
      catalogue.push(Object.freeze({...q, sourceKind: 'practice-booklet', skillKeys: Object.freeze(mapped.map(s => s.key)), courseTitle: first.courseTitle, bookTitle: first.bookTitle, topicTitle: q.chapterTitle, skillTitle: q.subchapterTitle}));
    }
    for (const row of catalogue) for (const key of new Set(row.skillKeys)) {
      for (const kind of [row.sourceKind, 'both']) sourceCounts.set(`${kind}/${key}`, (sourceCounts.get(`${kind}/${key}`) || 0) + 1);
    }
    let saved = null;
    try { saved = JSON.parse(sessionStorage.getItem(storageKey)); } catch (_) { /* A new session or unavailable storage. */ }
    if (saved?.version !== 1) saved = null;
    $('papers-source').value = ['luisa', 'practice-booklet', 'both'].includes(saved?.source) ? saved.source : 'both';
    options('papers-course', 'All courses', window.FMQ_LIBRARY.courses.map(c => [c.id, c.title]), saved?.course);
    chosenSkills = new Set(Array.isArray(saved?.skills) ? saved.skills : []);
    chosenTopics = new Set(Array.isArray(saved?.topics) ? saved.topics : saved?.topic ? [saved.topic] : []);
    if (saved?.count && /^\d+$/.test(saved.count)) $('papers-count').value = saved.count;
    refreshFilters(saved?.book);
    persistEnabled = true;
    $('papers-source').addEventListener('change', () => { chosenSkills.clear(); chosenTopics.clear(); refreshFilters($('papers-book').value); });
    $('papers-course').addEventListener('change', () => { chosenSkills.clear(); chosenTopics.clear(); refreshFilters(); });
    $('papers-book').addEventListener('change', () => { chosenSkills.clear(); chosenTopics.clear(); refreshFilters($('papers-book').value); });
    $('papers-topics').addEventListener('change', event => {
      if (event.target.checked) chosenTopics.add(event.target.value); else chosenTopics.delete(event.target.value);
      chosenSkills.clear(); refreshFilters($('papers-book').value);
    });
    $('papers-all-topics').addEventListener('click', () => { chosenTopics.clear(); chosenSkills.clear(); refreshFilters($('papers-book').value); });
    $('papers-skills').addEventListener('change', event => {
      if (event.target.checked) chosenSkills.add(event.target.value); else chosenSkills.delete(event.target.value);
      updatePool();
    });
    $('papers-all-skills').addEventListener('click', () => { chosenSkills.clear(); refreshFilters($('papers-book').value); });
    $('papers-count').addEventListener('change', persist);
    $('papers-generate-form').addEventListener('submit', event => { event.preventDefault(); generate(); });
    $('papers-regenerate').addEventListener('click', generate);
    $('papers-cancel').addEventListener('click', () => cancelLoading());
    $('papers-clear').addEventListener('click', () => { selected = []; updateSelection(); status('Paper cleared. Choose questions to start again.'); });
    $('papers-browse').addEventListener('click', () => { browseOpen = true; renderBrowse(); });
    $('papers-previous').addEventListener('click', () => { page--; renderBrowse(); });
    $('papers-next').addEventListener('click', () => { page++; renderBrowse(); });
    $('papers-questions').addEventListener('click', event => {
      const button = event.target.closest('[data-add]'); if (!button || operation || printing) return;
      const row = rows.get(button.dataset.add); if (!row) return;
      if (selected.some(q => q.id === row.id)) selected = selected.filter(q => q.id !== row.id); else selected = [...selected, row];
      updateSelection(); status(`${selected.length} questions selected.`);
    });
    $('papers-selected').addEventListener('click', event => {
      const button = event.target.closest('[data-remove]'); if (!button || operation || printing) return;
      const index = selected.findIndex(row => row.id === button.dataset.remove);
      selected = selected.filter(row => row.id !== button.dataset.remove); updateSelection();
      const next = $('papers-selected').querySelectorAll('[data-remove]');
      (next[Math.min(index, next.length - 1)] || $('papers-browse')).focus();
      status(`${selected.length} questions selected.`);
    });
    $('papers-print').addEventListener('click', async () => {
      if (!selected.length || operation || printing) return;
      // Snapshot before opening: future edits cannot change this paper or its solutions.
      const snapshot = Object.freeze([...selected]);
      printing = true; updateControls(); status('Preparing the print preview…');
      try {
        const result = await window.LUISA_PAPERS_PRINT.create(snapshot);
        if (result?.ready === false) status(`The preview needs attention before printing. ${(result.warnings || []).join(' ')}`, true);
        else status(result?.warnings?.length ? `Print preview ready. ${result.warnings.join(' ')}` : 'Print preview ready in a new window. Use its Print / Save PDF button.');
      } catch (error) { status(error.message || 'The print preview could not be opened. Allow pop-ups for this site and try again.', true); }
      finally { printing = false; updateControls(); }
    });
    for (const id of ['papers-source', 'papers-course', 'papers-book', 'papers-all-topics', 'papers-all-skills', 'papers-count', 'papers-generate', 'papers-browse']) $(id).disabled = false;
    updateControls();
    const savedIds = new Set(Array.isArray(saved?.selected) ? saved.selected : []);
    const byId = new Map(catalogue.map(row => [row.id, row]));
    const restored = [...savedIds].map(id => byId.get(id)).filter(Boolean);
    if (restored.length) setSelection(restored, `${restored.length} questions restored from this browser session.`);
    else status(`${catalogue.length.toLocaleString()} Edexcel-filtered worked questions available. Choose your pool to begin.`);
  } catch (error) {
    status(error.message || 'The paper builder could not start. Reload the page to retry.', true);
    for (const id of ['papers-generate', 'papers-regenerate', 'papers-print', 'papers-browse']) $(id).disabled = true;
  }
})();
