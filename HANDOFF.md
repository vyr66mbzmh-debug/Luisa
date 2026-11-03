# Luisa handoff
Updated: 2026-11-03. Read AGENTS.md and docs/agentic/LEAD-RULES.md first.

## Completed v0.27 scope
Issue #15; PRs #16 and #17 squash-merged. Final checked release a9f0365e0893fda9d8185b8bca686c23d9e1a976 is live on Cloudflare and ADA. Both6867-entry manifests and241 fetched resources per host match the same artifact. All96 replacement Pure Year2 chapter9 originals are delivered as102 teaching panels,51 matching booklet pages and42 textbook pages. Title is Differentiation; overlapping old variants are superseded. Source/maths/visual/interaction/print acceptance: docs/evidence/v027-acceptance.json. Release: docs/evidence/v027-release.json.

Installed-app documents have visible Back controls. Live offline booklet/textbook rendering, page navigation, exact slide/reveal restoration, return to originating downloads page and offline reload pass on both hosts in desktop Chromium standalone emulation. This is not physical iPad acceptance. ADA initially served .mjs with an invalid module MIME type; unchanged PDF.js modules now use .js, and both live module headers are checked.

Owner requires only the latest Luisa release on ADA. Superseded release directories and old source/deployment archives were removed. No historical Luisa backup remains there; recovery stays outside ADA in Cloudflare and OneDrive. OPS-002/DEVOPS record capacity checks, staging, directory activation and cleanup after verification. Unrelated server files preserved. Usage phase boundaries, source usage and detailed acceptance remain privately in materials/build/output/v027; phase allocation is approximate and includes cached context, not an exact provider bill. Work complete; wait for the next owner task. No schedules.

## Completed v0.26 scope
Issue #13; PR #14 squash-merged as272f74c127a749a4127e8925d162664818d4ce42. Current follow-up branch task/13-v026-release-evidence. Owner authorised checked publication; on 2026-11-03 explicitly paused ADA work and skipped its v0.26 copy because ADA is down. Retry ADA with v0.27. All11 requested chapters are locally agent accepted: Pure Year2 10/11/12, Mechanics Year2 6/7/8, Core Pure1 3/5, Core Pure2 6/7/8. Total571 displayed slides,289 booklet pages,260 textbook pages. See docs/evidence/v026-chapters.json. Cloudflare production v0.26 verified:6644 manifest entries match and437 actual resources hash-checked. ADA v0.26 is skipped by explicit owner instruction; no ADA deployment is claimed. See docs/evidence/v026-release.json.

Owner approved splitting Integration original82 into7 readable panels, with matching board/booklet numbering.110 originals become116 displayed slides. Vectors22-slide recheck restores intermediate steps and diagrams. All chapter-specific source/math/visual/interaction/print and both-library checks pass; private detailed evidence and source usage stay in OneDrive materials/build/output/v026.

PWA-001 deferral is explicitly superseded. Owner confirms Vectors works offline on iPad Pro12.9 fifth generation, reported iPadOS27.2. One-action Download all implemented; filter/busy/failure/retry, stale-catalogue and root/AL offline checks pass. Root/AL worker termination, replacement identity, old offline resources and retry pass. Final real-library Download all saves62 packs at both prefixes and all11 requested chapter resources open offline. Testing evidence is recorded in docs/evidence/v026-offline-preview.json. Physical testing of other platforms and the final bulk-download build remains unclaimed. Existing Pure1 chapters10/12 missing dependencies remain explicitly unavailable.

The v0.26 ADA pause was superseded by the owner’s v0.27 dual-host instruction. v0.26 itself remains historically skipped; its delivered chapters are included in v0.27. No automatic schedules.

## Completed v0.25 scope
Issue #10: owner authorised v0.25 conversion of Pure Year 2 chapters 6 and 7 and Core Pure 1 chapters 1 and 4, with teaching slides, two-up student booklets and linked textbook chapters. Publication to Cloudflare and ADA is explicitly authorised after acceptance and repository checks. PR #11 was squash-merged. v0.25 is live on Cloudflare and ADA at checked release revision eb8cbb43fa6e822f9b93797f29061213f732159e. Both manifests and 96 fetched resources per host match the same 6,235-file artifact. See docs/evidence/v025-release.json. This documentation follow-up records that verified release; inspect the live manifest for any later documentation-only revision.

All four chapters are agent accepted: Pure Year 2 chapters 6/7 have 46/53 slides and 23/27 booklet pages; Core Pure 1 chapters 1/4 have 41/48 slides and 21/24 booklet pages. All 188 source slides and 95 booklet pages received source/maths/visual/print review, with independent review and resolved findings. Three viewport sizes, each individual answer/cover, actual Space ordering and Reset were checked. All 88 extracted textbook pages match the original printed content. Both libraries and viewer resource links work below a non-root prefix; the library return preserves the chosen chapter. See docs/evidence/v025-chapters.json. Owner acceptance is not claimed.

The four original decks and both textbooks are readable after OneDrive restoration. Private authoring inputs, scripts, per-slide/page evidence and usage remain in the OneDrive materials build folder. The gate passed 158 requirements, 122 catalogue destinations and 13 tooling tests; current-head remote build/test/scan passed before squash merge. The release was rebuilt cleanly from the merged revision. Cloudflare was verified first, then the same artifact was staged, fully hashed, copied to ADA and verified online. The prior ADA artifact and recovery copy were verified against all 6,155 prior manifest entries. No credentials were created or expanded.

OPS-008 records the owner-reaffirmed requirement to keep the Mac awake during active work with bounded temporary assertions, verified and released when work stops. Do not let idle locking interrupt development; do not bypass a manual lock or change persistent password/security settings.

PR #9 was merged externally by the owner before v0.25; it only added requirements documentation. Its deferral is now superseded by the explicit v0.26 owner instruction.

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

## PWA requirement history (superseded deferral)
PWA-001 restores the owner’s original installable/offline app requirement, now explicitly covering Apple (iOS/iPadOS/macOS), Windows and Android systems, including the actual iiyama smartboard. See register.json for acceptance criteria and ROADMAP.md for future work. Implementation and partial verification are recorded under PWA-001; other physical devices remain unverified. Owner explicitly prohibited changes to live v0.24 or another publication for this documentation task. PR #9 was merged externally before this task; its implementation is now authorised for v0.26.

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
