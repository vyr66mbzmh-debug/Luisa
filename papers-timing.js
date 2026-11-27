/* Shared timed-paper scheduling (PAP-091). Student-safe: it applies no mark-scheme rule of its own.
   Each entry point passes its eligibility predicate. The student generator accepts any question with a
   known whole-question mark total. The teacher exam (papers-exam.js) also requires an eligible scheme. */
(() => {
  'use strict';
  const print = window.LUISA_PAPERS_PRINT;
  if (!print?.paperMinutes) return;
  // PAP-067-1: paper time within ±2 minutes of the target.
  const TOLERANCE = 2;
  const minutesFor = marks => print.paperMinutes(marks);
  const bandOf = row => row.difficulty || 'unclassified';
  const closingBand = row => ['difficult', 'very-difficult'].includes(bandOf(row));
  const topicOf = row => row.paperId ? `${row.paperId}:${(row.chapterKeys || [])[0] || ''}` : (row.chapterKeys || [])[0] || row.chapterId || row.skillId || row.bookId || row.id;
  const knownMarks = row => Number.isInteger(row.marks) && row.marks > 0;
  const markedRows = rows => rows.filter(knownMarks);
  const validMinutes = minutes => Number.isInteger(minutes) && minutes >= 2 && minutes <= 600;
  // Mark totals whose paper time is within ±2 minutes of the target, nearest first (exact time first).
  function targetMarks(minutes) {
    const out = [];
    for (let marks = 1; marks <= Math.ceil(minutes * 5 / 6) + 3; marks++) {
      const off = Math.abs(minutesFor(marks) - minutes);
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
  // Every opening-band question is easy, every closing-band question is difficult,
  // and (for two or more questions) Question 1 is easy and the last question is difficult.
  function orderProblems(rows) {
    if (rows.length < 2 || markedRows(rows).length !== rows.length) return [];
    const problems = [], bands = bandPositions(rows);
    rows.forEach((row, index) => {
      const opening = bands[index] === 'opening' || index === 0, closing = bands[index] === 'closing' || index === rows.length - 1;
      if (opening && bandOf(row) !== 'easy') problems.push(`Question ${index + 1} is in the first 20% of marks but is ${bandOf(row)}, not easy.`);
      else if (closing && !closingBand(row)) problems.push(`Question ${index + 1} is in the last 20% of marks but is ${bandOf(row)}, not difficult.`);
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
    const hard = rows.filter(row => closingBand(row)).sort((a, b) => b.marks - a.marks);
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
  // 8 questions, otherwise improving pairwise swaps. Fewest problems wins; ties keep the greedy order.
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
  // New topics first, then the rest, so every subset prefers variety.
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
    const marks = rows.reduce((sum, row) => sum + row.marks, 0), time = minutesFor(marks) ?? 0;
    return {rows, marks, minutes: time, timeMiss: Math.max(0, Math.abs(time - minutes) - TOLERANCE), offBy: Math.abs(time - minutes), bandProblems: orderProblems(rows).length, variety: new Set(rows.map(topicOf)).size};
  }
  // Priorities when constraints conflict: (a) time within ±2 minutes, (b) difficulty order, (c) variety, (d) exact time.
  const compare = (a, b) => a.timeMiss - b.timeMiss || a.bandProblems - b.bandProblems || b.variety - a.variety || a.offBy - b.offBy;
  const better = (a, b) => !b || compare(a, b) < 0;
  // Whole questions only. `eligible` is the entry point's own rule; rows failing it, or without a
  // known positive mark total, are never used. The result reports time and order separately.
  function plan(pool, minutes, {eligible = () => true, attempts = 240, random = Math.random} = {}) {
    if (!validMinutes(minutes)) throw Error('Choose a whole number of minutes from 2 to 600.');
    const rows = markedRows(pool.filter(eligible)), counts = {easy: 0, medium: 0, difficult: 0, 'very-difficult': 0, unclassified: 0}, marksBy = {...counts};
    for (const row of rows) { counts[bandOf(row)]++; marksBy[bandOf(row)] += row.marks; }
    const report = {target: minutes, available: rows.length, availableMarks: rows.reduce((sum, row) => sum + row.marks, 0), counts, marksBy, excluded: pool.length - rows.length};
    if (!rows.length) return {...report, rows: [], marks: 0, minutes: null, timeMet: false, bandProblems: 0, problems: [], variety: 0};
    const goals = targetMarks(minutes); let best = null;
    for (let attempt = 0; attempt < attempts; attempt++) {
      const order = shuffle(rows, random);
      for (const marks of goals.slice(0, 5)) {
        const opening = bandFill(freshFirst(order.filter(row => bandOf(row) === 'easy'), []), marks);
        const closing = bandFill(freshFirst(order.filter(row => closingBand(row) && !opening.includes(row)), opening.map(topicOf)), marks);
        const chosen = new Set([...opening, ...closing]), used = [...chosen].map(topicOf);
        const rest = marks - [...chosen].reduce((sum, row) => sum + row.marks, 0);
        const others = order.filter(row => !chosen.has(row));
        const middlePool = freshFirst(others, used).slice(0, 160);
        let middle = rest > 0 ? subsetWithSum(middlePool, rest) : rest === 0 ? [] : null;
        if (!middle) { // Closest whole-question total: greedy fill below the goal.
          middle = []; let sum = 0;
          for (const row of middlePool) if (sum + row.marks <= Math.max(rest, 0)) { middle.push(row); sum += row.marks; }
        }
        let paper = [...opening, ...middle, ...closing];
        let total = paper.reduce((sum, row) => sum + row.marks, 0);
        if (total < marks) { for (const row of order) if (!paper.includes(row) && total + row.marks <= goals.at(-1)) { paper.push(row); total += row.marks; } }
        // A greedy fill can overshoot when the band fills are large; an exact subset of the whole pool wins then.
        if (!paper.length || Math.abs(minutesFor(total) - minutes) > TOLERANCE) {
          const exact = subsetWithSum(freshFirst(order, []).slice(0, 200), marks);
          if (exact) paper = exact;
        }
        // Attempts use the fast greedy order; the order search runs once on the chosen paper.
        const candidate = score(orderByBands(paper, {repair: false}), minutes);
        if (better(candidate, best)) best = candidate;
        if (!best.timeMiss && !best.bandProblems && !best.offBy && best.variety === best.rows.length) break;
      }
      if (best && !best.timeMiss && !best.bandProblems && attempt > 24) break;
    }
    if (best.bandProblems) { const repaired = score(orderByBands(best.rows), minutes); if (compare(repaired, best) < 0) best = repaired; }
    return {...report, rows: best.rows, marks: best.marks, minutes: best.minutes, timeMet: !best.timeMiss,
      bandProblems: best.bandProblems, problems: orderProblems(best.rows), variety: best.variety};
  }
  window.LUISA_PAPERS_TIMING = Object.freeze({tolerance: TOLERANCE, presets: Object.freeze([30, 45, 60, 90, 120]),
    knownMarks, validMinutes, targetMarks, bandPositions, orderProblems, orderByBands, plan});
})();
