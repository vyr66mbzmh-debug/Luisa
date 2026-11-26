(opts) => {
  const panel = document.querySelector("#slide-content .source-slide");
  const live = FMQ_TEST.getState().slide;
  if (!panel) throw Error("Missing board layout: " + live.id);
  if (live.singlePageExercise?.sourcePlates)
    throw Error("Needs native transcription: " + live.id);
  if (live.solutionPanels)
    throw Error("Needs all staged solution panels: " + live.id);
  const content = panel.cloneNode(true),
    student = opts.edition === "student";
  // The classroom sets its readable typography on an ancestor outside the
  // cloned board. Retain it so wrapped answer lines have the same width in print.
  if (panel.closest(".readable-mode")) content.classList.add("readable-mode");
  // An embedded player has no playback in print. Keep its actual video link.
  for (const frame of content.querySelectorAll("iframe")) {
    const shape = frame.closest("[data-shape]");
    const item = live.shapes.find(
      (s) => s.id === shape?.dataset.shape && s.youtubeId,
    );
    if (!item) continue;
    const link = document.createElement("a");
    link.href =
      "https://www.youtube.com/watch?v=" + encodeURIComponent(item.youtubeId);
    link.textContent = item.alt || "Watch the video";
    link.style.cssText =
      "display:inline-block;font:33px Lesson,serif;color:#185688;text-decoration:underline";
    const note = document.createElement("p");
    note.style.cssText = "font:22px Lesson,serif;color:#183957";
    note.textContent = link.href;
    shape.replaceChildren(link, note);
  }
  const base = panel.getBoundingClientRect(),
    w = panel.offsetWidth,
    h = panel.offsetHeight;
  const scale = base.width / w,
    printHeight = Math.max(h, w * 0.663);
  function box(x, y, width, height, label = "") {
    const e = document.createElement("div");
    e.className = "write-area";
    Object.assign(e.style, {
      left: x + "px",
      top: y + "px",
      width: width + "px",
      height: height + "px",
    });
    e.textContent = label;
    content.append(e);
  }
  function bounds(e) {
    const r = e.getBoundingClientRect();
    return {
      x: (r.x - base.x) / scale,
      y: (r.y - base.y) / scale,
      w: r.width / scale,
      h: r.height / scale,
    };
  }
  function arrayRows(tex) {
    const match = tex.match(
      /\\begin\{array\}\{[^}]*\}([\s\S]*?)\\end\{array\}/,
    );
    if (!match) return [];
    const body = match[1].replace(/\\hline/g, "");
    const rows = [],
      row = [];
    let cell = "",
      depth = 0;
    for (let i = 0; i < body.length; i++) {
      const ch = body[i];
      if (ch === "\\" && body[i + 1] === "\\" && depth === 0) {
        row.push(cell.trim());
        rows.push(row.splice(0));
        cell = "";
        i++;
        continue;
      }
      if (ch === "&" && depth === 0) {
        row.push(cell.trim());
        cell = "";
        continue;
      }
      if (ch === "{") depth++;
      if (ch === "}") depth--;
      cell += ch;
    }
    if (cell.trim() || row.length) {
      row.push(cell.trim());
      rows.push(row);
    }
    return rows;
  }
  // Preserve true/false reasoning in print; each alternative opens the same
  // explanation, so either answer button maps to the same written response.
  const alternatives = live.alternativeTriggers || [];
  for (const ids of alternatives) {
    const visibleTargets = new Set();
    for (const id of ids) {
      for (const step of live.animation.triggers[id] || []) {
        for (const action of step) {
          if (action.type === "set" && action.to?.[0]?.val === "visible") {
            for (const target of action.targets)
              visibleTargets.add(target.spid);
          }
        }
      }
    }
    for (const id of visibleTargets) {
      const ref = panel.querySelector('[data-shape="' + CSS.escape(id) + '"]');
      const print = content.querySelector(
        '[data-shape="' + CSS.escape(id) + '"]',
      );
      if (!ref || !print) continue;
      const r = bounds(ref);
      box(r.x - 4, r.y - 4, r.w + 8, r.h + 8);
      if (student) print.remove();
      else print.classList.add("answer-blue");
    }
    for (const id of ids)
      content.querySelector('[data-shape="' + CSS.escape(id) + '"]')?.remove();
  }
  const owned = [...panel.querySelectorAll("[data-answer-for]")].filter(
    (e) =>
      !e.closest("[data-supplied-theory]") && e.offsetWidth && e.offsetHeight,
  );
  if (live.singlePageExercise) {
    const sketch = content.querySelector(".exercise-sketch");
    if (sketch) {
      // The classroom layers these two states in exactly the same position.
      // Keep just the appropriate diagram in each permanent print edition.
      sketch.querySelector(student ? ".exercise-sketch-answer" : ":scope > img").remove();
    }

    const work = panel.querySelector(".exercise-working"),
      r = bounds(work);
    const band = panel.querySelector(".exercise-diagram-band");
    if (student && band) {
      const rect = bounds(band);
      content.querySelector(".exercise-diagram-band").replaceChildren();
      box(rect.x, rect.y, rect.w, rect.h);
    }
    // Exact part starts match the worked edition, including the first item of a second column.
    const anchors = [...work.querySelectorAll(".luisa-part-label")].map((e) => [
      e.textContent,
      bounds(e),
    ]);
    // Allocate spare vertical space across all parts. Otherwise short typeset
    // answers put (b) directly below (a), leaving the pupil no room for (a).
    // Keep the starts aligned in both editions. Tables retain their drawn grids
    // and multiple columns retain their own reading order.
    const blocks = [...work.querySelectorAll(".lesson-image-prose > *")];
    const plainSingleColumn = anchors.length > 1 && blocks.length &&
      (parseInt(getComputedStyle(work).columnCount, 10) || 1) === 1 &&
      !work.querySelector("img,svg:not(.katex svg),table,[data-math*='{array}']");
    if (plainSingleColumn) {
      const inkBottom = Math.max(...blocks.map(el => {
        const area = bounds(el);
        return area.y + area.h;
      }));
      const bottom = band ? bounds(band).y : printHeight;
      const extra = Math.floor((bottom - inkBottom - 24) / anchors.length);
      if (extra > 0) {
        const labels = content.querySelectorAll(".exercise-working .luisa-part-label");
        for (let i = 1; i < anchors.length; i++) {
          anchors[i][1].y += i * extra;
          const line = labels[i].closest(".luisa-lettered-part");
          const original = work.querySelectorAll(".luisa-part-label")[i]
            .closest(".luisa-lettered-part");
          const oldMargin = parseFloat(getComputedStyle(original).marginTop) || 0;
          line.style.marginTop = (oldMargin + extra) + "px";
        }
        const printWork = content.querySelector(".exercise-working");
        printWork.style.height = (bottom - r.y - 8) + "px";
      }
    }
    const title = content.querySelector(".exercise-head");
    title.querySelector(".exercise-reveal")?.remove();
    if (student) {
      // The header keeps the given diagram. Reserve the worked diagrams' space for sketches.
      const workedFigures = [...panel.querySelectorAll(".exercise-header-answer")];
      if (workedFigures.length) {
        const first = bounds(workedFigures[0]);
        const last = bounds(workedFigures.at(-1));
        title.querySelectorAll(".exercise-header-answer").forEach(e => {
          e.replaceChildren();
          e.removeAttribute("data-answer-for");
          e.removeAttribute("aria-hidden");
          e.classList.remove("answer-concealed", "answer-blue", "is-hidden");
        });
        box(first.x, first.y, last.x + last.w - first.x, first.h);
      }
    }
    box(
      r.x - 5,
      r.y - 7,
      r.w + 9,
      (band ? bounds(band).y : printHeight) - r.y - 5,
    );
    if (student) {
      // Preserve a writable table or sample-space grid at its very place in
      // the solution. Only given row/column headings may be prefilled.
      for (const field of work.querySelectorAll("[data-math]")) {
        const rows = arrayRows(field.dataset.math);
        if (!rows.length) continue;
        // The key describes the variable. All values in a student-built
        // distribution stay empty, including transformed outcomes.
        const g = bounds(field.querySelector(".katex-html") || field),
          grid = document.createElement("table");
        grid.className = "pencil-table";
        const style = getComputedStyle(work),
          count = parseInt(style.columnCount, 10) || 1;
        const gap = parseFloat(style.columnGap) || 0,
          col = (r.w - (count - 1) * gap) / count;
        const ix = Math.max(0, Math.floor((g.x - r.x) / (col + gap)));
        const edge = r.x + (ix + 1) * col + ix * gap - 12;
        const width = Math.min(
          edge - g.x,
          Math.max(g.w, rows[0].length * 67 + 80),
        );
        const future = [
          ...work.querySelectorAll(".luisa-part-label,.katex-html"),
        ]
          .map(bounds)
          .filter(
            (b) =>
              b.y > g.y + g.h + 1 &&
              b.x >= r.x + ix * (col + gap) - 2 &&
              b.x < edge,
          );
        const bottom = Math.min(
          printHeight - 10,
          ...future.map((b) => b.y - 5),
        );
        const height = Math.min(
          Math.max(g.h, rows.length * 41),
          Math.max(g.h, bottom - g.y),
        );
        Object.assign(grid.style, {
          left: g.x + "px",
          top: g.y + "px",
          width: width + "px",
          height: height + "px",
        });
        const sample = rows[0][0].trim() === "";
        for (let i = 0; i < rows.length; i++) {
          const tr = grid.insertRow();
          for (let j = 0; j < rows[i].length; j++) {
            const cell = tr.insertCell();
            if (j === 0 || (sample && !i)) {
              const t = rows[i][j].trim();
              if (t) katex.render(t, cell, { throwOnError: true });
            }
          }
        }
        content.append(grid);
      }
      content.querySelector(".exercise-working").replaceChildren();
      for (const [text, anchor] of anchors) {
        const e = document.createElement("div");
        e.className = "part-cue";
        e.textContent = text;
        Object.assign(e.style, { left: anchor.x + "px", top: anchor.y + "px" });
        content.append(e);
      }
    }
  } else if (live.exerciseWritingAreas) {
    // Some exercises have their own labelled axes and multi-cell data tables.
    // Keep the full source layout and reserve one writing area per subpart.
    for (const area of live.exerciseWritingAreas) {
      const cells = area.shapes.map(id => {
        const el = panel.querySelector('[data-shape="' + CSS.escape(id) + '"]');
        if (!el) throw Error("Missing exercise writing area: " + id);
        return bounds(el);
      });
      const x = Math.min(...cells.map(b => b.x));
      const y = Math.min(...cells.map(b => b.y));
      const right = Math.max(...cells.map(b => b.x + b.w));
      const bottom = Math.max(...cells.map(b => b.y + b.h));
      box(x, y, right - x, bottom - y, student ? area.label : "");
    }
    if (student) {
      content.querySelectorAll("[data-answer-for]").forEach(answer => answer.remove());
    }
  } else {
    const areas = new Map();
    for (const e of owned) {
      // Several expressions or graphics may live within the same answer slot.
      const r = bounds(e);
      if (r.w < 4 || r.h < 4) continue;
      const key = e.getAttribute("data-answer-for"),
        all = areas.get(key) || [];
      all.push(r);
      areas.set(key, all);
    }
    // The printed answer starts where its classroom working starts. Give a
    // pupil the clear space below it, stopping before any other teaching ink.
    const occupied = [...panel.querySelectorAll("[data-shape]")].filter(
      e => e.offsetWidth && e.offsetHeight && !e.matches(".lesson-answer-cover,.is-hidden,.answer-concealed") &&
        !e.querySelector("[data-shape]") && !e.closest(".lesson-answer-cover")
    ).map(bounds);
    // Several shapes revealed by one control share one writing space.
    const slots = [...areas.values()].map(rectangles => {
      const x = Math.min(...rectangles.map(r => r.x));
      const y = Math.min(...rectangles.map(r => r.y));
      const right = Math.max(...rectangles.map(r => r.x + r.w));
      const bottom = Math.max(...rectangles.map(r => r.y + r.h));
      return {x, y, w: right - x, h: bottom - y};
    });
    for (const r of slots) {
      const bottom = r.y + r.h;
      let limit = printHeight - 5;
      for (const other of [...occupied, ...slots]) {
        if (other.x >= r.x + r.w || other.x + other.w <= r.x) continue;
        if (other.y < bottom - 1) continue;
        limit = Math.min(limit, Math.max(bottom, other.y - 8));
      }
      box(Math.max(2, r.x - 3), Math.max(1, r.y - 3),
          Math.min(w - r.x - 4, r.w + 6), Math.min(printHeight - r.y - 3, limit - r.y));
    }
    if (student)
      for (const e of content.querySelectorAll(
        "[data-answer-for]:not([data-supplied-theory])",
      ))
        e.remove();
  }
  content
    .querySelectorAll(
      ".lesson-answer-cover,.exercise-reveal,.is-hidden,.answer-concealed,.lesson-animation-control",
    )
    .forEach((e) => e.remove());
  content.style.height = printHeight + "px";
  return {
    html: content.outerHTML,
    w,
    h: printHeight,
    css: [...document.querySelectorAll("link[rel=stylesheet]")].map(
      (e) => e.href,
    ),
    title: document.querySelector("#lesson-title").innerText,
    id: live.id,
  };
};
