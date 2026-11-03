# Luisa handoff
Updated: 2026-11-03. Read AGENTS.md and docs/agentic/LEAD-RULES.md first.

## Current scope
Issue #10: owner authorised v0.25 conversion of Pure Year 2 chapters 6 and 7 and Core Pure 1 chapters 1 and 4, with teaching slides, two-up student booklets and linked textbook chapters. Publication to Cloudflare and ADA is explicitly authorised after acceptance and repository checks. Chapter delivery is locally complete on task/10-v025-four-chapters; preserve this branch and its assets. No v0.25 release has been published.

All four chapters are agent accepted: Pure Year 2 chapters 6/7 have 46/53 slides and 23/27 booklet pages; Core Pure 1 chapters 1/4 have 41/48 slides and 21/24 booklet pages. All 188 source slides and 95 booklet pages received source/maths/visual/print review, with independent review and resolved findings. Three viewport sizes, each individual answer/cover, actual Space ordering and Reset were checked. All 88 extracted textbook pages match the original printed content. Both libraries and viewer resource links work below a non-root prefix; the library return preserves the chosen chapter. See docs/evidence/v025-chapters.json. Owner acceptance is not claimed.

The four original decks and both textbooks are readable after OneDrive restoration. Private authoring inputs, scripts, per-slide/page evidence and usage remain in the OneDrive materials build folder. The local gate passed 158 requirements, 122 catalogue destinations and 13 tooling tests; final head verification and remote build/test/scan must still precede landing. The checked task branch is published through the existing GitHub Desktop connection; no credentials were created or expanded. OPS-008 now records the owner-reaffirmed temporary keep-awake requirement. Neither Cloudflare nor ADA has received v0.25 yet. ADA's established public directory is reachable. Complete the PR/check/squash process, verify Cloudflare, then copy the same checked artifact to ADA and verify both. Private checkpoint records exact continuation steps.

PWA-001 remains deferred. PR #9 was merged externally by the owner before this branch; it only adds requirements documentation. This task does not implement PWA features.

Usage counters are available for this chat, including cached input. Earlier activities interleaved conversion, checking and shared implementation, so an exact retrospective phase breakdown must not be invented. Private usage evidence records the available boundaries.

## Foundation record
- Repository: https://github.com/vyr66mbzmh-debug/Luisa ; same history and repository ID, local origin updated.
- Foundation PR #3 merged; production manifest verified revision 358d1be, version 0.24, clean. Issue #1 closed; roadmap #2 tracks future scope. A small evidence-record PR follows; inspect current main/live manifest for its exact revision.
- Canonical register: docs/requirements/register.json (158 requirements); generated REQUIREMENTS.md beside it. Historical assertions are not fresh acceptance.
- Main protection: PR, build/test/scan, up-to-date branches, linear history and no bypass; squash merge only. Secret Protection and push protection enabled.
- Cloudflare production: python3 scripts/luisa.py gate, output dist, PYTHON_VERSION=3.12.8. Renamed-repository previews succeeded. Verify each merged revision online.
- Development project: https://github.com/users/vyr66mbzmh-debug/projects/1 (owner access); Status/Priority/PR/Wave fields. Built-in project workflows, no new token.
- Local gate and CI passed: 156 requirements, 110 catalogue destinations, 9 tooling tests, 6155 packaged public files. This is infrastructure evidence, not renewed content acceptance.
- No new chapter work, schedules, paid services or credentials in this setup.

## ADA is a required release target
Every new published website version must also be copied to ADA from the same checked static artifact. Use the established web server; no Python server or SSH tunnel. Keep internal SSH/target details in private WORKSPACE.json. Verify the configured URL prefix, logo, CSS, libraries, teaching slides and PDFs live; record both hosts' revision/version before declaring release complete. See docs/DEVOPS.md.

## New mandatory requirement, deferred
PWA-001 restores the owner’s original installable/offline app requirement, now explicitly covering Apple (iOS/iPadOS/macOS), Windows and Android systems, including the actual iiyama smartboard. See register.json for acceptance criteria and ROADMAP.md for future work. Status planned / not_checked; existing manifest/service-worker caching does not establish acceptance. Owner explicitly prohibited changes to live v0.24 or another publication for this documentation task. PR #9 was merged externally before this task; its implementation remains deferred.

## Start next session
1. Inspect git status, git worktree list, open PRs and remote main. Preserve unfinished owner work; do not force reset.
2. Read assigned issue and relevant requirement IDs only. docs/handoff/START-HERE.md has the new-chat prompt.
3. Use one issue/branch/PR, targeted checks, then full gate and risk review. Verify live manifest and actual changed links after automatic deployment.
4. Record usage with scripts/usage.py, update evidence and this handoff. GitHub CLI is absent on the original machine; signed-in UI was used, while connector is read-only. Do not widen access silently.

## Relevant files and inputs
- docs/ARCHITECTURE.md, docs/TWELVE-FACTOR.md, docs/DEVOPS.md.
- docs/ROADMAP.md: remaining availability and deferred features; docs/ACCEPTANCE.md: source/maths/visual/interaction/print evidence.
- docs/OWNER-ACTIONS.md: verified controls and remaining portability boundaries.
- Private LUISA_STATE_DIR/WORKSPACE.json: original machine paths, authoring/mail locations; usage.jsonl is private.
- OneDrive can dehydrate both assets and Git blobs. Use a temporary clone outside OneDrive for full validation if needed; preserve the canonical master and uncommitted overlays.

## Baseline and boundaries
Legacy Maths questions: 3423/3423 (100%); sections 132/132, separate from expanded indexes and teaching progress. Full fresh acceptance is not inferred from those totals.
The public clone serves existing outputs. Original decks/books and historical authoring toolchain are private external inputs; new content needs targeted source access. Full chapter-authoring portability remains a follow-up.
