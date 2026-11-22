/* Teacher-only exam paper (PAP-065C). Owner and ADA staff editions only: the pupil
   build removes this file, its stylesheet and the builder controls that load it. */
(() => {
  'use strict';
  const print = window.LUISA_PAPERS_PRINT;
  if (!print?.internals) return;
  const {element, whileOpen, asset, content, prepare, overflows, wideContent, splitBlock} = print.internals;
  const storageKey = 'luisa-papers-exam-v1';
  const defaultInstructions = [
    'Calculators may be used.',
    'Mathematical formulae booklet is provided. Answer all questions and ensure that your answers to parts of questions are clearly labelled.',
    'Should you use additional paper, make sure that question number is clearly labelled',
    'Answers should be given to three significant figures unless otherwise stated.'
  ].join('\n\n');
  const gravityHtml = 'Unless otherwise indicated, wherever a value of <span data-math="g"></span> is required, take <span data-math="g = 9.8\\,\\mathrm{m\\,s^{-2}}"></span>';
  const extraMinutes = minutes => Math.round(minutes * 0.25);
  const plural = (count, word) => `${count} ${word}${count === 1 ? '' : 's'}`;
  const monthYear = (date = new Date()) => date.toLocaleDateString('en-GB', {month: 'long', year: 'numeric'});

  function courseGroup(row) {
    if (row.sourceKind === 'past-exam' && row.paperCode) {
      const part = row.paperCode.split('/').at(-1);
      if (row.paperCode.startsWith('9FM0')) return 'Core';
      return {'31': 'Statistics', '32': 'Mechanics'}[part] || 'Pure';
    }
    const book = row.printChapter?.bookTitle || row.bookTitle || '';
    if (/mechanic/i.test(book)) return 'Mechanics';
    if (/statistic/i.test(book)) return 'Statistics';
    if (/core/i.test(book)) return 'Core';
    if (/pure/i.test(book)) return 'Pure';
    return book || row.courseTitle || 'Other';
  }
  const listNumbers = numbers => numbers.length === 1 ? String(numbers[0]) : numbers.slice(0, -1).join(', ') + ' and ' + numbers.at(-1);
  // One line per course in question order; omitted when every question shares a course.
  function courseMap(rows) {
    const groups = new Map();
    rows.forEach((row, index) => {
      const group = courseGroup(row);
      if (!groups.has(group)) groups.set(group, []);
      groups.get(group).push(index + 1);
    });
    if (groups.size < 2) return '';
    return [...groups].map(([group, numbers]) => `${numbers.length === 1 ? 'Question' : 'Questions'} ${listNumbers(numbers)} ${numbers.length === 1 ? 'is' : 'are'} from ${group}`).join('\n');
  }
  const hasMechanics = rows => rows.some(row => courseGroup(row) === 'Mechanics');
  function paperTotals(rows) {
    const unknown = rows.filter(row => !Number.isInteger(row.marks) || row.marks <= 0);
    const marks = rows.reduce((sum, row) => sum + (Number.isInteger(row.marks) ? row.marks : 0), 0);
    const minutes = print.paperMinutes(marks);
    return {unknown, marks, minutes, extra: minutes === null ? null : extraMinutes(minutes)};
  }

  function frontPage(doc, rows, options, totals) {
    const sheet = element(doc, 'section', 'print-page exam-front-page');
    sheet.setAttribute('aria-label', 'Front page');
    const name = element(doc, 'p', 'exam-name');
    name.append('Name: ', element(doc, 'span', 'exam-blank exam-name-blank'));
    const heading = element(doc, 'div', 'exam-title-block');
    heading.append(element(doc, 'h1', 'exam-title', [options.yearGroup, options.title].map(v => (v || '').trim()).filter(Boolean).join(' ')),
      element(doc, 'p', 'exam-month', (options.monthYear || '').trim()));
    if ((options.date || '').trim()) {
      const date = element(doc, 'p', 'exam-date');
      date.append(element(doc, 'strong', '', 'Date:'), ' ' + options.date.trim());
      heading.append(date);
    }
    const time = element(doc, 'div', 'exam-time-block');
    const line = (label, ...parts) => { const p = element(doc, 'p'); p.append(element(doc, 'strong', '', label), ...parts); time.append(p); return p; };
    line('Time:', ` ${totals.minutes} minutes `, element(doc, 'span', 'exam-extra', `(+${totals.extra} minutes extra time)`)).className = 'exam-time';
    line('Total marks available:', ` ${totals.marks}`).className = 'exam-marks-available';
    line('Total marks achieved:', ' ', element(doc, 'span', 'exam-blank exam-achieved-blank')).className = 'exam-marks-achieved';
    const notes = element(doc, 'div', 'exam-instructions');
    for (const paragraph of (options.instructions ?? defaultInstructions).split(/\n\s*\n/).map(text => text.trim()).filter(Boolean)) {
      const p = element(doc, 'p');
      paragraph.split('\n').forEach((text, index) => { if (index) p.append(element(doc, 'br')); p.append(text); });
      notes.append(p);
    }
    if (hasMechanics(rows)) {
      const gravity = element(doc, 'p', 'exam-gravity');
      gravity.innerHTML = gravityHtml;
      notes.append(gravity);
    }
    const map = (options.courseMap ?? courseMap(rows)).split('\n').map(text => text.trim()).filter(Boolean);
    if (map.length) {
      const list = element(doc, 'div', 'exam-course-map');
      for (const text of map) {
        const p = element(doc, 'p'), match = /^(.*\b(?:is|are) from )(.+)$/i.exec(text);
        if (match) p.append(match[1], element(doc, 'strong', '', match[2])); else p.append(text);
        list.append(p);
      }
      notes.append(list);
    }
    sheet.append(name, element(doc, 'hr', 'exam-rule'), heading, element(doc, 'hr', 'exam-rule'), time,
      element(doc, 'div', 'exam-spacer'), element(doc, 'hr', 'exam-rule'), notes);
    return sheet;
  }

  async function create(rows, options = {}) {
    if (!Array.isArray(rows) || !rows.length) throw Error('Select at least one question first.');
    if (new Set(rows.map(row => row.id)).size !== rows.length) throw Error('A paper cannot contain duplicate questions.');
    if (rows.some(row => !row.id || !row.question)) throw Error('Every selected question needs its original prompt.');
    const totals = paperTotals(rows);
    if (totals.unknown.length) throw Error(`An exam paper needs the marks for every question. Remove the ${plural(totals.unknown.length, 'question')} without known marks, then try again.`);
    const previewURL = new URL('paper-preview.html', document.baseURI);
    const win = window.open(previewURL.href, '_blank');
    if (!win) throw Error('Allow pop-ups for Luisa to open the paper preview.');
    await whileOpen(win, new Promise((resolve, reject) => {
      const loaded = () => {
        try {
          if (!win.document.querySelector('meta[name="luisa-paper-preview"]')) reject(Error('The paper preview could not open. Sign in or reconnect, then try again.'));
          else resolve();
        } catch (_) { reject(Error('The paper preview could not open. Please try again.')); }
      };
      win.addEventListener('load', loaded, {once: true});
      if (win.location.href === previewURL.href && win.document.readyState === 'complete') loaded();
    }));
    const doc = win.document;
    doc.open();
    doc.write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Exam Paper</title></head><body></body></html>');
    doc.close();
    const base = element(doc, 'base'); base.href = document.baseURI; doc.head.append(base);
    const toolbar = element(doc, 'aside', 'print-toolbar');
    const status = element(doc, 'p', 'print-status', 'Preparing the exam paper…'); status.setAttribute('role', 'status');
    const printButton = element(doc, 'button', '', 'Print / Save PDF'); printButton.type = 'button'; printButton.disabled = true;
    const close = element(doc, 'button', 'secondary', 'Close preview'); close.type = 'button'; close.onclick = () => win.close();
    toolbar.append(element(doc, 'strong', '', 'Luisa · Exam paper'), status, printButton, close); doc.body.append(toolbar);
    const pages = element(doc, 'main', 'print-pages exam-paper marks-pending'); pages.setAttribute('aria-label', 'Exam paper'); doc.body.append(pages);
    let ready = false;
    win.addEventListener('beforeprint', () => doc.body.classList.toggle('not-ready', !ready));
    try {
      await whileOpen(win, Promise.all([asset(doc, 'link', 'papers-print.css'), asset(doc, 'link', 'papers-exam.css'), asset(doc, 'link', 'vendor/katex.min.css'), asset(doc, 'script', 'vendor/katex.min.js')]));
      const front = frontPage(doc, rows, options, totals);
      const staging = element(doc, 'div', 'print-staging exam-staging marks-pending'); doc.body.append(staging);
      const rendered = rows.map(row => {
        const prompt = print.normaliseMarks(content(doc, (row.sourceKind === 'past-exam' ? '' : row.contextHtml || '') + row.question));
        staging.append(prompt);
        return {row, prompt};
      });
      staging.append(front);
      await whileOpen(win, prepare(win, staging, status), 120000);
      pages.append(front);
      const warnings = [];
      if (overflows(front)) warnings.push('The front page instructions and course map do not fit on one page. Shorten them, then create a new preview.');
      const questionPages = [];
      function newPage() {
        const sheet = element(doc, 'section', 'print-page exam-page');
        const body = element(doc, 'div', 'page-content');
        const footer = element(doc, 'footer', 'page-footer exam-footer');
        footer.append(element(doc, 'span', 'page-number'));
        sheet.append(body, footer); pages.append(sheet); questionPages.push(sheet);
        return body;
      }
      function heading(row, number, continuation) {
        const head = element(doc, 'header', 'question-heading compact-heading exam-heading');
        head.append(element(doc, 'h2', '', 'Q' + number + (continuation ? ' · continued' : '')));
        if (!continuation) head.append(element(doc, 'strong', 'question-marks', '[' + row.marks + ' Marks]'));
        return head;
      }
      function answerLines(body) {
        const lines = element(doc, 'div', 'answer-lines'); lines.setAttribute('aria-label', 'Lined answer space');
        // Vector rules exactly 8 mm apart (mm user units avoid pixel snapping), clipped to the space left.
        const svg = doc.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'answer-rules'); svg.setAttribute('aria-hidden', 'true');
        for (let i = 1; i <= 38; i++) {
          const line = doc.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('class', 'answer-line');
          line.setAttribute('x1', '0'); line.setAttribute('x2', '100%');
          line.setAttribute('y1', `${8 * i}mm`); line.setAttribute('y2', `${8 * i}mm`);
          svg.append(line);
        }
        lines.append(svg); body.append(lines);
      }
      for (let i = 0; i < rendered.length; i++) {
        const {row, prompt} = rendered[i], number = i + 1;
        if (win.closed) throw Error('Paper preview was closed.');
        status.textContent = `Laying out questions: ${number} of ${rows.length}…`;
        await new Promise(resolve => window.setTimeout(resolve, 0));
        const queue = [...prompt.childNodes].filter(n => n.nodeType !== 3 || n.textContent.trim());
        const own = [];
        let body, section, holder, hasContent;
        const start = continuation => {
          body = newPage(); own.push(body);
          section = element(doc, 'article', 'print-question exam-question'); section.dataset.questionId = row.id;
          holder = element(doc, 'div', 'math-content');
          section.append(heading(row, number, continuation), holder); body.append(section);
          hasContent = false;
        };
        start(false);
        while (queue.length) {
          const block = queue.shift(); holder.append(block);
          if (!overflows(body) && !wideContent(holder)) { hasContent = true; continue; }
          block.remove();
          if (hasContent) { start(true); queue.unshift(block); continue; }
          const pieces = block.nodeType === 1 && splitBlock(block);
          if (pieces?.length > 1) { queue.unshift(...pieces); continue; }
          if (block.nodeType === 1) block.classList.add('compact');
          holder.append(block);
          if (overflows(body) || wideContent(holder)) warnings.push(`Question ${number} (${row.sourceLabel || row.id}) has an indivisible expression or figure that does not fit a full page at readable size.`);
          hasContent = true;
        }
        // Two pages per question; longer questions round up to an even count so each starts on an odd page.
        const finish = () => {
          while (own.length < 2 || own.length % 2) { const blank = newPage(); blank.parentElement.classList.add('exam-blank-page'); own.push(blank); }
          own.forEach((page, index) => { if (index >= own.indexOf(body)) answerLines(page); });
          const last = own.at(-1);
          last.append(element(doc, 'p', 'question-total', `(Total for Question ${number} is ${plural(row.marks, 'mark')})`));
          if (number === rows.length) last.append(element(doc, 'hr', 'paper-end-rule'), element(doc, 'p', 'paper-total', `TOTAL FOR PAPER IS ${totals.marks} MARKS`));
          return last;
        };
        let last = finish();
        if (overflows(last)) {
          // Content filled the final page: the totals move to the next pair of pages.
          last.querySelectorAll('.question-total, .paper-end-rule, .paper-total').forEach(node => node.remove());
          body = own.at(-1);
          for (let k = 0; k < 2; k++) { const blank = newPage(); blank.parentElement.classList.add('exam-blank-page'); own.push(blank); }
          own.forEach(page => page.querySelector('.answer-lines')?.remove());
          last = finish();
          if (overflows(last)) warnings.push(`Question ${number} totals do not fit on its final page.`);
        }
      }
      staging.remove();
      pages.classList.remove('marks-pending');
      print.placeMarks(pages);
      const total = questionPages.length;
      questionPages.forEach((sheet, index) => {
        sheet.querySelector('.page-number').textContent = `Page ${index + 1} of ${total}`;
        sheet.setAttribute('aria-label', `Exam paper, page ${index + 1} of ${total}`);
      });
      if (warnings.length) {
        doc.body.classList.add('not-ready');
        status.textContent = 'This exam paper cannot be printed completely. Remove or replace the listed questions, then create a new preview.';
        const list = element(doc, 'ul', 'print-errors'); [...new Set(warnings)].forEach(warning => list.append(element(doc, 'li', '', warning))); toolbar.append(list);
        return {window: win, pageCount: total, warnings: [...new Set(warnings)], ready: false};
      }
      ready = true;
      status.textContent = `${rows.length} questions · ${totals.marks} marks · ${totals.minutes} minutes · front page and ${total} A4 pages. Choose A4, 100% scale and turn off browser headers and footers in the print dialog.`;
      printButton.disabled = false; printButton.onclick = () => win.print();
      return {window: win, pageCount: total, warnings: [], ready: true};
    } catch (error) {
      if (!win.closed) { doc.body.classList.add('not-ready'); status.textContent = `Exam paper unavailable: ${error.message}`; }
      throw error;
    }
  }

  window.LUISA_PAPERS_EXAM = Object.freeze({create, courseMap, courseGroup, extraMinutes, defaultInstructions});

  // Builder controls (present only in owner and staff papers.html).
  const $ = id => document.getElementById(id);
  const builder = window.LUISA_PAPERS_BUILDER;
  if (!$('papers-exam') || !builder) return;
  const fields = {yearGroup: 'papers-exam-year', title: 'papers-exam-title', monthYear: 'papers-exam-month', date: 'papers-exam-date', instructions: 'papers-exam-instructions', courseMap: 'papers-exam-map'};
  let saved = {};
  try { saved = JSON.parse(sessionStorage.getItem(storageKey)) || {}; } catch (_) { saved = {}; }
  $('papers-exam-title').value = saved.title ?? 'Maths Assessment';
  $('papers-exam-year').value = saved.yearGroup ?? '';
  $('papers-exam-month').value = saved.monthYear ?? monthYear();
  $('papers-exam-date').value = saved.date ?? '';
  $('papers-exam-instructions').value = saved.instructions ?? defaultInstructions;
  let mapEdited = typeof saved.courseMap === 'string';
  if (mapEdited) $('papers-exam-map').value = saved.courseMap;
  function save() {
    const state = Object.fromEntries(Object.entries(fields).map(([key, id]) => [key, $(id).value]));
    if (!mapEdited) delete state.courseMap;
    try { sessionStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) { /* Optional convenience only. */ }
  }
  function refresh() {
    const rows = builder.snapshot();
    if (!mapEdited) $('papers-exam-map').value = courseMap(rows);
    const totals = paperTotals(rows);
    $('papers-exam-print').disabled = builder.busy() || !rows.length || Boolean(totals.unknown.length);
    $('papers-exam-summary').textContent = !rows.length ? 'Select questions to build an exam paper.'
      : totals.unknown.length ? `${plural(totals.unknown.length, 'selected question')} without known marks cannot go in an exam paper.`
      : `${plural(rows.length, 'question')} · ${totals.marks} marks · Time: ${totals.minutes} minutes (+${totals.extra} minutes extra time)${hasMechanics(rows) ? ' · g = 9.8 line included' : ''}`;
  }
  for (const id of Object.values(fields)) $(id).addEventListener('input', () => { if (id === fields.courseMap) mapEdited = true; save(); });
  $('papers-exam-map-reset').addEventListener('click', () => { mapEdited = false; save(); refresh(); });
  document.addEventListener('luisa-papers-state', refresh);
  $('papers-exam-print').addEventListener('click', () => builder.run(async () => {
    const rows = builder.snapshot();
    builder.status('Preparing the exam paper…');
    try {
      const options = Object.fromEntries(Object.entries(fields).map(([key, id]) => [key, $(id).value]));
      if (!mapEdited) options.courseMap = courseMap(rows);
      const result = await create(rows, options);
      if (result.ready === false) builder.status(`The exam paper needs attention before printing. ${result.warnings.join(' ')}`, true);
      else builder.status('Exam paper ready in a new window. Use its Print / Save PDF button.');
    } catch (error) { builder.status(error.message || 'The exam paper could not be opened. Allow pop-ups for this site and try again.', true); }
  }));
  refresh();
})();
