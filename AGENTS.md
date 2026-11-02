# Luisa agent instructions

## Privacy and authority
Never commit credentials, account usage snapshots, personal paths/contact data, unpublished source corrections or owner documents. Source materials remain read-only outside this public Git repository. Respect runtime permissions; never disguise a denied operation. Preserve unrelated changes.

## Start with small context
Read HANDOFF.md, docs/agentic/LEAD-RULES.md and the assigned issue only. Consult docs/requirements/register.json by requirement ID and architecture/decisions only as needed. CLAUDE.md points here. Do not read the chat archive or whole material library.

## Mandatory output standard
- Luisa branding; public version increases by .01 for product releases; all version badges link to development progress.
- White slide background to viewport edges; whole slide fits without scrolling, clipping, overlap, tiny text or distorted diagrams. Consistent readable fonts; hanging indents for every numbered/bulleted item and subpart.
- Preserve every supplied teaching step, explanation, hint and meaningful diagram/arrow. Native LaTeX except explicit owner image exceptions.
- Independent, fully concealed answers with correct numbered pale-blue covers. No purple badges, stray question marks or obstructing ticks. Natural click/Space teaching order; rewrite before result; Reset correct.
- Student booklet: two original slides per A4 page; same titles/numbers; preserve supplied theory; omit only concealed answers and allocate useful handwriting space. New content must use available panel area from creation. Deferred improvement to accepted older layouts is separate from defects.
- Chapter delivery includes checked slides, student booklet AND correct textbook chapter PDF, connected in both libraries and verified online.
- Checked means source, maths, visual, interaction and print acceptance with evidence. Never replace these with a successful render. Invalidate affected approvals after edits.
- Reuse questions across skill/chapter views; preserve edition-specific references. Do not publicly label practice by its upstream question-bank provider.

## Workflow and efficiency
One bounded issue, branch and PR at a time by default. New independent work is backlog, not silent scope expansion. Lead owns shared catalogues, CI, dependency manifests and integration. Delegated implementers never publish; use isolated worktrees and fresh briefs only when authorised. No context forks or duplicate agents. One heavy job at a time; cap test/browser workers.
Run `python3 scripts/luisa.py gate` before landing; review according to risk. Never skip or loosen failures. Automatic publication after green checks is owner-authorised; every new release must also be copied to ADA from the same checked artifact and both deployments verified. Never call a push a live release. See docs/DEVOPS.md.
Record usage with `scripts/usage.py` at start/end and compact progress in HANDOFF.md. Provider/model counters may be unavailable: say so; account percentage deltas are estimates. No reset-credit spending or paid changes without current authority. No automatic wakeup/report schedules.
Continue only the authorised job; stop at explicit pause, completion, a genuine external blocker or enforced limit, saving exact commands/branch/worktree state. New sessions must inspect git/worktree state before editing.
For legacy Maths progress include questions completed /3423, percentage, and sections /132 separately from slide/booklet progress. Course order: Pure 1, Pure 2, Mechanics 1, Mechanics 2, Statistics 1, Statistics 2; Core Pure 1/2 separately.

## Authority
The owner-approved register in docs/requirements/register.json supersedes all historical README/LESSON_REQUIREMENTS and V10–V13 planning files. Those names remain provenance only. New explicit owner instructions take precedence; log them before implementation.
