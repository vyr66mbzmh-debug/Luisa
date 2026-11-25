# Luisa agent instructions

## Quick start for any AI agent
These steps work with any engine or person, and need no earlier conversation:
1. Read this file, then `HANDOFF.md` (current state, "Tooling, access and where everything lives") and the assigned GitHub issue.
2. Run `python3 scripts/bootstrap.py`, which builds the pinned environment in the private state folder. Then use `<state>/env/bin/python` with `env/bin` first on `PATH` and `LUISA_BROWSER_CHANNEL` as printed.
3. Run `python3 scripts/luisa.py doctor`. Every line must say PASS. A MISSING line names the human action; that is a genuine blocker, so report it.
4. Follow `docs/agentic/RELEASE-RUNBOOK.md` for any import, release, deployment or owner report. Its numbered steps use only tooling in this repository.
5. Private values come only from `WORKSPACE.json` through `scripts/release/private.py`. Never print, commit or paste them.
Vendor files (CLAUDE.md and similar) only point here.

## Privacy and authority
Never commit credentials, account usage snapshots, personal paths/contact data, unpublished source corrections or owner documents. Source materials remain read-only outside this public Git repository. Respect runtime permissions; never disguise a denied operation. Preserve unrelated changes.

## Start with small context
Read HANDOFF.md, docs/agentic/LEAD-RULES.md and the assigned issue only. Consult docs/requirements/register.json by requirement ID and architecture/decisions only as needed. CLAUDE.md points here. Do not read the chat archive or whole material library.

## Mandatory output standard
- Luisa branding; public version increases by .01 for product releases; all version badges link to development progress.
- White slide background to viewport edges; whole slide fits without scrolling, clipping, overlap, tiny text or distorted diagrams. Consistent readable fonts; hanging indents for every numbered/bulleted item and subpart.
- Preserve every supplied teaching step, explanation, hint and meaningful diagram/arrow. Native LaTeX except explicit owner image exceptions.
- Independent, fully concealed answers with pale-blue covers showing the source prompt. From v0.34 follow UI-034: use the approved subtle button style on screen, omit standalone question marks, and keep printed answer areas flat with light borders. Use the actual exercise identifier when requested. No purple badges or obstructing ticks. Natural click/Space teaching order; rewrite before result; Reset correct.
- Student booklet: two original slides per A4 page; same titles/numbers; preserve supplied theory; omit only concealed answers and allocate useful handwriting space. New content must use available panel area from creation. Deferred improvement to accepted older layouts is separate from defects.
- Chapter delivery includes checked slides, student booklet AND correct textbook chapter PDF, connected in both libraries and verified online.
- Checked means source, maths, visual, interaction and print acceptance with evidence. Never replace these with a successful render. Invalidate affected approvals after edits.
- Reuse questions across skill/chapter views; preserve edition-specific references. Do not publicly label practice by its upstream question-bank provider.

- Owner-authorised v0.26 PWA-001: installable across Apple, Windows and Android systems, explicitly including the iiyama smartboard, explicit offline downloads/readiness and real-device offline acceptance. Existing caching is not proof of compliance. The owner explicitly authorised implementation and checked publication in v0.26 on 2026-11-03, superseding the previous deferral.

## Workflow and efficiency
On Mac, keep the machine awake during active authorised work with temporary bounded idle-system/display-sleep and user-active assertions; verify them and release job-owned assertions when work stops. Do not change persistent lock/password settings or bypass a manual lock. See OPS-008.
One bounded issue, branch and PR at a time by default. New independent work is backlog, not silent scope expansion. Lead owns shared catalogues, CI, dependency manifests and integration. Delegated implementers never publish; use isolated worktrees and fresh briefs only when authorised. No context forks or duplicate agents. One heavy job at a time; cap test/browser workers.
Run `python3 scripts/luisa.py gate` before landing; review according to risk. Never skip or loosen failures. Automatic publication after green checks is owner-authorised; every new release must also be copied to ADA from the same checked artifact and both deployments verified. Never call a push a live release. See docs/DEVOPS.md. Every published release also requires the final owner email via the private SMTP adapter (FR-024); this is standing authorisation across agents/chats. Follow docs/handoff/RELEASE-EMAIL.md, record send outcome, and flag any failure as notification pending. Do not silently skip email or depend on Apple Mail/unlocked UI.
Record usage with `scripts/usage.py` at start/end and compact progress in HANDOFF.md. Provider/model counters may be unavailable: say so; account percentage deltas are estimates. No reset-credit spending or paid changes without current authority. No automatic wakeup/report schedules.
OPS-063 (standing): whenever the owner gives new requirements, record them on GitHub and in docs/requirements/register.json before or while implementing; at the end of every job, update HANDOFF.md and log the handoff and the token usage (with its source) to the job's GitHub issue before reporting done.
Continue only the authorised job; stop at explicit pause, completion, a genuine external blocker or enforced limit, saving exact commands/branch/worktree state. New sessions must inspect git/worktree state before editing.
For legacy Maths progress include questions completed /3423, percentage, and sections /132 separately from slide/booklet progress. Course order: Pure 1, Pure 2, Mechanics 1, Mechanics 2, Statistics 1, Statistics 2; Core Pure 1/2 separately.

## Authority
The owner-approved register in docs/requirements/register.json supersedes all historical README/LESSON_REQUIREMENTS and V10–V13 planning files. Those names remain provenance only. New explicit owner instructions take precedence; log them before implementation.

## Teaching slides, all books (RES-081)
Use the shared Luisa lesson font and visibly raised, keyboard-operable reveal buttons. Hide the answer content itself until its button is activated. Check for exposed glyphs at every edge before revealing and again after Reset. Student print uses flat writing areas.
Use one banner. For textbook exercises it identifies the exercise and the **printed book page**. Start immediately with the question, identify it by number and place its complete working behind **Solution** on that same slide. Long working may advance in steps while the question remains visible. Remove exercise-only divider slides and retain source assignment instructions with the relevant exercise.
For multipart examples, reveal each part's diagram and then its solution before starting the next part. Typeset mechanics diagrams in LaTeX with legible labels, arrowheads, directions and units. Explain abbreviations on first use and distinguish signed quantities from magnitudes. Write allocations as [3 marks] or [1 mark] and attach any method and accuracy marks to the line that earns them. Compare covered, revealed and printed views against the source before release.
