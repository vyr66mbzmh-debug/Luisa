'use strict';
(async () => {
  const $ = id => document.getElementById(id);
  const storageKey = 'luisa-papers-v1';
  const pageSize = 8;
  // Keep these identical to the question library renderer in app.js.
  const mathMacros = {"\\p":"\\mathrm P(#1)",'\\cosec':'\\operatorname{cosec}','\\cosech':'\\operatorname{cosech}','\\sech':'\\operatorname{sech}','\\coth':'\\operatorname{coth}','\\arcosech':'\\operatorname{arcosech}','\\arcsech':'\\operatorname{arcsech}','\\arsech':'\\operatorname{arsech}','\\arcoth':'\\operatorname{arcoth}','\\arsinh':'\\operatorname{arsinh}','\\arcosh':'\\operatorname{arcosh}','\\artanh':'\\operatorname{artanh}','\\Real':'\\operatorname{Re}','\\Imag':'\\operatorname{Im}','\\ssum':'\\sum_{r=1}^{#1}#2','\\arraystretch':'1'};
  const catalogue = [], rows = new Map(), contentCache = new Map();
  // PAP-077-3: there is no separate PMT source; PMT questions are exam-style questions.
  const sources = ['practice', 'exam-style', 'madas', 'past-papers', 'old-spec'];
  const chapters = new Map(), books = new Map(), papers = new Map();
  let textbook;
  let selectionOrder = [];
  let selected = [], chosenTopics = new Set(), page = 0, browseOpen = false;
  let operation = null, browseOperation = null, printing = false, persistEnabled = false;
  // PAP-091: generator mode and timed target; NAV-091: account preferences and separate teacher drafts.
  const timing = window.LUISA_PAPERS_TIMING, resume = window.LUISA_RESUME;
  let migrations = new Map();
  let generateMode = 'count', timedOffer = null, activeDraft = 'practice', drafts = {practice: null, exam: null};
  let resolveRestored; const restored = new Promise(resolve => { resolveRestored = resolve; });
  const DEFAULT_MINUTES = '30';
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
  const sourceLabel = row => ['past-exam', 'pmt', 'madas', 'old-spec'].includes(row.sourceKind) ? `Source: ${row.sourceLabel.replace(/^Source:\s*/i, '')}` : row.sourceKind === 'practice-booklet'
    ? `Source: Practice Booklet · Chapter ${row.chapterNumber} · ${row.subchapterLabel || row.subchapterTitle} · ${/^\d/.test(row.questionLabel) ? 'Q' : ''}${row.questionLabel}`
    : `Source: Luisa ${row.skillCode} Q${row.number}`;
  const showTopicContext = row => row.sourceKind !== 'madas' && !(row.sourceKind === 'past-exam' && row.paperCode?.startsWith('8'));
  const contextLabel = row => `${row.courseTitle} · ${row.bookTitle} · ${row.topicTitle}`;
  const printLayout = () => $('papers-condensed').checked ? 'condensed' : 'one';
  const draftOf = () => ({selected: selected.map(row => row.id), selectionOrder: [...selectionOrder], order: $('papers-order').value});
  function paperState() {
    const state = {
      version: 4, sources: Object.fromEntries(sources.map(source => [source, $('papers-source-' + source).checked])),
      pastPaper: $('papers-past-paper').value, difficulty: $('papers-difficulty').value,
      layout: printLayout(), includeAnswers: $('papers-answers').checked, order: $('papers-order').value,
      selected: selected.map(row => row.id), selectionOrder, course: $('papers-course').value,
      book: $('papers-book').value, chapters: [...chosenTopics], count: $('papers-count').value,
      mode: generateMode, minutes: $('papers-minutes').value, draft: activeDraft
    };
    // The inactive teacher draft is kept beside the active one, never merged into it.
    const other = activeDraft === 'exam' ? 'practice' : 'exam';
    if (drafts[other]) state.drafts = {[other]: drafts[other]};
    return state;
  }
  function persist() {
    if (!persistEnabled) return;
    const state = paperState();
    try { sessionStorage.setItem(storageKey, JSON.stringify(state)); }
    catch (_) { $('papers-selection-note').textContent = 'Your selection is held on this page. Browser session storage is unavailable.'; }
    // Only the user's own changes reach account storage, so startup defaults never replace newer choices.
    if (resume?.touched()) resume.save('papers', state);
  }
  function difficultyBucket(value) {
    return ({standard: 'medium', hard: 'difficult', 'very-hard': 'very-difficult'})[value] || value || 'unclassified';
  }
  function sourceMatches(row, includeMadas) {
    const difficulty = $('papers-difficulty').value;
    const paper = $('papers-past-paper').disabled ? '' : $('papers-past-paper').value;
    if (paper === 'old-spec-revision' && row.bank !== 'old-spec') return false;
    return (row.bank === 'madas' && includeMadas !== undefined ? includeMadas : $('papers-source-' + row.bank).checked) &&
      (!difficulty || (row.difficulty || 'unclassified') === difficulty) &&
      (!['past-papers', 'old-spec'].includes(row.bank) || !paper || row.paperId === paper);
  }
  function inHierarchy(chapter) {
    const course = $('papers-course').value, book = $('papers-book').value;
    return (!course || chapter.course === course) && (!book || chapter.bookKey === book);
  }
  function matchingChapters(row) {
    return row.chapterKeys.filter(key => inHierarchy(chapters.get(key)) && (!chosenTopics.size || chosenTopics.has(key)));
  }
  let examFilter = null, examMadas = false, examRowCheck = null;
  function pool(includeMadas, filter = null) {
    const eligible = catalogue.filter(row => (!filter || filter(row)) && sourceMatches(row, includeMadas) && matchingChapters(row).length);
    return preferOldSpec(eligible);
  }
  const visiblePool = () => pool(examFilter ? examMadas : undefined, examFilter);
  // Use the converted solution and marking table when both copies pass the filters.
  function preferOldSpec(eligible) {
    const aliases = new Set(eligible.filter(row => row.bank === 'old-spec' && row.canonicalId).map(row => row.canonicalId));
    return eligible.filter(row => !aliases.has(row.id));
  }
  function options(id, label, choices, wanted = '') {
    const select = $(id);
    select.replaceChildren(new Option(label, ''), ...choices.map(([value, title]) => new Option(title, value)));
    select.value = choices.some(([value]) => value === wanted) ? wanted : '';
  }
  function refreshFilters() {
    const topics = [...chapters.values()].filter(inHierarchy);
    const idsByChapter = new Map();
    for (const row of catalogue) if ((!examFilter || examFilter(row)) && sourceMatches(row, examFilter ? examMadas : undefined)) for (const key of row.chapterKeys) {
      if (!idsByChapter.has(key)) idsByChapter.set(key, new Set());
      idsByChapter.get(key).add(row.canonicalId || row.id);
    }
    $('papers-topics').replaceChildren(...topics.map(t => {
      const label = element('label', undefined, 'topic-choice');
      const input = document.createElement('input');
      input.type = 'checkbox'; input.value = t.key; input.checked = chosenTopics.has(t.key);
      const text = element('span', `${t.id}. ${t.title}`);
      const count = `${(idsByChapter.get(t.key)?.size || 0).toLocaleString()} questions`;
      text.append(element('small', $('papers-book').value ? count : `${t.bookTitle} · ${count}`));
      label.append(input, text);
      return label;
    }));
    markActive();
    updatePool();
  }
  function refreshBooks(wanted) {
    const course = $('papers-course').value;
    const available = [...books].filter(([, book]) => !course || book.course === course);
    options('papers-book', 'All books', available.map(([key, book]) => [key, book.title]), wanted);
  }
  // The past-paper dropdown lists only papers with a question in the chosen course/book, and is
  // disabled (and reset to All) while Past Papers is unticked (PAP-068-1, PAP-068-3).
  let paperChoices = [];
  function relevantPapers() {
    const oldSpec = $('papers-source-old-spec').checked;
    const regular = $('papers-source-past-papers').checked || !oldSpec;
    const relevant = new Set();
    for (const row of catalogue) if (((row.bank === 'past-papers' && regular) || (row.bank === 'old-spec' && oldSpec)) && !relevant.has(row.paperId)
      && row.chapterKeys.some(key => inHierarchy(chapters.get(key)))) relevant.add(row.paperId);
    return relevant;
  }
  function refreshPapers(wanted = $('papers-past-paper').value) {
    const ticked = $('papers-source-past-papers').checked || $('papers-source-old-spec').checked, relevant = relevantPapers();
    options('papers-past-paper', 'All past papers', paperChoices.filter(([id]) => relevant.has(id)), ticked ? wanted : '');
    $('papers-past-paper').disabled = !ticked || !relevant.size;
  }
  // Filter dropdowns on anything but "All" carry the active style (PAP-068-2).
  function markActive() {
    for (const id of ['papers-past-paper', 'papers-difficulty', 'papers-course', 'papers-book']) {
      const select = $(id);
      select.classList.toggle('filter-active', select.value !== '');
    }
  }
  // "In paper order" exists only while one individual past paper is chosen (PAP-063).
  const singlePaper = () => (!$('papers-past-paper').disabled && $('papers-past-paper').value) || '';
  function refreshOrder() {
    const select = $('papers-order'), paper = singlePaper();
    let option = select.querySelector('option[value="paper"]');
    if (paper && !option) {
      option = document.createElement('option'); option.value = 'paper'; option.textContent = 'In paper order'; select.append(option);
    } else if (!paper && option) {
      if (select.value === 'paper') select.value = 'topic';
      option.remove();
    }
  }
  function paperOrder(a, b) {
    const paper = singlePaper(), inA = a.paperId === paper, inB = b.paperId === paper;
    if (inA && inB) return a.questionNumber - b.questionNumber;
    if (inA !== inB) return inA ? -1 : 1;
    return selectionOrder.indexOf(a.id) - selectionOrder.indexOf(b.id);
  }
  function orderedChapter(row) {
    return chapters.get(matchingChapters(row)[0] || row.chapterKeys[0]);
  }
  // PAP-075-6 safety net: drop a copy whose original is also in these rows. Since v0.77 (PAP-077-1/2) the bank
  // holds no copies, so this removes nothing and the "skips N copies" note does not appear.
  function withoutDuplicateCopies(rows) {
    const ids = new Set(rows.map(row => row.id));
    const seen = new Set();
    return rows.filter(row => {
      const key = row.canonicalId || row.id;
      if (seen.has(key) || (row.duplicateOf && ids.has(row.duplicateOf))) return false;
      seen.add(key);
      return true;
    });
  }
  function duplicateNote() {
    const ids = new Set(selected.map(row => row.id));
    const pairs = selected.filter(row => row.duplicateOf && ids.has(row.duplicateOf));
    return pairs.length ? ` ${pairs.length === 1 ? 'One selected question is a copy' : `${pairs.length} selected questions are copies`} of another selected question (${pairs.map(row => sourceLabel(row).replace(/^Source: /, '')).join('; ')}).` : '';
  }
  function updatePool() {
    cancelLoading();
    clearOffer();
    const count = visiblePool().length;
    $('filter-title').textContent = `${count.toLocaleString()} questions in the selection`;
    $('papers-count').max = String(count);
    page = 0; updateControls(); persist(); timeEligibility();
    if (browseOpen) renderBrowse();
  }
  function printSnapshot() {
    const ordered = [...selected];
    if ($('papers-order').value === 'topic') ordered.sort((a,b) => orderedChapter(a).rank - orderedChapter(b).rank);
    if ($('papers-order').value === 'paper') ordered.sort(paperOrder);
    return Object.freeze(ordered.map(row => Object.freeze({...row, printChapter: orderedChapter(row)})));
  }
  // Narrow hook for the teacher-only exam paper (papers-exam.js), which uses the same selection.
  window.LUISA_PAPERS_BUILDER = Object.freeze({
    snapshot: printSnapshot, busy: () => Boolean(operation) || printing, status,
    async run(task) {
      if (!selected.length || operation || printing) return;
      printing = true; updateControls();
      try { return await task(); } finally { printing = false; updateControls(); }
    },
    // PAP-066: the timed exam generator draws from exactly the generator's pool.
    pool: includeMadas => pool(includeMadas),
    setExamFilter(filter, includeMadas, rowCheck = null) {
      examFilter = filter; examMadas = includeMadas; examRowCheck = filter ? rowCheck : null;
      refreshFilters();
    },
    // NAV-091: teacher practice and exam drafts are separate. Switching saves the current draft and opens
    // the other one; `validate` keeps only questions that are still usable there, in their order.
    restored,
    mode: () => activeDraft,
    switchDraft,
    validateDraft,
    withoutDuplicateCopies,
    // PAP-091-6: the whole-question Pearson mark total (undefined when it cannot be verified).
    practiceMarks: html => practiceMarks(html),
    // Runs a task with the builder locked (generate, add/remove and print disabled), even
    // when nothing is selected yet. Returns undefined when the builder is already busy.
    async exclusive(task) {
      if (operation || printing) return undefined;
      printing = true; updateControls();
      try { return await task(); } finally { printing = false; updateControls(); }
    },
    // Loads descriptors that are complete; failures are counted rather than aborting the run.
    async load(descriptors, progress) {
      const loaded = []; let failed = 0;
      for (const descriptor of descriptors) {
        try { loaded.push(await loadRow(descriptor)); } catch (_) { failed++; }
        if (progress && (loaded.length + failed) % 50 === 0) progress(loaded.length + failed);
      }
      return Object.assign(loaded, {failed});
    },
    // Replace or reorder the selection in an explicit order; printed "As selected".
    arrange(rows, message) {
      if (operation || printing) return false;
      selected = withoutDuplicateCopies(preferOldSpec(rows)); selectionOrder = selected.map(row => row.id);
      $('papers-order').value = 'selection';
      updateSelection();
      if (message) status(message);
      return true;
    }
  });
  function updateControls() {
    const busy = Boolean(operation) || printing;
    $('papers-generate').disabled = busy || !visiblePool().length;
    $('papers-regenerate').disabled = busy || !selected.length || !visiblePool().length;
    $('papers-clear').disabled = busy || !selected.length;
    $('papers-print').disabled = busy || !selected.length || !window.LUISA_PAPERS_PRINT;
    $('papers-cancel').hidden = !operation;
    $('papers-time-accept').disabled = busy;
    $('papers-generate').textContent = generateMode === 'time' ? 'Generate timed paper' : 'Generate paper';
    $('papers-selected').setAttribute('aria-busy', String(Boolean(operation)));
    document.querySelectorAll('[data-add], [data-remove]').forEach(button => { button.disabled = busy; });
    document.dispatchEvent(new CustomEvent('luisa-papers-state'));
  }
  function cancelLoading(announce = true) {
    if (!operation) return;
    operation.abort(); operation = null; updateControls();
    if (announce) status('Loading cancelled. Your previous paper has been kept.');
  }
  // PAP-091-6: the part an allocation belongs to. Two printed Pearson layouts are verified against the
  // source booklets: (1) one combined allocation after the last subpart, with no allocation on any earlier
  // subpart, belongs to the parent part (for example (b)(i)–(ii) "(4 marks)"); (2) an allocation printed at
  // the end of the prose between two lists belongs to the first part of the next list when that part has
  // none of its own. Anything else keeps the allocation where it is, so incomplete trees stay ambiguous.
  function owningPart(mark, marks) {
    const has = node => marks.some(other => node.contains(other));
    const part = mark.closest('li');
    if (part) {
      const parent = part.parentElement?.closest('li');
      const siblings = [...part.parentElement.children].filter(node => node.matches('li'));
      if (parent && siblings.length > 1 && siblings.at(-1) === part && siblings.slice(0, -1).every(node => !has(node)) &&
          [...part.querySelectorAll('li')].every(node => !has(node))) return parent;
      return part;
    }
    let next = mark.nextSibling;
    while (next && next.nodeType === 3 && !next.textContent.trim()) next = next.nextSibling;
    let previous = mark.previousSibling, afterList = false;
    for (; previous; previous = previous.previousSibling) if (previous.nodeType === 1 && previous.matches('ol, ul')) { afterList = true; break; }
    const first = next?.nodeType === 1 && next.matches('ol, ul') ? [...next.children].find(node => node.matches('li')) : null;
    return afterList && first && !has(first) ? first : null;
  }
  function practiceMarks(html) {
    const prompt = document.createElement('template');
    prompt.innerHTML = html;
    const marks = [...prompt.content.querySelectorAll('.marks')];
    if (!marks.length) return undefined;
    const amounts = marks.map(mark => /^\((\d+) marks?\)$/i.exec(mark.textContent.trim()));
    if (amounts.some(amount => !amount)) return undefined;
    const total = amounts.reduce((sum, amount) => sum + Number(amount[1]), 0);
    const table = marks[0].closest('.practice-layout-table');
    if (table && marks.every(mark => mark.closest('.practice-layout-table') === table)) {
      const cells = [...table.querySelectorAll('td')];
      const complete = cells.length === marks.length && cells.every((cell, index) =>
        marks[index].closest('td') === cell && cell.firstElementChild?.matches('strong') &&
        cell.firstElementChild.textContent.trim() === String.fromCharCode(97 + index) + '.');
      return complete ? total : undefined;
    }
    const parts = marks.map(mark => owningPart(mark, marks));
    if (marks.length === 1 && !marks[0].closest('li')) return Number(amounts[0][1]);
    const marked = new Set(parts);
    if (marked.has(null) || marked.size !== marks.length) return undefined;
    // A part can carry a combined allocation for its children, or all children
    // can carry their own allocations. A partially marked tree is ambiguous.
    for (const part of marked) {
      if ([...part.querySelectorAll('li')].some(child => marked.has(child))) return undefined;
      for (let branch = part; branch; branch = branch.parentElement.closest('li')) {
        const siblings = [...branch.parentElement.children].filter(sibling => sibling.matches('li'));
        const covered = siblings.every(sibling => marked.has(sibling) ||
          [...sibling.querySelectorAll('li')].some(child => marked.has(child)));
        if (!covered) return undefined;
      }
    }
    return total;
  }
  async function loadRow(descriptor, signal) {
    if (rows.has(descriptor.id)) return rows.get(descriptor.id);
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    const practice = ['practice-booklet', 'past-exam', 'pmt', 'madas', 'old-spec'].includes(descriptor.sourceKind);
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
    if (question.workedSolutionSteps !== undefined && (!Array.isArray(question.workedSolutionSteps) ||
        question.workedSolutionSteps.some(step => typeof step !== 'string' || !step.trim()))) {
      throw Error('This question has invalid worked solution steps.');
    }
    const marks = descriptor.sourceKind === 'practice-booklet' ? practiceMarks(question.question) : descriptor.marks;
    if (descriptor.bank === 'old-spec' && (!Array.isArray(question.markSchemeSteps) || !question.markSchemeSteps.length)) throw Error('This Old Spec mark scheme is incomplete.');
    const row = Object.freeze({...descriptor, marks, workedSolutionSteps: question.workedSolutionSteps, markSchemeSteps: question.markSchemeSteps, schemeNote: question.schemeNote || null, question: question.question, contextHtml: question.contextHtml || '', steps: Object.freeze([...question.steps]), hints: Object.freeze([...(question.hints || [])]), source: Object.freeze({kind: practice ? descriptor.sourceKind : 'skill-question', courseId: descriptor.courseId, bookId: descriptor.bookId, topicId: descriptor.topicId, skillId: descriptor.skillId || null, questionId: question.id || null, questionNumber: ['past-exam', 'pmt', 'madas', 'old-spec'].includes(descriptor.sourceKind) ? descriptor.questionNumber : practice ? descriptor.questionLabel : question.number, chapterId: descriptor.chapterId || null, subchapterId: descriptor.subchapterId || null, practiceBookletQuestionId: descriptor.sourceKind === 'practice-booklet' ? descriptor.id : null})});
    rows.set(row.id, row); return row;
  }
  function questionMetadata(row) {
    if (row.bank === 'old-spec') {
      const grade = row.difficulty[0].toUpperCase() + row.difficulty.slice(1);
      return [row.marks + ' marks', 'Difficulty: ' + grade, row.difficultyReason].join(' · ');
    }
    return [Number.isInteger(row.marks) && row.marks > 0 ? `${row.marks} marks` : '', row.difficulty ? `${(row.difficulty[0].toUpperCase() + row.difficulty.slice(1).replace('-', ' '))} · difficulty guide` : ''].filter(Boolean).join(' · ');
  }
  function fillPreview(container, row) {
    container.innerHTML = (row.contextHtml || '') + row.question;
    if (row.bank === 'old-spec' || row.sourceKind === 'past-exam') {
      const official = row.sourceKind === 'past-exam';
      const materials = [['Worked solution', official ? row.workedSolutionSteps : row.steps],
        ['Mark scheme', official ? row.steps : row.markSchemeSteps]];
      for (const [label, steps] of materials) {
        if (!steps?.length) continue;
        const details = element('details'), body = element('div');
        details.append(element('summary', label), body);
        container.append(details);
        details.addEventListener('toggle', () => {
          if (details.open && !body.childNodes.length) {
            body.innerHTML = steps.join('');
            renderMath(body);
          }
        });
      }
    }
    container.querySelectorAll('table').forEach(table => {
      if (table.closest('.math-table')) return;
      const scroll = element('div', undefined, 'math-table');
      scroll.tabIndex = 0;
      scroll.setAttribute('role', 'region');
      scroll.setAttribute('aria-label', 'Question table; scroll horizontally if needed');
      table.before(scroll); scroll.append(table);
    });
    window.LUISA_PAPERS_PRINT?.normaliseMarks?.(container);
    try { renderMath(container); }
    catch (_) { container.replaceChildren(element('p', 'This mathematical preview could not be rendered. Reload the page before printing.', 'preview-error')); }
    // Re-align the marks margin whenever wrapping changes (width, fonts or images).
    const placeMarks = window.LUISA_PAPERS_PRINT?.placeMarks;
    if (typeof placeMarks === 'function' && container.querySelector('.marks')) new ResizeObserver(() => placeMarks(container)).observe(container);
  }
  function updateSelection() {
    const currentIds = new Set(selected.map(r => r.id));
    selectionOrder = selectionOrder.filter(id => currentIds.has(id));
    const ordered = new Set(selectionOrder);
    selectionOrder.push(...selected.filter(r => !ordered.has(r.id)).map(r => r.id));
    if ($('papers-order').value === 'selection') selected.sort((a,b) => selectionOrder.indexOf(a.id)-selectionOrder.indexOf(b.id));
    if ($('papers-order').value === 'topic') selected.sort((a, b) => orderedChapter(a).rank - orderedChapter(b).rank);
    if ($('papers-order').value === 'paper') selected.sort(paperOrder);
    $('papers-selected-count').textContent = selected.length.toLocaleString();
    const known = selected.filter(r => Number.isInteger(r.marks) && r.marks > 0);
    const marks = known.reduce((n, r) => n + r.marks, 0);
    let summary = selected.length ? `${selected.length} questions` : '';
    if (known.length) summary += known.length === selected.length ? ` · ${marks} marks` : ` · ${marks} known marks (${known.length} of ${selected.length} questions)`;
    // Owner rule B (v0.65): any paper with a complete mark total states 6 minutes per 5 marks, rounded down.
    if (selected.length && known.length === selected.length && marks > 0) summary += ` · Time: ${Math.floor(marks * 6 / 5)} minutes`;
    $('papers-summary').textContent = summary + duplicateNote();
    $('papers-empty').hidden = Boolean(selected.length);
    $('papers-selected').replaceChildren(...selected.map(row => {
      const li = element('li', undefined, 'selected-item');
      const details = document.createElement('details');
      const summary = element('summary', sourceLabel(row));
      if (showTopicContext(row)) summary.append(element('small', `${contextLabel(row)} · ${row.skillTitle}`));
      summary.append(element('small', questionMetadata(row), 'question-meta'));
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
  async function setSelection(descriptors, message, resetOrder = false) {
    descriptors = withoutDuplicateCopies(preferOldSpec(descriptors));
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
      selected = next; if (resetOrder) selectionOrder = next.map(r => r.id); operation = null; updateSelection(); status(message);
    } catch (error) {
      if (operation !== controller) return;
      operation = null; updateControls();
      if (error.name !== 'AbortError') status(error.message || 'The questions could not be loaded. Try again.', true);
    }
  }
  function generate() {
    if (operation || printing) return;
    // PAP-075-6: a PMT copy is never generated alongside its original (the original is kept).
    const candidates = withoutDuplicateCopies(visiblePool()), count = Number($('papers-count').value);
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
    setSelection(next, `${count} questions selected. Review your paper or choose Preview & print.${count === candidates.length ? ' Every question in this pool is included.' : ''}`, true);
  }
  // ---- PAP-091: timed student papers ----
  const plural = (count, word) => `${count.toLocaleString()} ${word}${count === 1 ? '' : 's'}`;
  const knownMarks = row => Number.isInteger(row?.marks) && row.marks > 0;
  // A Pearson booklet descriptor has no marks until its content is loaded; it is checked, never guessed.
  const markable = row => knownMarks(rows.get(row.id) || row) || (row.sourceKind === 'practice-booklet' && !rows.has(row.id));
  const timedEligible = row => knownMarks(row) && (!examRowCheck || examRowCheck(row));
  const minutesInput = () => Number($('papers-minutes').value);
  function timeReport(text, isError = false) {
    $('papers-time-report').textContent = text;
    $('papers-time-report').classList.toggle('error', Boolean(isError));
    $('papers-time-report').hidden = !text;
  }
  function clearOffer(message) {
    if (!timedOffer) return;
    timedOffer = null; $('papers-time-accept').hidden = true;
    if (message !== undefined) timeReport(message);
  }
  function timeEligibility() {
    if (!timing) return;
    const candidates = withoutDuplicateCopies(visiblePool());
    const known = candidates.filter(row => timedEligible(rows.get(row.id) || row)).length;
    const unchecked = candidates.filter(row => row.sourceKind === 'practice-booklet' && !rows.has(row.id)).length;
    $('papers-time-eligible').textContent = !known && !unchecked ? 'The current filters contain no questions with a known mark total.'
      : `${plural(known, 'question')} with a known mark total` + (unchecked ? `, and ${plural(unchecked, 'Pearson question')} whose mark total is checked when you generate.` : '.');
  }
  function syncPresets() {
    const minutes = $('papers-minutes').value;
    document.querySelectorAll('[data-minutes]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.minutes === minutes)));
  }
  function setMode(mode, {focus = false} = {}) {
    generateMode = mode === 'time' && timing ? 'time' : 'count';
    document.querySelectorAll('input[name="papers-generate-mode"]').forEach(input => { input.checked = input.value === generateMode; });
    // First use of By time preselects 30 minutes.
    if (generateMode === 'time' && !timing.validMinutes(minutesInput())) $('papers-minutes').value = DEFAULT_MINUTES;
    $('papers-count-field').hidden = generateMode === 'time'; $('papers-count-help').hidden = generateMode === 'time';
    $('papers-count').required = generateMode === 'count';
    for (const id of ['papers-time-fields', 'papers-time-help', 'papers-time-eligible']) $(id).hidden = generateMode !== 'time';
    if (generateMode !== 'time') { clearOffer(); timeReport(''); }
    syncPresets(); updateControls();
    if (focus) (generateMode === 'time' ? document.querySelector('[data-minutes][aria-pressed="true"]') || $('papers-minutes') : $('papers-count')).focus();
  }
  const timedSummary = plan => `${plural(plan.rows.length, 'question')} · ${plan.marks} marks · estimated time ${plan.minutes} minutes`;
  function applyTimed(rowsInOrder, message) {
    selected = withoutDuplicateCopies(preferOldSpec(rowsInOrder)); selectionOrder = selected.map(row => row.id);
    // The generated order is kept through preview and print until the student changes it.
    $('papers-order').value = 'selection';
    updateSelection(); status(message);
  }
  async function generateTimed() {
    if (operation || printing || !timing) return;
    const minutes = minutesInput();
    if (!timing.validMinutes(minutes)) {
      timeReport('Choose a whole number of minutes from 2 to 600.', true); $('papers-minutes').focus(); return;
    }
    clearOffer();
    const candidates = withoutDuplicateCopies(visiblePool()).filter(markable);
    if (!candidates.length) { timeReport('The current filters contain no questions with a known mark total. Add sources or topics, or generate by number of questions.', true); return; }
    const controller = new AbortController(); operation = controller; updateControls();
    const signature = visiblePool().map(row => row.id).join('|') + '#' + minutes;
    timeReport(`Checking mark totals for ${plural(candidates.length, 'question')}…`);
    const loaded = []; let failed = 0;
    try {
      for (const descriptor of candidates) {
        if (examRowCheck || descriptor.sourceKind === 'practice-booklet' || rows.has(descriptor.id)) {
          try { loaded.push(await loadRow(descriptor, controller.signal)); }
          catch (error) { if (error.name === 'AbortError') throw error; failed++; }
          if ((loaded.length + failed) % 100 === 0) timeReport(`Checking mark totals: ${loaded.length + failed} of ${candidates.length}…`);
        } else loaded.push(descriptor);
      }
      if (operation !== controller) return;
      const plan = timing.plan(loaded, minutes, {eligible: timedEligible});
      const note = failed ? ` ${plural(failed, 'question')} could not be loaded and ${failed === 1 ? 'was' : 'were'} left out.` : '';
      const drawn = ` Drawn from ${plural(plan.available, 'question')} with a known mark total.`;
      if (!plan.available) { operation = null; updateControls(); timeEligibility(); timeReport('The current filters contain no questions with a known mark total. Add sources or topics, or generate by number of questions.' + note, true); return; }
      if (!plan.timeMet) {
        operation = null; updateControls(); timeEligibility();
        const reason = plan.availableMarks * 6 / 5 < minutes - timing.tolerance
          ? `These filters have ${plural(plan.available, 'question')} with a known mark total, ${plan.availableMarks} marks in all, so the longest paper is about ${window.LUISA_PAPERS_PRINT.paperMinutes(plan.availableMarks)} minutes.`
          : `No set of whole questions in these filters is within ${timing.tolerance} minutes of ${minutes} minutes.`;
        timedOffer = {rows: plan.rows, signature, minutes: plan.minutes};
        $('papers-time-accept').textContent = `Use ${plan.minutes}-minute paper`;
        $('papers-time-accept').hidden = false;
        timeReport(`${reason} The closest paper is ${timedSummary(plan)}. Your current paper is unchanged until you choose Use ${plan.minutes}-minute paper.${note}`, true);
        return;
      }
      const ready = [];
      for (const row of plan.rows) ready.push(await loadRow(row, controller.signal));
      if (operation !== controller) return;
      operation = null;
      applyTimed(ready, `Timed paper selected for ${minutes} minutes: ${timedSummary(plan)}. Review it or choose Preview & print.`);
      timeEligibility();
      timeReport(`Target ${minutes} minutes: ${timedSummary(plan)}.${drawn}${note}`);
    } catch (error) {
      if (operation !== controller) return;
      operation = null; updateControls();
      if (error.name !== 'AbortError') timeReport((error.message || 'The timed paper could not be generated.') + ' Your current paper has been kept.', true);
    }
  }
  async function acceptOffer() {
    if (!timedOffer || operation || printing) return;
    const offer = timedOffer, signature = visiblePool().map(row => row.id).join('|') + '#' + minutesInput();
    if (signature !== offer.signature) { clearOffer('The filters or target changed, so that paper is no longer offered. Generate again.'); return; }
    clearOffer();
    const controller = new AbortController(); operation = controller; updateControls();
    try {
      const ready = [];
      for (const row of offer.rows) ready.push(await loadRow(row, controller.signal));
      if (operation !== controller) return;
      operation = null;
      const marks = ready.reduce((sum, row) => sum + row.marks, 0);
      applyTimed(ready, `${offer.minutes}-minute paper selected: ${plural(ready.length, 'question')} · ${marks} marks.`);
      timeReport(`Using the ${offer.minutes}-minute paper: ${plural(ready.length, 'question')} · ${marks} marks · estimated time ${offer.minutes} minutes.`);
    } catch (error) {
      if (operation !== controller) return;
      operation = null; updateControls();
      if (error.name !== 'AbortError') timeReport((error.message || 'That paper could not be loaded.') + ' Your current paper has been kept.', true);
    }
  }
  // ---- PAP-091-10: Reset in the paper builder ----
  function resetFilters() {
    // A pupil returns to the course of their current class; teachers and the owner keep their course scope.
    const course = resume?.defaultCourse || $('papers-course').value;
    for (const source of sources) $('papers-source-' + source).checked = ['practice', 'exam-style', 'past-papers'].includes(source);
    $('papers-difficulty').value = '';
    if ([...$('papers-course').options].some(option => option.value === course)) $('papers-course').value = course;
    refreshBooks('');
    chosenTopics.clear();
    refreshPapers('');
    const order = $('papers-order').value;
    refreshOrder(); refreshFilters();
    if (order === 'paper') updateSelection();
    clearOffer(); timeReport('');
    status('Question filters reset. Your paper, generator settings and print options are unchanged.');
  }
  // ---- NAV-091: separate teacher practice and exam drafts ----
  const catalogueRow = id => catalogue.find(row => row.id === id);
  async function loadDraft(draft, validate) {
    const ids = Array.isArray(draft?.selected) ? draft.selected.filter(id => typeof id === 'string') : [];
    const missing = ids.filter(id => !catalogueRow(migrations.get(id) || id));
    const descriptors = [...new Set(ids.map(id => migrations.get(id) || id))].map(catalogueRow).filter(Boolean);
    const order = Array.isArray(draft?.selectionOrder) ? draft.selectionOrder.map(id => migrations.get(id) || id) : descriptors.map(row => row.id);
    descriptors.sort((a, b) => (order.indexOf(a.id) + 1 || Infinity) - (order.indexOf(b.id) + 1 || Infinity));
    const loadedRows = [], omitted = [...missing.map(id => 'ID ' + id)];
    for (const descriptor of descriptors) {
      try {
        const row = await loadRow(descriptor);
        if (validate && !validate(row)) omitted.push(sourceLabel(row).replace(/^Source: /, '')); else loadedRows.push(row);
      } catch (_) { omitted.push(sourceLabel(descriptor).replace(/^Source: /, '')); }
    }
    return {rows: loadedRows, omitted, order: ['topic', 'selection', 'paper'].includes(draft?.order) ? draft.order : 'selection'};
  }
  function omittedNote(omitted, where) {
    return omitted.length ? ` ${omitted.length === 1 ? 'One saved question was' : `${omitted.length} saved questions were`} omitted from ${where} because ${omitted.length === 1 ? 'it is' : 'they are'} no longer usable there: ${omitted.join('; ')}.` : '';
  }
  async function switchDraft(name, validate) {
    if (!['practice', 'exam'].includes(name) || name === activeDraft) return false;
    if (operation || printing) return false;
    drafts[activeDraft] = draftOf();
    const target = drafts[name] || (name === 'exam' ? draftOf() : {selected: [], selectionOrder: [], order: 'selection'});
    activeDraft = name; drafts[name] = null;
    const controller = new AbortController(); operation = controller; updateControls();
    status(name === 'exam' ? 'Opening your exam draft…' : 'Opening your practice paper…');
    try {
      const result = await loadDraft(target, validate);
      if (operation !== controller) return false;
      operation = null;
      selected = result.rows; selectionOrder = result.rows.map(row => row.id);
      if ([...$('papers-order').options].some(option => option.value === result.order)) $('papers-order').value = result.order;
      updateSelection();
      status((name === 'exam' ? `Exam draft: ${plural(selected.length, 'question')}.` : `Practice paper: ${plural(selected.length, 'question')}.`) + omittedNote(result.omitted, name === 'exam' ? 'the exam draft' : 'the practice paper'));
      return true;
    } catch (error) {
      if (operation === controller) { operation = null; updateControls(); }
      status(error.message || 'The draft could not be opened.', true);
      return false;
    }
  }
  // Re-check a restored draft against the current rules, keeping the remaining order.
  function validateDraft(validate, where = 'the exam draft') {
    const omitted = selected.filter(row => !validate(row));
    if (!omitted.length) return [];
    selected = selected.filter(validate); updateSelection();
    status(omittedNote(omitted.map(row => sourceLabel(row).replace(/^Source: /, '')), where).trim());
    return omitted;
  }
  async function renderBrowse() {
    browseOperation?.abort();
    const controller = new AbortController(); browseOperation = controller;
    const candidates = visiblePool(), total = Math.ceil(candidates.length / pageSize);
    page = Math.min(page, Math.max(0, total - 1));
    $('papers-browser').hidden = false;
    $('papers-previous').disabled = page === 0;
    $('papers-next').disabled = page + 1 >= total;
    $('papers-page').textContent = total ? `Page ${page + 1} of ${total} · ${candidates.length.toLocaleString()} questions` : 'No questions in this pool';
    const target = $('papers-questions'); target.setAttribute('aria-busy', 'true');
    target.replaceChildren(element('p', candidates.length ? 'Loading question previews…' : 'Change the source, difficulty or topics to find questions.'));
    try {
      const loaded = [];
      for (const row of candidates.slice(page * pageSize, (page + 1) * pageSize)) loaded.push(await loadRow(row, controller.signal));
      if (browseOperation !== controller) return;
      if (loaded.length) target.replaceChildren(...loaded.map(row => {
        const card = element('article', undefined, 'question-card');
        card.append(element('h3', sourceLabel(row), 'source-label'));
        if (showTopicContext(row)) card.append(element('p', `${contextLabel(row)} · ${row.skillTitle}`, 'question-context'));
        card.append(element('p', questionMetadata(row), 'question-meta'));
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
    textbook = await response.json();
    if (!Array.isArray(textbook.questions) || !textbook.questions.length) throw new Error('The Edexcel catalogue is unavailable. Reload the page to try again.');
    const courseTitles = new Map(textbook.courses.map(course => [course.id, course.title]));
    const bookKeys = new Map();
    for (const book of textbook.books) {
      const bookKey = book.course + '/' + book.id;
      bookKeys.set(book.id, bookKey);
      books.set(bookKey, book);
      for (const chapter of book.chapters) {
        const key = bookKey + '/' + chapter.id;
        chapters.set(key, {...chapter, key, bookKey, rank: chapters.size, course: book.course,
          courseTitle: courseTitles.get(book.course), bookTitle: book.title});
      }
    }
    const ids = new Set();
    function add(row, keys) {
      row.difficulty = difficultyBucket(row.difficulty);
      // PAP-074-1: every question carries its derived mark-scheme flag.
      if (!['official', 'source', 'editorial', 'worked', 'none'].includes(row.markScheme)) throw Error('A question has no mark-scheme classification: ' + row.id + '. Reload the page to retry.');
      if (ids.has(row.id) || !Array.isArray(keys) || !keys.length || keys.some(key => !chapters.has(key))) {
        throw Error('Invalid chapter association for ' + row.id + '. Reload the page to retry.');
      }
      ids.add(row.id);
      const chapterKeys = [...new Set(keys)].sort((a,b) => chapters.get(a).rank - chapters.get(b).rank);
      catalogue.push(Object.freeze({...row, chapterKeys: Object.freeze(chapterKeys)}));
    }
    // The source skill retains its library identity, even for cross-book targets.
    const eligible = new Map(textbook.questions.map(q => [q.skill + '/' + q.question, q]));
    for (const course of window.FMQ_LIBRARY.courses) for (const book of course.books) for (const topic of book.topics) for (const skill of topic.skills) {
      if (skill.reference || skill.available === false) continue;
      for (const question of skill.questions) {
        const entry = eligible.get(skill.id + '/' + question.number), targets = entry?.targets;
        if (question.reference || !targets) continue;
        const id = [course.id,book.id,topic.id,skill.id,'q' + question.number].join('/');
        add({id, sourceKind: 'luisa', bank: 'practice', difficulty: null, number: question.number, markScheme: entry.markScheme,
          courseId: course.id, bookId: book.id, topicId: topic.id, skillId: skill.id,
          courseTitle: course.title, bookTitle: book.title, topicTitle: topic.title, skillCode: skill.code, skillTitle: skill.title},
          targets.map(target => bookKeys.get(target.book) + '/' + target.chapter));
      }
    }
    if (ids.size !== eligible.size) throw Error('Some Edexcel questions could not be found in the question library.');
    const practiceResponse = await fetch(new URL('practice-catalogue.json', document.baseURI));
    if (!practiceResponse.ok) throw new Error('The Practice Booklet catalogue could not be loaded. Check your connection and reload.');
    const practiceCatalogue = await practiceResponse.json();
    if (practiceCatalogue.version !== 1 || !Array.isArray(practiceCatalogue.questions)) throw new Error('The Practice Booklet catalogue is invalid.');
    for (const q of practiceCatalogue.questions) {
      if (!q.id?.startsWith('practice/') || !/^content\/practice\/[a-z0-9/-]+\.json$/.test(q.dataPath) || !q.chapterNumber || !q.subchapterId || !q.subchapterTitle || !q.questionLabel || q.board !== 'Edexcel') throw new Error('A Practice Booklet source is incomplete or unverified.');
      if (!['practice','exam'].includes(q.bank || 'practice') || ![null,undefined,'easy','medium','difficult'].includes(q.difficulty)) throw new Error('A question classification is invalid.');
      const key = [q.courseId,q.bookId,q.chapterNumber].join('/');
      const chapter = chapters.get(key);
      if (chapter?.title !== q.chapterTitle) throw Error('Invalid Practice Booklet chapter for ' + q.id);
      add({...q, bank: q.bank === 'exam' ? 'exam-style' : 'practice', sourceKind: 'practice-booklet',
        courseTitle: chapter.courseTitle, bookTitle: chapter.bookTitle, topicTitle: chapter.title, skillTitle: q.subchapterTitle}, [key]);
    }
    const examResponse = await fetch(new URL('exam-catalogue.json', document.baseURI));
    if (!examResponse.ok) throw new Error('The past-paper catalogue could not be loaded. Check your connection and reload.');
    const examCatalogue = await examResponse.json();
    if (examCatalogue.version !== 1 || !Array.isArray(examCatalogue.questions)) throw new Error('The past-paper catalogue is invalid.');
    for (const q of examCatalogue.questions) {
      if (!q.id?.startsWith('exam/') || !/^content\/exams\/[a-z0-9-]+\.json$/.test(q.dataPath) || !q.sourceLabel || !q.paperId || !q.paperCode || !q.session ||
          q.board !== 'Edexcel' || q.status !== 'checked' || !Number.isInteger(q.marks) || q.marks <= 0 || !['easy','medium','difficult'].includes(q.difficulty)) throw Error('A past-exam question is incomplete or unverified.');
      const chapter = chapters.get(q.chapterKeys?.[0]);
      if (!chapter) throw Error('Invalid past-paper chapter for ' + q.id);
      papers.set(q.paperId, {session: q.session, code: q.paperCode, date: q.examDate || q.seriesDate || ''});
      add({...q, sourceKind: 'past-exam', bank: 'past-papers', courseTitle: chapter.courseTitle,
        bookTitle: chapter.bookTitle, topicTitle: chapter.title, skillTitle: q.topicSummary || ''}, q.chapterKeys);
    }
    // PAP-075/PAP-077-3: PMT Core Pure revision questions (topic sheets with their source mark schemes) are
    // exam-style questions; there is no separate source box.
    const pmtResponse = await fetch(new URL('pmt-catalogue.json', document.baseURI));
    if (!pmtResponse.ok) throw new Error('The PMT catalogue could not be loaded. Check your connection and reload.');
    const pmtCatalogue = await pmtResponse.json();
    if (pmtCatalogue.version !== 1 || !Array.isArray(pmtCatalogue.questions)) throw new Error('The PMT catalogue is invalid.');
    for (const q of pmtCatalogue.questions) if (q.duplicateOf && q.duplicateOf === q.id) throw Error('A PMT question is marked as a copy of itself.');
    for (const q of pmtCatalogue.questions) {
      if (!q.id?.startsWith('pmt/') || !/^content\/pmt\/[a-z0-9-]+\.json$/.test(q.dataPath) || !q.sourceLabel || q.board !== 'PMT' || q.status !== 'checked' ||
          !Number.isInteger(q.marks) || q.marks <= 0 || !['easy','medium','difficult'].includes(q.difficulty)) throw Error('A PMT question is incomplete or unverified.');
      const chapter = chapters.get(q.chapterKeys?.[0]);
      if (!chapter) throw Error('Invalid PMT chapter for ' + q.id);
      add({...q, sourceKind: 'pmt', bank: 'exam-style', courseTitle: chapter.courseTitle,
        bookTitle: chapter.bookTitle, topicTitle: chapter.title, skillTitle: q.topicSummary || ''}, q.chapterKeys);
    }
    const madasResponse = await fetch(new URL('madas-catalogue.json', document.baseURI));
    if (!madasResponse.ok) throw Error('The MADAS catalogue could not be loaded.');
    const madas = await madasResponse.json();
    if (madas.version !== 1 || !Array.isArray(madas.questions)) throw Error('Invalid MADAS catalogue.');
    for (const q of madas.questions) {
      const chapter = chapters.get(q.chapterKeys?.[0]);
      if (!chapter || !q.id.startsWith('madas/') || !/^content\/madas\/[a-z-]+\.json$/.test(q.dataPath) ||
          !Number.isInteger(q.marks) || q.marks < 1 || !['standard', 'hard', 'very-hard'].includes(q.difficulty)) throw Error('Invalid MADAS question: ' + q.id);
      add({...q, sourceKind: 'madas', bank: 'madas', courseTitle: chapter.courseTitle, bookTitle: chapter.bookTitle,
        topicTitle: chapter.title, skillTitle: q.topicSummary}, q.chapterKeys);
    }
    const oldResponse = await fetch(new URL('old-spec-catalogue.json', document.baseURI));
    if (!oldResponse.ok) throw Error('The Old Spec catalogue could not be loaded.');
    const oldSpec = await oldResponse.json();
    if (oldSpec.version !== 1 || !Array.isArray(oldSpec.questions)) throw Error('Invalid Old Spec catalogue.');
    for (const q of oldSpec.questions) {
      const chapter = chapters.get(q.chapterKeys?.[0]);
      if (!chapter || !q.id.startsWith('old-spec/') || !/^content\/old-spec\/rev\d\d\.json$/.test(q.dataPath) ||
          (q.canonicalId && !ids.has(q.canonicalId)) || !q.difficultyReason?.trim() || !['easy','medium','difficult'].includes(q.difficulty)) throw Error('Invalid Old Spec question: ' + q.id);
      add({...q, sourceLabel: q.sourceLabel + ' · ' + q.id.split('/')[1].toUpperCase(), sourceKind: 'old-spec', bank: 'old-spec', bookTitle: chapter.bookTitle,
        courseTitle: chapter.courseTitle, topicTitle: chapter.title, bookId: chapter.bookKey.split('/')[1],
        courseId: chapter.course, chapterId: chapter.id}, q.chapterKeys);
    }
    // A copy may point at a past-paper question or at another PMT question; both must exist once everything is loaded.
    for (const q of pmtCatalogue.questions) if (q.duplicateOf && !ids.has(q.duplicateOf)) throw Error('A PMT question is marked as a copy of a missing question.');
    // PAP-077-1: a removed duplicate maps to the question kept in its place (an official past paper or the earlier PMT question).
    migrations = new Map(Object.entries({...practiceCatalogue.migrations, ...pmtCatalogue.migrations, ...madas.migrations}).filter(([from, to]) => !ids.has(from) && ids.has(to)));
    let saved = null;
    try { saved = JSON.parse(sessionStorage.getItem(storageKey)); } catch (_) { /* A new session or unavailable storage. */ }
    // NAV-091: this tab's own state wins; a new sign-in or another device starts from the account's latest Papers state.
    if (![1, 2, 3, 4].includes(saved?.version)) saved = resume?.get('papers') || null;
    if (![1, 2, 3, 4].includes(saved?.version)) saved = null;
    if (saved?.version === 4 && saved.draft === 'exam' && document.getElementById('papers-exam')) activeDraft = 'exam';
    if (saved?.version === 4 && saved.drafts && typeof saved.drafts === 'object') for (const name of ['practice', 'exam']) {
      const draft = saved.drafts[name];
      if (name !== activeDraft && draft && Array.isArray(draft.selected)) drafts[name] = draft;
    }
    for (const source of sources) {
      // A version-2 session had one 'exam' box for exam-style and past papers. A saved 'pmt' box (v0.75-v0.76) is ignored (PAP-077-3).
      const key = saved?.version === 2 && ['exam-style', 'past-papers'].includes(source) ? 'exam' : source;
      $('papers-source-' + source).checked = saved?.sources?.[key] ?? (!['madas', 'old-spec'].includes(source));
    }
    paperChoices = [...papers].sort(([,a],[,b]) => b.date.localeCompare(a.date) || a.code.localeCompare(b.code))
      .map(([id, paper]) => {
        const part = paper.code.split('/').at(-1);
        const applied = {'21': '2 Statistics', '22': '2 Mechanics', '31': '3 Statistics', '32': '3 Mechanics'};
        const number = applied[part] || part.replace(/^0/, '');
        const qualification = (paper.code.startsWith('8') ? 'AS ' : '') + (paper.code.includes('FM0') ? 'Further Maths' : 'Maths');
        return [id, paper.session + ' Paper ' + number + ' (' + qualification + ' · ' + paper.code + ')'];
      });
    paperChoices.push(['old-spec-revision', oldSpec.group]);
    if (saved?.difficulty) {
      const bucket = difficultyBucket(saved.difficulty);
      if ([...$('papers-difficulty').options].some(option => option.value === bucket)) $('papers-difficulty').value = bucket;
    }
    $('papers-condensed').checked = saved?.layout === 'condensed';
    if (typeof saved?.includeAnswers === 'boolean') $('papers-answers').checked = saved.includeAnswers;
    // An explicit saved course (including All courses) wins; otherwise a pupil starts with their class's course.
    const savedCourse = saved?.version === 4 && typeof saved.course === 'string' ? saved.course : saved?.course || resume?.defaultCourse || '';
    options('papers-course', 'All courses', textbook.courses.map(c => [c.id, c.title]), savedCourse);
    refreshBooks(saved?.book);
    refreshPapers(saved?.pastPaper);
    refreshOrder();
    if (saved?.order === 'selection' || (saved?.order === 'paper' && singlePaper())) $('papers-order').value = saved.order;
    const migrated = saved && saved.version < 3 && (saved.topic || saved.topics?.length || saved.skills?.length);
    if (migrated) $('papers-selection-note').textContent = 'The old topic or skill restriction has been reset for textbook topics. Your saved paper is kept.';
    chosenTopics = new Set((Array.isArray(saved?.chapters) ? saved.chapters : [])
      .filter(key => chapters.has(key) && inHierarchy(chapters.get(key))));
    if (saved?.count && /^\d+$/.test(saved.count)) $('papers-count').value = saved.count;
    if (typeof saved?.minutes === 'string' && /^\d{1,3}$/.test(saved.minutes) && timing?.validMinutes(Number(saved.minutes))) $('papers-minutes').value = saved.minutes;
    // A first visit, or a legacy session without a saved mode, generates by number of questions.
    setMode(saved?.version === 4 && saved.mode === 'time' ? 'time' : 'count');
    refreshFilters();
    persistEnabled = true;
    for (const id of [...sources.map(source => 'papers-source-' + source), 'papers-past-paper', 'papers-difficulty']) {
      $(id).addEventListener('change', () => {
        refreshPapers();
        const order = $('papers-order').value;
        refreshOrder(); refreshFilters();
        if (order === 'paper') updateSelection();
      });
    }
    for (const id of ['papers-condensed','papers-answers']) $(id).addEventListener('change', persist);
    $('papers-order').addEventListener('change', updateSelection);
    const hierarchyChanged = () => {
      const order = $('papers-order').value;
      chosenTopics.clear(); refreshPapers(); refreshOrder(); refreshFilters();
      if (order === 'paper') updateSelection();
    };
    $('papers-course').addEventListener('change', () => { refreshBooks(); hierarchyChanged(); });
    $('papers-book').addEventListener('change', hierarchyChanged);
    $('papers-topics').addEventListener('change', event => {
      if (event.target.checked) chosenTopics.add(event.target.value); else chosenTopics.delete(event.target.value);
      updatePool();
    });
    $('papers-all-topics').addEventListener('click', () => { chosenTopics.clear(); refreshFilters(); });
    $('papers-count').addEventListener('change', persist);
    document.querySelectorAll('input[name="papers-generate-mode"]').forEach(input => input.addEventListener('change', () => { if (input.checked) { setMode(input.value); persist(); } }));
    document.querySelectorAll('[data-minutes]').forEach(button => button.addEventListener('click', () => {
      $('papers-minutes').value = button.dataset.minutes; syncPresets(); clearOffer(); timeReport(''); persist();
    }));
    $('papers-minutes').addEventListener('input', () => { syncPresets(); clearOffer(); timeReport(''); persist(); });
    $('papers-time-accept').addEventListener('click', acceptOffer);
    $('papers-reset').addEventListener('click', resetFilters);
    // Generate and Regenerate use the current mode, target and filters.
    const run = () => generateMode === 'time' ? generateTimed() : generate();
    $('papers-generate-form').addEventListener('submit', event => { event.preventDefault(); run(); });
    $('papers-regenerate').addEventListener('click', run);
    $('papers-cancel').addEventListener('click', () => cancelLoading());
    $('papers-clear').addEventListener('click', () => { if (operation || printing) return; selected = []; updateSelection(); status('Paper cleared. Choose questions to start again.'); });
    $('papers-browse').addEventListener('click', () => { browseOpen = true; renderBrowse(); });
    $('papers-previous').addEventListener('click', () => { page--; renderBrowse(); });
    $('papers-next').addEventListener('click', () => { page++; renderBrowse(); });
    $('papers-questions').addEventListener('click', event => {
      const button = event.target.closest('[data-add]'); if (!button || operation || printing) return;
      const row = rows.get(button.dataset.add); if (!row) return;
      if (selected.some(q => q.id === row.id)) selected = selected.filter(q => q.id !== row.id); else selected = [...selected.filter(q => (q.canonicalId || q.id) !== (row.canonicalId || row.id)), row];
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
      const snapshot = printSnapshot();
      printing = true; updateControls(); status('Preparing the print preview…');
      try {
        const result = await window.LUISA_PAPERS_PRINT.create(snapshot, {layout: printLayout(), includeAnswers: $('papers-answers').checked});
        if (result?.ready === false) status(`The preview needs attention before printing. ${(result.warnings || []).join(' ')}`, true);
        else status(result?.warnings?.length ? `Print preview ready. ${result.warnings.join(' ')}` : 'Print preview ready in a new window. Use its Print / Save PDF button.');
      } catch (error) { status(error.message || 'The print preview could not be opened. Allow pop-ups for this site and try again.', true); }
      finally { printing = false; updateControls(); }
    });
    for (const id of [...sources.map(source => 'papers-source-' + source), 'papers-difficulty', 'papers-course', 'papers-book', 'papers-all-topics', 'papers-count', 'papers-generate', 'papers-browse', 'papers-reset', 'papers-minutes']) $(id).disabled = false;
    document.querySelectorAll('input[name="papers-generate-mode"]').forEach(input => { input.disabled = !timing; });
    if (resume && !migrated) $('papers-selection-note').textContent = resume.edition === 'ada' ? 'Your paper and filters are saved to your account and reopen when you next sign in.' : 'Your paper and filters are remembered in this browser.';
    updateControls();
    // PAP-077-1: a saved selection is migrated once: each removed duplicate becomes the question kept in its place,
    // keeping its position, and a question chosen twice this way is kept once. The new IDs are saved on restore.
    const migrate = id => migrations.get(id) || id;
    const savedList = Array.isArray(saved?.selected) ? saved.selected.filter(id => typeof id === 'string') : [];
    const replaced = savedList.filter(id => migrations.has(id)).length;
    const savedIds = new Set(savedList.map(migrate));
    const byId = new Map(catalogue.map(row => [row.id, row]));
    const restoredRows = [...savedIds].map(id => byId.get(id)).filter(Boolean);
    const retired = [...savedIds].filter(id => !byId.has(id));
    selectionOrder = Array.isArray(saved?.selectionOrder) ? [...new Set(saved.selectionOrder.map(migrate).filter(id => savedIds.has(id)))] : [...savedIds];
    const retiredNote = retired.length ? ` ${retired.length === 1 ? 'One saved question is' : `${retired.length} saved questions are`} no longer available and ${retired.length === 1 ? 'was' : 'were'} omitted (ID ${retired.join('; ID ')}); the rest keep their order.` : '';
    if (restoredRows.length) {
      // The saved order is restored as it was; the generator does not run.
      await setSelection(restoredRows, `${restoredRows.length} questions restored${resume ? '' : ' from this browser session'}.` +
        (replaced ? ` ${replaced === 1 ? 'One duplicate question was' : `${replaced} duplicate questions were`} replaced by the same question from its original source.` : '') + retiredNote);
    } else { persist(); status(retiredNote.trim() || `${withoutDuplicateCopies(catalogue).length.toLocaleString()} Edexcel-filtered worked questions available. Choose topics to begin.`, Boolean(retiredNote)); }
    resolveRestored();
  } catch (error) {
    status(error.message || 'The paper builder could not start. Reload the page to retry.', true);
    for (const id of ['papers-generate', 'papers-regenerate', 'papers-print', 'papers-browse']) $(id).disabled = true;
  }
})();
