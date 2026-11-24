/* Teacher-only exam paper (PAP-065C). Owner and ADA staff editions only: the pupil
   build removes this file, its stylesheet and the builder controls that load it. */
(() => {
  'use strict';
  const print = window.LUISA_PAPERS_PRINT;
  if (!print?.internals) return;
  const {element, whileOpen, asset, content, prepare, overflows, wideContent, splitBlock} = print.internals;
  const storageKey = 'luisa-papers-exam-v1';
  const defaultInstructions = [
    'Calculators may be used and a formulae booklet is provided. Where specified, answers relying solely on technology will not receive credit.',
    'Give exact answers where requested and approximate numerical answers to three significant figures unless otherwise stated.',
    'Clearly label all answers, including those on additional paper, with the question number and part.'
  ].join('\n\n');
  // PAP-067-1: paper time within ±2 minutes of the target.
  const TOLERANCE = 2;
  // PAP-067-2: one print choice; questions only is the default.
  const CONTENTS = ['questions', 'scheme', 'both'];
  const gravityHtml = 'Unless otherwise indicated, wherever a value of <span data-math="g"></span> is required, take <span data-math="g = 9.8\\,\\mathrm{m\\,s^{-2}}"></span>';
  const extraMinutes = minutes => Math.round(minutes * 0.25);
  const plural = (count, word) => `${count} ${word}${count === 1 ? '' : 's'}`;
  // PAP-074-2: only questions with an official (or equivalent source) mark scheme may go in an exam paper.
  const hasMarkScheme = row => row.markScheme === 'official' || row.markScheme === 'source';
  // PAP-074-3 / PAP-075: a question page names no source. A context block keeps its content but loses its source label
  // (for example "Reference from 9.5 Q1"), whatever source the row comes from.
  const withoutSourceLabels = node => { node.querySelectorAll('.practice-context-label').forEach(label => label.remove()); return node; };
  // PAP-074-3: the scheme section names each question's exact source and bank ID; question pages never do.
  const schemeSource = row => `${print.sourceLabel(row)} · ID ${row.id}`;
  const monthYear = (date = new Date()) => date.toLocaleDateString('en-GB', {month: 'long', year: 'numeric'});
  // PAP-067-8: today in the teacher's local date (Europe/London), template style "Sunday 22nd November".
  function todayLabel(date = new Date()) {
    const part = type => new Intl.DateTimeFormat('en-GB', {timeZone: 'Europe/London', [type]: type === 'day' ? 'numeric' : 'long'}).format(date);
    const day = Number(part('day'));
    const suffix = day % 10 === 1 && day !== 11 ? 'st' : day % 10 === 2 && day !== 12 ? 'nd' : day % 10 === 3 && day !== 13 ? 'rd' : 'th';
    return `${part('weekday')} ${day}${suffix} ${part('month')}`;
  }
  // Printed date: ordinal suffixes after a day number are superscripted, as in the template.
  function appendDate(doc, parent, text) {
    let last = 0;
    for (const match of text.matchAll(/\b(\d{1,2})(st|nd|rd|th)\b/gi)) {
      parent.append(text.slice(last, match.index) + match[1], element(doc, 'sup', 'exam-ordinal', match[2]));
      last = match.index + match[0].length;
    }
    parent.append(text.slice(last));
  }

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
    const noScheme = rows.filter(row => !hasMarkScheme(row));
    const marks = rows.reduce((sum, row) => sum + (Number.isInteger(row.marks) ? row.marks : 0), 0);
    const minutes = print.paperMinutes(marks);
    return {unknown, noScheme, marks, minutes, extra: minutes === null ? null : extraMinutes(minutes)};
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
      date.append(element(doc, 'strong', '', 'Date:'), ' ');
      appendDate(doc, date, options.date.trim());
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
    const choice = options.content ?? 'questions';
    if (!CONTENTS.includes(choice)) throw Error('Choose Questions only, Mark scheme only or Questions and mark scheme.');
    const withQuestions = choice !== 'scheme', withScheme = choice !== 'questions';
    const totals = paperTotals(rows);
    if (totals.unknown.length) throw Error(`An exam paper needs the marks for every question. Remove the ${plural(totals.unknown.length, 'question')} without known marks, then try again.`);
    if (totals.noScheme.length) throw Error(`Every question in an exam paper needs an official mark scheme. Remove the ${plural(totals.noScheme.length, 'question')} marked "No mark scheme", then try again.`);
    if (withScheme && rows.some(row => !Array.isArray(row.steps) || !row.steps.length)) throw Error('Every selected question needs its mark scheme.');
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
    doc.write(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${withQuestions ? 'Exam Paper' : 'Mark Scheme'}</title></head><body></body></html>`);
    doc.close();
    const base = element(doc, 'base'); base.href = document.baseURI; doc.head.append(base);
    const toolbar = element(doc, 'aside', 'print-toolbar');
    const status = element(doc, 'p', 'print-status', withQuestions ? 'Preparing the exam paper…' : 'Preparing the mark scheme…'); status.setAttribute('role', 'status');
    const printButton = element(doc, 'button', '', 'Print / Save PDF'); printButton.type = 'button'; printButton.disabled = true;
    const close = element(doc, 'button', 'secondary', 'Close preview'); close.type = 'button'; close.onclick = () => win.close();
    toolbar.append(element(doc, 'strong', '', withQuestions ? 'Luisa · Exam paper' : 'Luisa · Mark scheme'), status, printButton, close); doc.body.append(toolbar);
    const pages = element(doc, 'main', 'print-pages exam-paper marks-pending'); pages.setAttribute('aria-label', 'Exam paper'); doc.body.append(pages);
    let ready = false;
    win.addEventListener('beforeprint', () => doc.body.classList.toggle('not-ready', !ready));
    try {
      await whileOpen(win, Promise.all([asset(doc, 'link', 'papers-print.css'), asset(doc, 'link', 'papers-exam.css'), asset(doc, 'link', 'vendor/katex.min.css'), asset(doc, 'script', 'vendor/katex.min.js')]));
      const front = frontPage(doc, rows, options, totals);
      const staging = element(doc, 'div', 'print-staging exam-staging marks-pending'); doc.body.append(staging);
      const rendered = withQuestions ? rows.map(row => {
        const prompt = print.normaliseMarks(withoutSourceLabels(content(doc, (row.sourceKind === 'past-exam' ? '' : row.contextHtml || '') + row.question)));
        staging.append(prompt);
        return {row, prompt};
      }) : [];
      if (withQuestions) staging.append(front);
      // The paired official (or source) scheme with all its continuations (PAP-074-2).
      const schemes = withScheme ? rows.map(row => {
        const scheme = content(doc, row.steps.map(html => `<div class="solution-step">${html}</div>`).join(''));
        staging.append(scheme);
        return {row, scheme};
      }) : [];
      await whileOpen(win, prepare(win, staging, status), 120000);
      if (withQuestions) pages.append(front);
      const warnings = [];
      if (withQuestions && overflows(front)) warnings.push('The front page instructions do not fit on one page. Shorten them, then create a new preview.');
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
      // PAP-067-2: the mark scheme section, after the whole paper, in exam order.
      const schemePages = [];
      const examName = [[options.yearGroup, options.title].map(v => (v || '').trim()).filter(Boolean).join(' '), (options.monthYear || '').trim() || monthYear()].filter(Boolean).join(', ');
      function schemePage() {
        const sheet = element(doc, 'section', 'print-page exam-scheme-page');
        const body = element(doc, 'div', 'page-content');
        const footer = element(doc, 'footer', 'page-footer exam-footer');
        footer.append(element(doc, 'span', 'page-number'));
        if (!schemePages.length) body.append(element(doc, 'h1', 'exam-scheme-title', `Mark scheme: ${examName}`));
        sheet.append(body, footer); pages.append(sheet); schemePages.push(sheet);
        return body;
      }
      let schemeBody = null;
      for (let i = 0; i < schemes.length; i++) {
        const {row, scheme} = schemes[i], number = i + 1;
        if (win.closed) throw Error('Paper preview was closed.');
        status.textContent = `Laying out the mark scheme: ${number} of ${rows.length}…`;
        await new Promise(resolve => window.setTimeout(resolve, 0));
        if (!schemeBody) schemeBody = schemePage();
        let section;
        const newSection = continuation => {
          section = element(doc, 'article', 'print-solution exam-scheme'); section.dataset.questionId = row.id;
          const head = element(doc, 'header', 'question-heading compact-heading exam-heading');
          head.append(element(doc, 'h2', '', 'Question ' + number + (continuation ? ' (continued)' : '')));
          section.append(head);
          if (!continuation) section.append(element(doc, 'p', 'exam-scheme-source', schemeSource(row)));
          schemeBody.append(section);
        };
        newSection(false);
        const queue = [...scheme.children].map(node => node.cloneNode(true));
        let hasContent = false;
        while (queue.length) {
          const block = queue.shift(); section.append(block);
          if (wideContent(block)) {
            block.classList.add('compact');
            if (wideContent(block)) warnings.push(`Question ${number} (${row.sourceLabel || row.id}) has a mark scheme expression wider than the printable page.`);
          }
          if (!overflows(schemeBody)) { hasContent = true; continue; }
          block.remove();
          if (hasContent || schemeBody.children.length > 1) {
            if (!hasContent) section.remove();
            schemeBody = schemePage(); newSection(hasContent); hasContent = false; queue.unshift(block); continue;
          }
          const pieces = splitBlock(block);
          if (pieces && pieces.length > 1) { queue.unshift(...pieces); continue; }
          block.classList.add('compact'); section.append(block);
          if (overflows(schemeBody)) warnings.push(`Question ${number} (${row.sourceLabel || row.id}) has a mark scheme block too tall for one page; no content has been removed.`);
          hasContent = true;
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
      schemePages.forEach((sheet, index) => {
        sheet.querySelector('.page-number').textContent = `Mark scheme page ${index + 1} of ${schemePages.length}`;
        sheet.setAttribute('aria-label', `Mark scheme, page ${index + 1} of ${schemePages.length}`);
      });
      if (warnings.length) {
        doc.body.classList.add('not-ready');
        status.textContent = 'This exam paper cannot be printed completely. Remove or replace the listed questions, then create a new preview.';
        const list = element(doc, 'ul', 'print-errors'); [...new Set(warnings)].forEach(warning => list.append(element(doc, 'li', '', warning))); toolbar.append(list);
        return {window: win, pageCount: total, schemePageCount: schemePages.length, warnings: [...new Set(warnings)], ready: false};
      }
      ready = true;
      const parts = withQuestions ? `front page and ${total} A4 pages${withScheme ? `, then ${schemePages.length} mark scheme pages` : ''}` : `mark scheme only, ${schemePages.length} A4 pages`;
      status.textContent = `${rows.length} questions · ${totals.marks} marks · ${totals.minutes} minutes · ${parts}. Choose A4, 100% scale and turn off browser headers and footers in the print dialog.`;
      printButton.disabled = false; printButton.onclick = () => win.print();
      return {window: win, pageCount: total, schemePageCount: schemePages.length, warnings: [], ready: true};
    } catch (error) {
      if (!win.closed) { doc.body.classList.add('not-ready'); status.textContent = `${withQuestions ? 'Exam paper' : 'Mark scheme'} unavailable: ${error.message}`; }
      throw error;
    }
  }

  // ---- PAP-066-1 and PAP-066-5: timed selection and difficulty order (exam paper only) ----
  const LABELS = ['easy', 'medium', 'difficult'];
  const bandOf = row => LABELS.includes(row.difficulty) ? row.difficulty : 'unrated';
  const topicOf = row => row.paperId ? `${row.paperId}:${(row.chapterKeys || [])[0] || ''}` : (row.chapterKeys || [])[0] || row.chapterId || row.skillId || row.bookId || row.id;
  const markedRows = rows => rows.filter(row => Number.isInteger(row.marks) && row.marks > 0);
  // Mark totals whose paper time is within ±2 minutes of the target, nearest first.
  function targetMarks(minutes) {
    const out = [];
    for (let marks = 1; marks <= Math.ceil(minutes * 5 / 6) + 3; marks++) {
      const off = Math.abs(print.paperMinutes(marks) - minutes);
      if (off <= TOLERANCE) out.push({marks, off});
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
  function orderByBands(rows, {repair = true} = {}) {
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
    const greedy = [...opening, ...middle, ...closing];
    return repair && orderProblems(greedy).length ? repairOrder(greedy) : greedy;
  }
  // When the greedy order breaks the rule, search for a better one: every order for up to
  // 8 questions, otherwise improving pairwise swaps. Fewest problems wins; ties keep the
  // greedy order (and its variety).
  function repairOrder(rows) {
    let best = rows, bestProblems = orderProblems(rows).length;
    if (rows.length <= 8) {
      const permute = (done, left) => {
        if (!bestProblems) return;
        if (!left.length) { const n = orderProblems(done).length; if (n < bestProblems) { best = done; bestProblems = n; } return; }
        left.forEach((row, index) => permute([...done, row], left.filter((_, i) => i !== index)));
      };
      permute([], rows);
      return best;
    }
    for (let improved = true; improved && bestProblems;) {
      improved = false;
      for (let i = 0; i < best.length && !improved; i++) for (let j = i + 1; j < best.length && !improved; j++) {
        const trial = [...best]; [trial[i], trial[j]] = [trial[j], trial[i]];
        const n = orderProblems(trial).length;
        if (n < bestProblems) { best = trial; bestProblems = n; improved = true; }
      }
    }
    return best;
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
    return {rows, marks, minutes: time, timeMiss: Math.max(0, Math.abs(time - minutes) - TOLERANCE), offBy: Math.abs(time - minutes), bandProblems: orderProblems(rows).length, variety: new Set(rows.map(topicOf)).size};
  }
  const compare = (a, b) => a.timeMiss - b.timeMiss || a.bandProblems - b.bandProblems || b.variety - a.variety || a.offBy - b.offBy;
  const better = (a, b) => !b || compare(a, b) < 0;
  // Priorities when constraints conflict: (a) time within ±2 minutes, (b) difficulty bands, (c) variety.
  function planTimedPaper(pool, minutes, {attempts = 240, random = Math.random} = {}) {
    if (!Number.isInteger(minutes) || minutes < 2 || minutes > 600) throw Error('Choose a whole number of minutes from 2 to 600.');
    const rows = markedRows(pool), counts = {easy: 0, medium: 0, difficult: 0, unrated: 0}, marksBy = {easy: 0, medium: 0, difficult: 0, unrated: 0};
    for (const row of rows) { counts[bandOf(row)]++; marksBy[bandOf(row)] += row.marks; }
    const report = {target: minutes, extraTarget: extraMinutes(minutes), available: rows.length, availableMarks: rows.reduce((sum, row) => sum + row.marks, 0), counts, marksBy, excluded: pool.length - rows.length};
    if (!rows.length) return {...report, ok: false, rows: [], reasons: ['None of the questions in the chosen topics has known marks, so no exam paper can be timed from them. Add Practice Booklet or past-paper sources.']};
    const goals = targetMarks(minutes); let best = null;
    for (let attempt = 0; attempt < attempts; attempt++) {
      const order = shuffle(rows, random);
      for (const marks of goals.slice(0, 5)) {
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
        // Attempts use the fast greedy order; the order search runs once on the chosen paper.
        const candidate = score(orderByBands(paper, {repair: false}), minutes);
        if (better(candidate, best)) best = candidate;
        if (!best.timeMiss && !best.bandProblems && !best.offBy && best.variety === best.rows.length) break;
      }
      if (best && !best.timeMiss && !best.bandProblems && attempt > 24) break;
    }
    if (best.bandProblems) { const repaired = score(orderByBands(best.rows), minutes); if (compare(repaired, best) < 0) best = repaired; }
    const reasons = [];
    if (best.timeMiss) {
      reasons.push(report.availableMarks * 6 / 5 < minutes - TOLERANCE
        ? `The chosen topics have ${plural(rows.length, 'question')} with known marks, ${report.availableMarks} marks in all, which is only ${print.paperMinutes(report.availableMarks)} minutes.`
        : `No combination of whole questions in the chosen topics gives ${minutes} ± ${TOLERANCE} minutes; the nearest is ${best.minutes} minutes (${best.marks} marks).`);
    }
    if (best.bandProblems) {
      reasons.push(`The difficulty order cannot be met: the chosen topics have ${plural(counts.easy, 'easy question')} (${marksBy.easy} marks) and ${plural(counts.difficult, 'difficult question')} (${marksBy.difficult} marks), and the paper needs about ${Math.ceil(best.marks * 0.2)} marks of each.`);
      reasons.push(...orderProblems(best.rows));
    }
    return {...report, ok: !reasons.length, rows: best.rows, marks: best.marks, minutes: best.minutes, extra: extraMinutes(best.minutes), variety: best.variety, reasons};
  }

  window.LUISA_PAPERS_EXAM = Object.freeze({create, hasMarkScheme, schemeSource, courseGroup, extraMinutes, defaultInstructions, todayLabel, tolerance: TOLERANCE, targetMarks, bandPositions, orderProblems, orderByBands, planTimedPaper});

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
  // PAP-067-8: today's date unless the teacher typed or cleared the field in this session.
  let dateEdited = saved.dateEdited === true;
  $('papers-exam-date').value = dateEdited ? saved.date ?? '' : todayLabel();
  $('papers-exam-instructions').value = saved.instructions ?? defaultInstructions;
  $('papers-exam-minutes').value = saved.targetMinutes ?? '60';
  const contentInputs = [...document.querySelectorAll('input[name="papers-exam-content"]')];
  const chosenContent = () => contentInputs.find(input => input.checked)?.value || 'questions';
  if (CONTENTS.includes(saved.printContent)) contentInputs.forEach(input => { input.checked = input.value === saved.printContent; });
  function save() {
    const state = Object.fromEntries(Object.entries(fields).map(([key, id]) => [key, $(id).value]));
    state.printContent = chosenContent();
    state.dateEdited = dateEdited;
    try { sessionStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) { /* Optional convenience only. */ }
  }
  let proposal = null;
  const report = $('papers-exam-target-report'), accept = $('papers-exam-accept');
  function showReport(text, isError) { report.textContent = text; report.classList.toggle('error', Boolean(isError)); report.hidden = !text; }
  function targetPreview() {
    const minutes = Number($('papers-exam-minutes').value);
    $('papers-exam-target-help').textContent = Number.isInteger(minutes) && minutes > 0
      ? `Target ${minutes} minutes (+${extraMinutes(minutes)} minutes extra time): about ${Math.ceil(minutes * 5 / 6)} marks, within ±${TOLERANCE} minutes.` : 'Enter a whole number of minutes.';
  }
  function refresh() {
    const rows = builder.snapshot();
    const totals = paperTotals(rows), busy = builder.busy();
    const eligible = builder.pool().filter(hasMarkScheme).length;
    $('papers-exam-print').disabled = busy || !rows.length || Boolean(totals.unknown.length) || Boolean(totals.noScheme.length);
    $('papers-exam-generate').disabled = busy || !eligible;
    const total = builder.pool().length;
    $('papers-exam-eligible').textContent = `${eligible.toLocaleString()} of ${total.toLocaleString()} question${total === 1 ? '' : 's'} in the chosen sources and topics ${eligible === 1 ? 'has' : 'have'} an official mark scheme and can go in an exam paper.`;
    $('papers-exam-order').disabled = busy || rows.length < 2 || Boolean(totals.unknown.length);
    $('papers-exam-summary').textContent = !rows.length ? 'Select questions to build an exam paper.'
      : totals.noScheme.length ? `${plural(totals.noScheme.length, 'selected question')} without an official mark scheme cannot go in an exam paper. Remove ${totals.noScheme.length === 1 ? 'it' : 'them'} or generate a timed paper.`
      : totals.unknown.length ? `${plural(totals.unknown.length, 'selected question')} without known marks cannot go in an exam paper.`
      : `${plural(rows.length, 'question')} · ${totals.marks} marks · Time: ${totals.minutes} minutes (+${totals.extra} minutes extra time)`;
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
      // Shown in the same grid cell as the move buttons so the selection layout is unchanged.
      if (!hasMarkScheme(rows[index])) group.append(Object.assign(document.createElement('span'), {className: 'exam-no-scheme', textContent: 'No mark scheme'}));
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
  contentInputs.forEach(input => input.addEventListener('change', save));
  $('papers-exam-date').addEventListener('input', () => { dateEdited = true; save(); });
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
    const signature = () => builder.pool().map(row => row.id).join('|');
    try {
      const work = await builder.exclusive(async () => {
        const before = signature();
        // Only questions with an official mark scheme (PAP-074-2); questions without marks are excluded as before.
        const descriptors = builder.withoutDuplicateCopies(builder.pool()).filter(hasMarkScheme);
        const pool = await builder.load(descriptors, count => showReport(`Loading the questions in the chosen topics… ${count} of ${descriptors.length}`));
        if (signature() !== before) return {stale: true};
        return {plan: planTimedPaper(pool, minutes), failed: pool.failed};
      });
      if (!work) { showReport('Luisa is busy with another paper task. Wait for it to finish, then generate again.', true); return; }
      if (work.stale) { showReport('The sources or topics changed while the questions were loading. Generate the timed paper again.', true); return; }
      const {plan, failed} = work;
      const note = failed ? ` ${plural(failed, 'question')} could not be loaded and were left out.` : '';
      const summary = plan.rows.length ? `${plural(plan.rows.length, 'question')} · ${plan.marks} marks · ${plan.minutes} minutes (+${plan.extra} minutes extra time)` : '';
      if (plan.ok) {
        if (!builder.arrange(plan.rows, `Timed exam paper selected: ${summary}. Review it, reorder if needed, or choose Preview exam paper.`)) {
          showReport('Luisa is busy with another paper task, so the timed paper was not applied. Generate again when it finishes.', true); return;
        }
        showReport(`Target ${minutes} minutes met: ${summary}, ordered easy to difficult.${note}`);
      } else {
        proposal = plan.rows;
        const timeMet = plan.rows.length && Math.abs(plan.minutes - minutes) <= TOLERANCE;
        showReport(`${timeMet ? `Target ${minutes} minutes met, but not every exam rule.` : `Target ${minutes} minutes cannot be met exactly with these topics.`} ${plan.reasons.join(' ')}${summary ? ` Closest paper: ${summary}.` : ''} Add or change topics and generate again${summary ? ', or use the closest paper' : ''}.${note}`, true);
        accept.hidden = !plan.rows.length;
      }
    } catch (error) { showReport(error.message || 'The timed paper could not be generated.', true); }
    finally { refresh(); }
  });
  accept.addEventListener('click', () => {
    if (!proposal) return;
    if (builder.arrange(proposal, 'Closest timed paper selected. Review it or choose Preview exam paper.')) { proposal = null; accept.hidden = true; showReport(''); }
    else showReport('Luisa is busy with another paper task. Try again when it finishes.', true);
  });
  document.addEventListener('luisa-papers-state', refresh);
  $('papers-exam-print').addEventListener('click', () => builder.run(async () => {
    const rows = builder.snapshot();
    const choice = chosenContent();
    builder.status(choice === 'scheme' ? 'Preparing the mark scheme…' : 'Preparing the exam paper…');
    try {
      const options = {...Object.fromEntries(Object.entries(fields).map(([key, id]) => [key, $(id).value])), content: choice};
      const result = await create(rows, options);
      if (result.ready === false) builder.status(`The ${choice === 'scheme' ? 'mark scheme' : 'exam paper'} needs attention before printing. ${result.warnings.join(' ')}`, true);
      else builder.status(`${choice === 'scheme' ? 'Mark scheme' : choice === 'both' ? 'Exam paper and mark scheme' : 'Exam paper'} ready in a new window. Use its Print / Save PDF button.`);
    } catch (error) { builder.status(error.message || 'The exam paper could not be opened. Allow pop-ups for this site and try again.', true); }
  }));
  targetPreview();
  refresh();
})();
