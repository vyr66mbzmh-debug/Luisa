# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.89 -->
**Release 0.89 · GitHub #168.**

Select Old Spec beside Past Papers to include 244 revision questions across 17 Core Pure chapters. The paper dropdown groups the 22 packs under old spec revision questions.

Each exercise has a worked solution and a separate mark scheme. The collection retains 15 edited labels and includes 33 easy, 124 medium and 87 difficult questions. The teacher exam builder uses the marking tables or the suggested marking guide for the 17 exercises with authored allocations.

The 264 pack positions resolve to 244 exercises. The 30 existing catalogue matches keep their original sources and appear once in a combined selection. See issue #168 for production verification.
<!-- END LUISA-RELEASE-BLOCK -->

## Tooling, access and where everything lives

Everything needed to import papers, build, test, land, deploy, verify, archive and report a release is in this repository (OPS-064). Only private values stay outside Git (OPS-065).

**Start from scratch (any agent, any engine, or a human).**
1. Clone the repository. Read AGENTS.md (quick start), this file and `docs/agentic/RELEASE-RUNBOOK.md`.
2. Ask the owner for the private state folder (default `~/.local/share/luisa-agent-state`, or set `LUISA_STATE_DIR`) containing `WORKSPACE.json`. You also need GitHub CLI access to the repository and SSH access to the ADA host.
3. Run `python3 scripts/bootstrap.py`. It creates the pinned environment at `<state>/env`.
4. Run `<state>/env/bin/python scripts/luisa.py doctor`. Every line must say PASS. Each MISSING line names the human action needed.
5. Follow the runbook for the job.

**Where each tool lives.**

| Area | Location | What it does |
|---|---|---|
| Gate, build, artifact checks, privacy scan, cold-start check | `scripts/luisa.py` | Commands: `gate`, `check`, `test`, `scan`, `privacy`, `build`, `check-artifact`, `doctor`, `requirements` |
| Environment | `scripts/bootstrap.py`, `requirements-tools.txt` | Builds the pinned Python environment: Playwright, PyMuPDF, SymPy and Node (nodejs-wheel), plus a browser |
| Release tooling | `scripts/release/` | Its README describes each script: `land_build.py`, `ada.py`, `verify_owner.py`, `qa_live.py`, `qa_offline.py`, `docs.py`, `report.py`, `finish.py`, `tokens.py`, `doctor.py` and `private.py` |
| Past-paper import | `scripts/import/` | Per-paper pipeline (README), with the v0.72 Sample set as the reference input set in `scripts/import/sets/` |
| Landing a reviewed PR | `scripts/land.py` | Run through `scripts/release/land_build.py` |
| Recovery archive | `scripts/archive_release.py` | Run through `scripts/release/finish.py archive` |
| Usage records | `scripts/usage.py` | `start`/`end` per job |
| Release specs | `docs/releases/v<version>.json`, `docs/releases/v<version>-handoff.md` | Release notes, report intro and this file's release block |
| Review role | `docs/agentic/REVIEWER-RULES.md`, `docs/agentic/review-record.schema.json` | Reviewer role and output schema |

**Private configuration keys** (`WORKSPACE.json`; names only, values never in Git, logs or reports): `master`, `mailSender`, `pastPaperSource` (the folder where the owner puts new past papers; since v0.73 `<state>/past-paper-source/`), `ada.sshHost`, `ada.sshPort`, `ada.url`, `ada.pupilEmailDomain`, and `ada.layout.releaseRoot`, `releasePrefix`, `startScript`, `dataDir`, `runtimePython`, `supervisorCommand`, `serviceName`, `nginx`. `scripts/release/private.py` is the only reader.

**What stays private, and why.** The following stay in the private state folder or the owner's machine:
- credentials and SMTP settings, inside the mail adapter;
- the ADA SSH host and the server's internal paths;
- mail sender and recipient;
- account databases and their snapshots;
- owner source PDFs;
- unpublished corrections;
- session transcripts;
- release work folders (`<state>/releases/v<version>/`, holding QA results and printed PDFs);
- owner reports (`<state>/reports/`).

The repository is public, so anything committed is visible to everyone. `python3 scripts/luisa.py privacy` (part of the gate) blocks credentials, personal paths, private hosts and owner source PDFs.

**The ADA website address** is public. The owner site's offline page links pupils to it, and the auth app names it. The SSH host and server layout are private.

## Standing rules and authority
- **Rules:** AGENTS.md (mandatory standard), `docs/agentic/LEAD-RULES.md`, `docs/agentic/REVIEWER-RULES.md`, and the requirement register `docs/requirements/register.json` (generated `REQUIREMENTS.md`). New owner instructions take precedence; record them on GitHub and in the register while implementing (OPS-063).
- **Release targets:** every release goes to Cloudflare (owner edition, deployed automatically from main) and to ADA (staff and pupil editions), all from the same checked artifact. Then the recovery ZIP and the SMTP owner report (FR-024, `docs/handoff/RELEASE-EMAIL.md`) follow.
- **Report:** one handoff in every form (OPS-069). A release is complete only when `scripts/release/finish.py complete` passes (OPS-070).
- **Usage limits:** never schedule wakeups. On a usage limit, write the exact resume point to `<state>/v<version-without-dot>/PROGRESS.md` (the agent's notes folder; the tools' work folder is `<state>/releases/v<version>/`, see the runbook) and stop; the owner restarts the work.
- **Legacy Maths progress:** questions 3423/3423 (100%) and sections 132/132, reported separately from slide, booklet and expanded-index progress.

## History
Earlier release handoffs (v0.51 onwards) and the historical notes kept here before v0.73 are in `docs/handoff/HISTORY.md`.
