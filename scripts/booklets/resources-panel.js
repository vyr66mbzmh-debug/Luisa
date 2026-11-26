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
    if (live.id === "fs1-1C-q8") {
      const question = content.querySelector(".exercise-question");
      const prompt = document.createElement("header");
      prompt.className = "split-prompt";
      prompt.innerHTML = "<strong>Question 8</strong>";
      const flow = [...question.querySelector(".lesson-image-prose").children];
      // Put the common stem at the top and the verbatim subparts above their
      // own working. This leaves nearly the whole physical panel for the tables.
      const grid = document.createElement("div");
      grid.className = "three-part";
      const working = content.querySelector(
        ".exercise-working .lesson-image-prose",
      );
      let between = [];
      for (const e of flow) {
        if (e.classList.contains("luisa-lettered-part")) {
          const col = document.createElement("section");
          grid.append(col);
          col.append(...between);
          between = [];
          const label = document.createElement("div");
          label.className = "part-prompt";
          label.innerHTML = e.innerHTML;
          col.append(label);
        } else {
          const para = document.createElement("div");
          para.innerHTML = e.innerHTML;
          if (grid.children.length) {
            para.className = "part-definition";
            between.push(para);
          } else {
            prompt.append(para);
          }
        }
      }
      if (between.length) grid.lastElementChild.append(...between);
      let part = -1;
      for (const e of [...working.children]) {
        if (e.classList.contains("luisa-lettered-part")) part++;
        if (part < 0) continue;
        e.querySelector(".luisa-part-label")?.remove();
        const col = grid.children[part];
        if (!student) {
          const para = document.createElement("div");
          para.className = "work-line";
          para.innerHTML = e.innerHTML;
          col.append(para);
        }
      }
      if (student) {
        const layouts = [
          [
            ["", "1", "2", "3", "4"],
            ["1", "", "", "", ""],
            ["2", "", "", "", ""],
            ["3", "", "", "", ""],
            ["4", "", "", "", ""],
          ],
          [
            ["x", "", "", "", ""],
            ["P(X = x)", "", "", "", ""],
          ],
          [
            ["x", "", "", "", ""],
            ["y", "", "", "", ""],
            ["P(Y = y)", "", "", "", ""],
          ],
          [
            ["x", "", "", "", ""],
            ["z", "", "", "", ""],
            ["P(Z = z)", "", "", "", ""],
          ],
        ];
        layouts.forEach((rows, i) => {
          const el = document.createElement("table");
          el.className = "exercise-grid";
          for (const row of rows) {
            const tr = el.insertRow();
            for (const cell of row) tr.insertCell().textContent = cell;
          }
          if (i === 3) el.style.marginTop = "62px";
          grid.children[i < 2 ? 0 : 1].append(el);
        });
      }
      content.replaceChildren(prompt, grid);
      content.style.height = printHeight + "px";
      return {
        html: content.outerHTML,
        w,
        h: printHeight,
        css: [...document.querySelectorAll("link[rel=stylesheet]")].map(
          (e) => e.href,
        ),
        title: live.title,
        id: live.id,
      };
    }
    if (student && live.id === "fs1-6E-q12") {
      const earlier = panel.querySelector(".exercise-under-question"),
        left = bounds(earlier);
      const area = content.querySelector(".exercise-under-question");
      area.replaceChildren();
      area.classList.remove("answer-blue");
      const section = (parent, caption) => {
        const sec = document.createElement("section");
        parent.append(sec);
        sec.style.cssText =
          "padding:7px 9px;border:1.35px solid #8997a2;box-sizing:border-box;font:21px Lesson,serif;color:#183957";
        const label = document.createElement("span");
        label.textContent = caption;
        sec.append(label);
        return sec;
      };
      const table = (parent, rows, cols, firstColumn) => {
        const el = document.createElement("table");
        parent.append(el);
        el.style.cssText =
          "border-collapse:collapse;table-layout:fixed;width:100%;font:19px Lesson,serif;color:#183957;margin:5px 0";
        for (let i = 0; i <= rows.length; i++) {
          const row = el.insertRow();
          for (let j = 0; j < cols.length; j++) {
            const cell = row.insertCell();
            cell.textContent = i === 0 ? cols[j] : j === 0 ? rows[i - 1] : "";
            cell.style.cssText =
              "border:1.3px solid #8796a2;text-align:center;height:37px;padding:0 3px;line-height:1.08";
            if (j === 0) cell.style.width = firstColumn;
          }
        }
      };
      area.style.cssText =
        "position:absolute;left:" +
        left.x +
        "px;top:" +
        left.y +
        "px;width:" +
        left.w +
        "px;height:" +
        (printHeight - left.y - 12) +
        "px;display:grid;grid-template-rows:1fr 1.75fr;gap:6px;";
      section(area, "(a)");
      const expected = section(area, "(b)   Expected frequencies");
      table(
        expected,
        ["Biology", "Chemistry", "Physics"],
        ["Science", "£0–20k", "£20–40k", "£40–60k", "£60–80k", "> £80k"],
        "21%",
      );
      const work = content.querySelector(".exercise-working"),
        r = bounds(panel.querySelector(".exercise-working"));
      work.remove();
      const right = document.createElement("div");
      content.append(right);
      right.style.cssText =
        "position:absolute;left:" +
        r.x +
        "px;top:" +
        r.y +
        "px;width:" +
        r.w +
        "px;height:" +
        (printHeight - r.y - 12) +
        "px;display:grid;grid-template-rows:3fr 1fr;gap:6px";
      const pool = section(right, "Pooled counts and contributions");
      table(
        pool,
        ["Biology", "", "", "Chemistry", "", "", "Physics", "", ""],
        ["Science", "Band (£k)", "Observed", "Expected", "Contribution"],
        "22%",
      );
      section(right, "Test statistic and conclusion");
      content.querySelector(".exercise-reveal")?.remove();
      content.style.height = printHeight + "px";
      return {
        html: content.outerHTML,
        w,
        h: printHeight,
        css: [...document.querySelectorAll("link[rel=stylesheet]")].map(
          (e) => e.href,
        ),
        title: live.title,
        id: live.id,
      };
    }
    if (student && live.singlePageExercise.studentGraph) {
      const spec = live.singlePageExercise.studentGraph;
      const work = panel.querySelector(".exercise-working"),
        r = bounds(work);
      const source = work.querySelector(".exercise-figure");
      const image = document.createElement("img");
      image.src = new URL("../" + spec.asset, source.src).href;
      image.alt = spec.alt;
      Object.assign(image.style, {
        height: "100%",
        width: "100%",
        objectFit: "contain",
      });
      const wrapper = document.createElement("section");
      Object.assign(wrapper.style, {
        position: "absolute",
        top: r.y + "px",
        left: r.x + "px",
        width: r.w + "px",
        height: printHeight - r.y - 12 + "px",
        display: "grid",
        gridTemplateRows: "1fr 1.4fr 1.15fr 3.3fr 1.3fr",
        border: "1.5px solid #8796a2",
        boxSizing: "border-box",
      });
      for (const label of work.querySelectorAll(".luisa-part-label")) {
        const sec = document.createElement("div"),
          cue = document.createElement("span");
        Object.assign(sec.style, {
          display: "flex",
          padding: "5px 9px",
          gap: "8px",
          alignItems: "flex-start",
          minHeight: "0",
        });
        cue.textContent = label.textContent;
        cue.style.font = "22px Lesson,serif";
        sec.append(cue);
        if (label.textContent.replace(/[^a-z]/g, "") === spec.part)
          sec.append(image);
        wrapper.append(sec);
      }
      content.querySelector(".exercise-reveal")?.remove();
      content.querySelector(".exercise-working").replaceChildren();
      content.append(wrapper);
      content.style.height = printHeight + "px";
      return {
        html: content.outerHTML,
        w,
        h: printHeight,
        css: [...document.querySelectorAll("link[rel=stylesheet]")].map(
          (e) => e.href,
        ),
        title: live.title,
        id: live.id,
      };
    }
    if (student && live.id.startsWith("fs1-6")) {
      const work = panel.querySelector(".exercise-working"),
        r = bounds(work);
      const groups = [];
      function newGroup(label = "") {
        const g = { label, rows: [], weight: 0 };
        groups.push(g);
        return g;
      }
      let group;
      const numberOfColumns =
        parseInt(getComputedStyle(work).columnCount, 10) || 1;
      const lineWidth = r.w / numberOfColumns;
      for (const line of work.querySelector(".lesson-image-prose").children) {
        const marker = line.querySelector(".luisa-part-label");
        if (marker || !group) group = newGroup(marker?.textContent || "");
        const tex = [...line.querySelectorAll("[data-math]")].map(
          (e) => e.dataset.math,
        );
        const array = tex.find((t) => t.includes("\\begin{array}"));
        if (array) {
          group.rows.push(arrayRows(array));
        } else {
          const text = line.textContent;
          group.weight += Math.max(
            1,
            Math.ceil(text.length / (lineWidth / 15)),
          );
        }
      }
      content.querySelector(".exercise-working").replaceChildren();
      content.querySelector(".exercise-reveal")?.remove();
      const page = document.createElement("div");
      page.className = "pencil-slots";
      Object.assign(page.style, {
        position: "absolute",
        display: "flex",
        flexDirection: "column",
        left: r.x + "px",
        top: r.y + "px",
        width: r.w + "px",
        height: printHeight - r.y - 12 + "px",
        border: "1.55px solid #8997a2",
        padding: "8px",
        boxSizing: "border-box",
      });
      for (const g of groups) {
        const sec = document.createElement("section");
        page.append(sec);
        Object.assign(sec.style, {
          display: "flex",
          flexDirection: "column",
          flex: g.weight + " 1 auto",
          position: "relative",
          minHeight: "0",
          padding: "2px 6px",
          gap: "5px",
        });
        if (g.label) {
          const cap = document.createElement("span");
          cap.style.font = "22px Lesson,serif";
          cap.textContent = g.label;
          sec.append(cap);
        }
        for (const rows of g.rows) {
          const table = document.createElement("table");
          sec.append(table);
          Object.assign(table.style, {
            borderCollapse: "collapse",
            width: "100%",
            tableLayout: "fixed",
            font: "17px Lesson,serif",
            flex: "0 1 auto",
          });
          const tall = rows.length > 3;
          const rowHeight = Math.min(
            39,
            Math.max(
              24,
              (printHeight - r.y - 58 * groups.length - 80) /
                (groups.reduce(
                  (a, g) => a + g.rows.reduce((n, rows) => n + rows.length, 0),
                  0,
                ) || 1),
            ),
          );
          for (let i = 0; i < rows.length; i++) {
            const tr = table.insertRow();
            rows[i].forEach((value, j) => {
              const td = tr.insertCell();
              td.style.cssText =
                "border:1.2px solid #8796a2;text-align:center;padding:0 2px;height:" +
                rowHeight +
                "px";
              if (!j) td.style.width = tall ? "26%" : "20%";
              const containsText = /\\text\{/.test(value);
              // Leave student-computed numbers, estimates and pooling choices blank.
              if (
                (i === 0 || j === 0) &&
                (containsText || /^[OE]_i$/.test(value))
              ) {
                katex.render(value, td, { throwOnError: true });
              }
            });
          }
        }
      }
      content.append(page);
      content.style.height = printHeight + "px";
      return {
        html: content.outerHTML,
        w,
        h: printHeight,
        css: [...document.querySelectorAll("link[rel=stylesheet]")].map(
          (e) => e.href,
        ),
        title: live.title,
        id: live.id,
      };
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
    for (const rectangles of areas.values()) {
      for (const r of rectangles) {
        const bottom = r.y + r.h;
        let limit = printHeight - 5;
        for (const other of occupied) {
          if (other.x >= r.x + r.w || other.x + other.w <= r.x) continue;
          if (other.y + other.h <= bottom + 1) continue;
          limit = Math.min(limit, Math.max(bottom, other.y - 8));
        }
        box(
          Math.max(2, r.x - 3),
          Math.max(1, r.y - 3),
          Math.min(w - r.x - 4, r.w + 6),
          Math.min(printHeight - r.y - 3, Math.max(r.h + 6, limit - r.y)),
        );
      }
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
