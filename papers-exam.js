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
      element(doc, 'p', 'exam-month', (options.monthYear || '').trim() || monthYear()));
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
      if (overflows(front)) warnings.push('The front page instructions do not fit on one page. Shorten them, then create a new preview.');
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
        // PAP-066-6: exam papers say "Question N"; other printouts keep "QN".
        head.append(element(doc, 'h2', '', 'Question ' + number + (continuation ? ' (continued)' : '')));
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

  // ---- PAP-066-1 and PAP-066-5: timed selection and difficulty order (exam paper only) ----
  const LABELS = ['easy', 'medium', 'difficult'];
  const bandOf = row => LABELS.includes(row.difficulty) ? row.difficulty : 'unrated';
  const topicOf = row => row.paperId ? `${row.paperId}:${(row.chapterKeys || [])[0] || ''}` : (row.chapterKeys || [])[0] || row.chapterId || row.skillId || row.bookId || row.id;
  const markedRows = rows => rows.filter(row => Number.isInteger(row.marks) && row.marks > 0);
  // Mark totals whose paper time is within ±1 minute of the target, nearest first.
  function targetMarks(minutes) {
    const out = [];
    for (let marks = 1; marks <= Math.ceil(minutes * 5 / 6) + 2; marks++) {
      const off = Math.abs(print.paperMinutes(marks) - minutes);
      if (off <= 1) out.push({marks, off});
    }
    return out.sort((a, b) => a.off - b.off || a.marks - b.marks).map(item => item.marks);
  }
  // A question belongs to the band holding its midpoint mark (cumulative from Question 1):
  // midpoint below 20% of the paper's marks = opening band, above 80% = closing band.
  function bandPositions(rows) {
    const total = rows.reduce((sum, row) => sum + row.marks, 0); let start = 0;
    return rows.map(row => { const mid = (start + row.marks / 2) / total; start += row.marks; return mid < 0.2 ? 'opening' : mid > 0.8 ? 'closing' : 'middle'; });
  }
  // Rule: every opening-band question is easy, every closing-band question is difficult,
  // and (for two or more questions) Question 1 is easy and the last question is difficult.
  function orderProblems(rows) {
    if (rows.length < 2 || markedRows(rows).length !== rows.length) return [];
    const problems = [], bands = bandPositions(rows);
    rows.forEach((row, index) => {
      const opening = bands[index] === 'opening' || index === 0, closing = bands[index] === 'closing' || index === rows.length - 1;
      if (opening && bandOf(row) !== 'easy') problems.push(`Question ${index + 1} is in the first 20% of marks but is ${bandOf(row)}, not easy.`);
      else if (closing && bandOf(row) !== 'difficult') problems.push(`Question ${index + 1} is in the last 20% of marks but is ${bandOf(row)}, not difficult.`);
    });
    return problems;
  }
  // Middle 60%: a varied mix, avoiding the same topic or difficulty twice in a row where possible.
  function vary(rows) {
    const left = [...rows], out = [];
    while (left.length) {
      const last = out.at(-1);
      let index = last ? left.findIndex(row => topicOf(row) !== topicOf(last) && bandOf(row) !== bandOf(last)) : 0;
      if (index < 0) index = left.findIndex(row => topicOf(row) !== topicOf(last));
      out.push(...left.splice(Math.max(index, 0), 1));
    }
    return out;
  }
  function orderByBands(rows) {
    const total = rows.reduce((sum, row) => sum + row.marks, 0);
    if (rows.length < 2 || !total) return [...rows];
    const easy = rows.filter(row => bandOf(row) === 'easy').sort((a, b) => b.marks - a.marks);
    const hard = rows.filter(row => bandOf(row) === 'difficult').sort((a, b) => b.marks - a.marks);
    const opening = [], closing = []; let head = 0, tail = 0;
    // Fill the opening band with easy questions until the next question's midpoint passes 20%.
    while (easy.length && (!opening.length || head + Math.min(...rows.filter(row => !opening.includes(row)).map(row => row.marks)) / 2 < total * 0.2)) {
      const fit = easy.findIndex(row => head + row.marks / 2 < total * 0.2);
      const row = easy.splice(fit < 0 ? easy.length - 1 : fit, 1)[0]; opening.push(row); head += row.marks;
      if (fit < 0) break;
    }
    while (hard.length && (!closing.length || tail + Math.min(...rows.filter(row => !opening.includes(row) && !closing.includes(row)).map(row => row.marks).concat([Infinity])) / 2 < total * 0.2)) {
      const fit = hard.findIndex(row => tail + row.marks / 2 < total * 0.2);
      const row = hard.splice(fit < 0 ? hard.length - 1 : fit, 1)[0]; closing.unshift(row); tail += row.marks;
      if (fit < 0) break;
    }
    let middle = vary(rows.filter(row => !opening.includes(row) && !closing.includes(row)));
    // The question after the opening band should be the one whose midpoint lands past 20%.
    const first = middle.findIndex(row => head + row.marks / 2 >= total * 0.2);
    if (first > 0) middle = [middle[first], ...vary(middle.filter((_, index) => index !== first))];
    const last = middle.findIndex(row => tail + row.marks / 2 >= total * 0.2 && row !== middle[0]);
    if (last >= 0 && last !== middle.length - 1) middle = [...middle.filter((_, index) => index !== last), middle[last]];
    return [...opening, ...middle, ...closing];
  }
  const shuffle = (rows, random) => { const out = [...rows]; for (let i = out.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [out[i], out[j]] = [out[j], out[i]]; } return out; };
  // New topics first, then the rest, so every subset prefers variety (priority c).
  function freshFirst(rows, used) { const seen = new Set(used); const a = [], b = []; for (const row of rows) { (seen.has(topicOf(row)) ? b : a).push(row); seen.add(topicOf(row)); } return [...a, ...b]; }
  function subsetWithSum(rows, wanted) {
    const parent = new Array(wanted + 1).fill(-1); parent[0] = -2;
    rows.forEach((row, index) => { for (let sum = wanted; sum >= row.marks; sum--) if (parent[sum] === -1 && parent[sum - row.marks] !== -1 && parent[sum - row.marks] !== index) parent[sum] = index; });
    if (parent[wanted] === -1) return null;
    const out = []; for (let sum = wanted; sum > 0; sum -= rows[parent[sum]].marks) out.push(rows[parent[sum]]);
    return out;
  }
  // Fill one band with whole questions whose midpoints stay inside its 20% of `marks`.
  function bandFill(rows, marks) { const out = []; let sum = 0; for (const row of rows) if (sum + row.marks / 2 < marks * 0.2 || !out.length) { if (sum + row.marks > marks * 0.45) continue; out.push(row); sum += row.marks; } return out; }
  function score(rows, minutes) {
    const marks = rows.reduce((sum, row) => sum + row.marks, 0), time = print.paperMinutes(marks) ?? 0;
    return {rows, marks, minutes: time, timeMiss: Math.max(0, Math.abs(time - minutes) - 1), offBy: Math.abs(time - minutes), bandProblems: orderProblems(rows).length, variety: new Set(rows.map(topicOf)).size};
  }
  const compare = (a, b) => a.timeMiss - b.timeMiss || a.bandProblems - b.bandProblems || b.variety - a.variety || a.offBy - b.offBy;
  const better = (a, b) => !b || compare(a, b) < 0;
  // Priorities when constraints conflict: (a) time within ±1 minute, (b) difficulty bands, (c) variety.
  function planTimedPaper(pool, minutes, {attempts = 240, random = Math.random} = {}) {
    if (!Number.isInteger(minutes) || minutes < 2 || minutes > 600) throw Error('Choose a whole number of minutes from 2 to 600.');
    const rows = markedRows(pool), counts = {easy: 0, medium: 0, difficult: 0, unrated: 0}, marksBy = {easy: 0, medium: 0, difficult: 0, unrated: 0};
    for (const row of rows) { counts[bandOf(row)]++; marksBy[bandOf(row)] += row.marks; }
    const report = {target: minutes, extraTarget: extraMinutes(minutes), available: rows.length, availableMarks: rows.reduce((sum, row) => sum + row.marks, 0), counts, marksBy, excluded: pool.length - rows.length};
    if (!rows.length) return {...report, ok: false, rows: [], reasons: ['None of the questions in the chosen topics has known marks, so no exam paper can be timed from them. Add Practice Booklet or past-paper sources.']};
    const goals = targetMarks(minutes); let best = null;
    for (let attempt = 0; attempt < attempts; attempt++) {
      const order = shuffle(rows, random);
      for (const marks of goals.slice(0, 3)) {
        const opening = bandFill(freshFirst(order.filter(row => bandOf(row) === 'easy'), []), marks);
        const closing = bandFill(freshFirst(order.filter(row => bandOf(row) === 'difficult' && !opening.includes(row)), opening.map(topicOf)), marks);
        const chosen = new Set([...opening, ...closing]), used = [...chosen].map(topicOf);
        const rest = marks - [...chosen].reduce((sum, row) => sum + row.marks, 0);
        const others = order.filter(row => !chosen.has(row));
        // Middle 60%: any difficulty (a varied mix), new topics first.
        const middlePool = freshFirst(others, used).slice(0, 160);
        let middle = rest > 0 ? subsetWithSum(middlePool, rest) : rest === 0 ? [] : null;
        if (!middle) { // Closest whole-question total: greedy fill below the goal.
          middle = []; let sum = 0;
          for (const row of middlePool) if (sum + row.marks <= Math.max(rest, 0)) { middle.push(row); sum += row.marks; }
        }
        let paper = [...opening, ...middle, ...closing];
        let total = paper.reduce((sum, row) => sum + row.marks, 0);
        if (total < marks) { for (const row of order) if (!paper.includes(row) && total + row.marks <= goals.at(-1)) { paper.push(row); total += row.marks; } }
        const candidate = score(orderByBands(paper), minutes);
        if (better(candidate, best)) best = candidate;
        if (!best.timeMiss && !best.bandProblems && !best.offBy && best.variety === best.rows.length) break;
      }
      if (best && !best.timeMiss && !best.bandProblems && attempt > 24) break;
    }
    const reasons = [];
    if (best.timeMiss) {
      reasons.push(report.availableMarks * 6 / 5 < minutes - 1
        ? `The chosen topics have ${plural(rows.length, 'question')} with known marks, ${report.availableMarks} marks in all, which is only ${print.paperMinutes(report.availableMarks)} minutes.`
        : `No combination of whole questions in the chosen topics gives ${minutes} ± 1 minutes; the nearest is ${best.minutes} minutes (${best.marks} marks).`);
    }
    if (best.bandProblems) {
      reasons.push(`The difficulty order cannot be met: the chosen topics have ${plural(counts.easy, 'easy question')} (${marksBy.easy} marks) and ${plural(counts.difficult, 'difficult question')} (${marksBy.difficult} marks), and the paper needs about ${Math.ceil(best.marks * 0.2)} marks of each.`);
      reasons.push(...orderProblems(best.rows));
    }
    return {...report, ok: !reasons.length, rows: best.rows, marks: best.marks, minutes: best.minutes, extra: extraMinutes(best.minutes), variety: best.variety, reasons};
  }

  window.LUISA_PAPERS_EXAM = Object.freeze({create, courseGroup, extraMinutes, defaultInstructions, targetMarks, bandPositions, orderProblems, orderByBands, planTimedPaper});

  // Builder controls (present only in owner and staff papers.html).
  const $ = id => document.getElementById(id);
  const builder = window.LUISA_PAPERS_BUILDER;
  if (!$('papers-exam') || !builder) return;
  const fields = {yearGroup: 'papers-exam-year', title: 'papers-exam-title', monthYear: 'papers-exam-month', date: 'papers-exam-date', instructions: 'papers-exam-instructions', targetMinutes: 'papers-exam-minutes'};
  let saved = {};
  try { saved = JSON.parse(sessionStorage.getItem(storageKey)) || {}; } catch (_) { saved = {}; }
  $('papers-exam-title').value = saved.title ?? 'Maths Assessment';
  $('papers-exam-year').value = saved.yearGroup ?? '';
  $('papers-exam-month').value = saved.monthYear ?? monthYear();
  $('papers-exam-date').value = saved.date ?? '';
  $('papers-exam-instructions').value = saved.instructions ?? defaultInstructions;
  $('papers-exam-minutes').value = saved.targetMinutes ?? '60';
  function save() {
    const state = Object.fromEntries(Object.entries(fields).map(([key, id]) => [key, $(id).value]));
    try { sessionStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) { /* Optional convenience only. */ }
  }
  let proposal = null;
  const report = $('papers-exam-target-report'), accept = $('papers-exam-accept');
  function showReport(text, isError) { report.textContent = text; report.classList.toggle('error', Boolean(isError)); report.hidden = !text; }
  function targetPreview() {
    const minutes = Number($('papers-exam-minutes').value);
    $('papers-exam-target-help').textContent = Number.isInteger(minutes) && minutes > 0
      ? `Target ${minutes} minutes (+${extraMinutes(minutes)} minutes extra time): about ${Math.ceil(minutes * 5 / 6)} marks, within ±1 minute.` : 'Enter a whole number of minutes.';
  }
  function refresh() {
    const rows = builder.snapshot();
    const totals = paperTotals(rows), busy = builder.busy();
    $('papers-exam-print').disabled = busy || !rows.length || Boolean(totals.unknown.length);
    $('papers-exam-generate').disabled = busy || !builder.pool().length;
    $('papers-exam-order').disabled = busy || rows.length < 2 || Boolean(totals.unknown.length);
    $('papers-exam-summary').textContent = !rows.length ? 'Select questions to build an exam paper.'
      : totals.unknown.length ? `${plural(totals.unknown.length, 'selected question')} without known marks cannot go in an exam paper.`
      : `${plural(rows.length, 'question')} · ${totals.marks} marks · Time: ${totals.minutes} minutes (+${totals.extra} minutes extra time)${hasMechanics(rows) ? ' · g = 9.8 line included' : ''}`;
    const problems = totals.unknown.length ? [] : orderProblems(rows);
    const warning = $('papers-exam-order-warning');
    warning.hidden = !problems.length;
    warning.textContent = problems.length ? `This order does not follow the exam difficulty order (easy first 20% of marks, difficult last 20%). ${problems.join(' ')}` : '';
    decorate(rows);
  }
  // Manual reordering: Move up/down on each selected question (teacher editions only).
  function decorate(rows) {
    const items = [...document.querySelectorAll('#papers-selected > li.selected-item')];
    items.forEach((li, index) => {
      if (li.querySelector('.exam-move')) return;
      const id = rows[index]?.id; if (!id) return;
      const group = document.createElement('span'); group.className = 'exam-move';
      for (const [label, delta] of [['Move up', -1], ['Move down', 1]]) {
        const button = document.createElement('button'); button.type = 'button'; button.className = 'quiet'; button.textContent = label;
        button.dataset.examMove = String(delta); button.dataset.id = id; button.disabled = builder.busy() || (delta < 0 ? index === 0 : index === rows.length - 1);
        button.setAttribute('aria-label', `${label}: question ${index + 1}`);
        group.append(button);
      }
      li.append(group);
    });
  }
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-exam-move]'); if (!button) return;
    const rows = [...builder.snapshot()], index = rows.findIndex(row => row.id === button.dataset.id), to = index + Number(button.dataset.examMove);
    if (index < 0 || to < 0 || to >= rows.length) return;
    [rows[index], rows[to]] = [rows[to], rows[index]];
    builder.arrange(rows, `Question moved to position ${to + 1}. Order is now As selected.`);
  });
  for (const id of Object.values(fields)) $(id).addEventListener('input', () => { save(); if (id === fields.targetMinutes) targetPreview(); });
  document.querySelectorAll('[data-exam-preset]').forEach(button => button.addEventListener('click', () => {
    $('papers-exam-minutes').value = button.dataset.examPreset; save(); targetPreview();
  }));
  $('papers-exam-order').addEventListener('click', () => {
    const rows = orderByBands(builder.snapshot());
    builder.arrange(rows, 'Questions ordered for the exam: easy questions first, a varied mix in the middle and difficult questions last.');
  });
  $('papers-exam-generate').addEventListener('click', async () => {
    const minutes = Number($('papers-exam-minutes').value);
    if (!Number.isInteger(minutes) || minutes < 2 || minutes > 600) { showReport('Choose a whole number of minutes from 2 to 600.', true); $('papers-exam-minutes').focus(); return; }
    proposal = null; accept.hidden = true; showReport('Loading the questions in the chosen topics…');
    $('papers-exam-generate').disabled = true;
    try {
      const descriptors = builder.pool().filter(row => ['practice-booklet', 'past-exam'].includes(row.sourceKind));
      const skipped = builder.pool().length - descriptors.length;
      const pool = await builder.load(descriptors, count => showReport(`Loading the questions in the chosen topics… ${count} of ${descriptors.length}`));
      const plan = planTimedPaper(pool, minutes);
      const note = skipped ? ` ${plural(skipped, 'question')} without marks in the chosen sources were left out.` : '';
      const summary = plan.rows.length ? `${plural(plan.rows.length, 'question')} · ${plan.marks} marks · ${plan.minutes} minutes (+${plan.extra} minutes extra time)` : '';
      if (plan.ok) {
        builder.arrange(plan.rows, `Timed exam paper selected: ${summary}. Review it, reorder if needed, or choose Preview exam paper.`);
        showReport(`Target ${minutes} minutes met: ${summary}, ordered easy to difficult.${note}`);
      } else {
        proposal = plan.rows;
        const timeMet = plan.rows.length && Math.abs(plan.minutes - minutes) <= 1;
        showReport(`${timeMet ? `Target ${minutes} minutes met, but not every exam rule.` : `Target ${minutes} minutes cannot be met exactly with these topics.`} ${plan.reasons.join(' ')}${summary ? ` Closest paper: ${summary}.` : ''} Add or change topics and generate again${summary ? ', or use the closest paper' : ''}.${note}`, true);
        accept.hidden = !plan.rows.length;
      }
    } catch (error) { showReport(error.message || 'The timed paper could not be generated.', true); }
    finally { refresh(); }
  });
  accept.addEventListener('click', () => {
    if (!proposal) return;
    if (builder.arrange(proposal, 'Closest timed paper selected. Review it or choose Preview exam paper.')) { proposal = null; accept.hidden = true; }
  });
  document.addEventListener('luisa-papers-state', refresh);
  $('papers-exam-print').addEventListener('click', () => builder.run(async () => {
    const rows = builder.snapshot();
    builder.status('Preparing the exam paper…');
    try {
      const options = Object.fromEntries(Object.entries(fields).map(([key, id]) => [key, $(id).value]));
      const result = await create(rows, options);
      if (result.ready === false) builder.status(`The exam paper needs attention before printing. ${result.warnings.join(' ')}`, true);
      else builder.status('Exam paper ready in a new window. Use its Print / Save PDF button.');
    } catch (error) { builder.status(error.message || 'The exam paper could not be opened. Allow pop-ups for this site and try again.', true); }
  }));
  targetPreview();
  refresh();
})();
