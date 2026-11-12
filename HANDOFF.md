# Current Luisa handoff

<!-- LUISA-REPORT-HANDOFF v0.39 -->
**Luisa v0.39 is live on Cloudflare and ADA.** The production feature revision is `9584cbf3ec282db65bee515c5bd11bf348d5a207`; documentation revision `6a248b8ee4c14a5488eb6e080a69f36ce9132b25` records the release evidence and handoff. At that verification, both hosts served the same 8,145-file artifact with matching build-manifest SHA-256 `008f6e7e793b0669536bd124613dc07697bc394606ecf6041787dbc7fa30fd5c`. All 269 Standard and Further Maths solution PDFs were fetched from both hosts, returned `application/pdf`, and matched the approved source byte counts and SHA-256 fingerprints. The Cloudflare interface showed Skill solutions beside Print topic and Print skill. ADA's superseded release was removed after verification. Evidence: [v0.39 release evidence](docs/evidence/v039-release.json).

**Next agent:** The release is published and verified. Physical smartboard checks remain with the owner; the next task awaits the owner's assignment. Before starting, read `AGENTS.md`, `docs/agentic/LEAD-RULES.md`, this handoff and the relevant requirement IDs.

For a slide change, refresh its student and solution PDFs together, compile both reproduction bundles, and follow [BOOKLET-STANDARD.md](docs/handoff/BOOKLET-STANDARD.md). For a release, update GitHub requirements and evidence, refresh this handoff when continuation instructions change, run `python3 scripts/luisa.py gate`, and verify the published revision and changed resources on both hosts. Follow [RELEASE-EMAIL.md](docs/handoff/RELEASE-EMAIL.md) to send the full Luisa Report with the tagged handoff at the end. Record the SMTP outcome privately.
<!-- END LUISA-REPORT-HANDOFF -->

## Historical release notes

## v0.38 solution covers

Every chapter solution booklet has a red Solutions subtitle beneath its cover title. The 62 updated PDF fingerprints are in docs/evidence/v038-solutions.json. The owner collection and its PDF-backed LaTeX assets use these same files.

## v0.37 chapter solutions

The owner selected v0.37 for the solutions release. All 62 chapter PDFs match the repaired acceptance hashes across 1,496 pages. Teaching chapters, player controls, textbook topics, Development progress and offline chapter downloads use the corresponding solution resources. Both live deployments and all 62 solution hashes were verified. The release evidence is in docs/evidence/v037-release.json. Physical-device checks remain with the owner.

## Historical v0.36 integration assignment

Read [V036-SOLUTIONS-INTEGRATION.md](docs/handoff/V036-SOLUTIONS-INTEGRATION.md). The owner now authorises verified solution PDFs in teaching chapters, relevant View by textbook topics and Development progress. This supersedes earlier private-only instructions for solution PDFs; LaTeX originals and source/audit materials remain private. Every slide change must refresh both student and solution booklets and their reproduction bundles. All 62 local solution bundles are complete and repaired for Apple Quartz; website integration is pending. v0.36 already exists, so follow the handoff version/cache instructions rather than treating it as a fresh unpublished release.


Updated 9 November 2026. Read AGENTS.md and docs/agentic/LEAD-RULES.md, then the task-specific documents below.

## Booklet requirements and next solution task

- [BOOKLET-STANDARD.md](docs/handoff/BOOKLET-STANDARD.md) is the consolidated design, filename, document-location and selective replacement specification. Apply BKT-035, BKT-036-COVER, BKT-036-SOLUTIONS, BKT-036-ORIGINALS and BKT-036-RETENTION from the canonical requirement register.
- [SOLUTIONS-NEXT-AGENT.md](docs/handoff/SOLUTIONS-NEXT-AGENT.md) is the continuation brief requested for Astra with medium reasoning. It records prototype failures, regression cases and acceptance checks.
- The private workspace map resolves machine-specific paths. Final student copies are in `../Students Handout/`; private solution copies belong in `../Student Handout Solutions/`. Each collection has `_Latex original/<Book>/` reproduction bundles and the same eight book folders.
- The owner requires selective latest-only replacement. After a replacement chapter bundle is verified, install it at its canonical paths and delete that chapter's superseded generated PDF/LaTeX variants and obsolete assets. Preserve other chapters, original source materials and required current aliases/assets. The standard defines the full scope.

## Verified student baseline

Luisa v0.36 student booklets were published on Cloudflare and ADA at `41d724dcdfa2acbe21b8b5f622bf2488de16d773`. Both live manifests matched all 7,811 files and 326 fetched resources per host. Saved v0.35 downloads updated to v0.36 and reopened offline. The recovery archive was verified, ADA's prior release removed after verification, and the final HTML Luisa Report was accepted by SMTP on 8 November 2026 at 22:01 UTC.

All 62 student booklets, 2,947 teaching panels and 1,489 A4 pages are the reference set. The coloured first panels were independently checked with white 36pt Georgia Bold titles. Later teaching content and owner copies were verified. The 62 student PDF-backed LaTeX reproduction originals compiled successfully. Evidence is docs/evidence/v036-booklets.json and docs/evidence/v036-acceptance.json. Physical print/device checks remain with the owner.

## Historical private solution status

The owner stopped solution work on 8 November and requested completion with another model. Existing private solution PDFs and their LaTeX sources remain unfinished drafts with known defects. Their counts and successful renders do not establish acceptance. The next agent can resume under the owner's solution-completion instruction using the dedicated brief.

The private stop record is `../materials/build/output/v035-final/SOLUTIONS-STOPPED-CHECKPOINT.json`. Candidate authoring scripts live in `../materials/build/scripts/v035-final/`. They require inspection and correction. The latest per-field prototype stopped on Statistics Year 1 Chapter 2 slide 37 because hidden black text beneath an opaque student cover was misclassified as a caption. Explicit ownership also missed geometrically masked working. The brief records these issues and the PDF containment trial.

Keep source/output fingerprints tied to the material actually checked. For scoped regeneration, preserve unselected entries and mark changed unselected chapters stale. Resume from verified source and per-chapter evidence before replacing private drafts.

All release and development reports begin with a visible Luisa website link. Use `./` on website pages to preserve the ADA prefix.

Legacy Maths questions are 3,423 / 3,423 (100%), with 132 / 132 sections.

# v0.35 booklet standard

BKT-035 applies to all current and future student booklets. Use descriptive BookYear_ChNN_Chapter_Title.pdf filenames, no Luisa in panel headers, and a Data Collection style first title panel. Its banner names Subject Year N Chapter N - Topic. Later panels preserve their layout and teaching content. Keep the eight book folders of matching owner copies current. Evidence is docs/evidence/v035-booklets.json.

# Luisa handoff

## v0.34 teaching release

Start with docs/evidence/v034-acceptance.json. It records the 62 deck and booklet fingerprints, all 94 named original slide references, and the mapping after removing six Statistics course maps and the final Probability extension. The catalogue contains 2,947 slides and 1,489 A4 booklet pages. Statistics accounts for 463 slides and 234 pages.

All live teaching implementations share lesson-controls.js and lesson-touch.js. Source answer elements have explicit owners. Exercise identifiers, source animation targets and meaningful print-only captions survive separate screen and booklet rendering. The linked STEP sketch and Exercise 12J solution PDFs are included in the Pure Year 1 Chapter 12 offline pack. Private v034 authoring and review outputs are in the established materials build directories. Booklet generation uses the same origin as the slide viewer so the printed mathematics uses the supplied fonts.

Validate the chapter report with python3 scripts/report_chapters.py development-progress.html release-report-0.34.html. The page counts and accepted hashes come from the release evidence. Run python3 scripts/luisa.py gate and require the three current-head CI checks before landing. Verify the production manifests, chapter resources, navigation and the saved v0.33 to v0.34 transition on both hosts. The private v034 release directory holds host verification, recovery and final SMTP submission records. Physical Magic Mouse Chrome/Safari and iPad confirmation remain open.

Legacy Maths questions are 3,423 / 3,423 (100%), with 132 / 132 sections.

## v0.33 chapter reports
Statistics acceptance covers both years (470 slides, 10 booklets, 236 printed pages). The artifact fingerprints and review scope are in docs/evidence/v033-statistics.json. After editing any signed deck or booklet, review the changed material before renewing its acceptance.
Run `python3 scripts/report_chapters.py development-progress.html release-report-0.33.html` after any chapter update, using the new report filename for subsequent releases. Link every available resource independently of final acceptance. Student booklet, source textbook and practice chapter are distinct resources. Render checks alone do not qualify a chapter for final acceptance.

## v0.31 teaching navigation
Implement WEB-031 and SLD-031 in every future teaching player and chapter listing. All seven current players load lesson-touch.js against the slide region and delegate gestures to the existing controls. Standard Maths practice PDFs use the teaching catalogue practice field. Physical smartboard and iPad checks remain with the owner.

## v0.30 Statistics release
Track STA-030, SLD-030, WEB-030 and PUB-030. Slide 55 uses original covers 1, 4, 2, 3, each labelled ?. Include the outstanding Statistics chapters for both years. All ten Statistics chapters have slides and two-up booklets. Source-matched cover labels and explicit exercise overrides take precedence. Full visual and print acceptance for the newly uploaded chapters remains outstanding. See the release report and private v030 browser/print evidence. Verify both hosts and recovery archive before the final email.

## v0.29 release handoff
Statistics Year 1 Chapter 2 uses the replacement 90-slide source and a 45-page student booklet. Slide 68 requires separate Midpoints, Mean and Standard deviation controls. Maintain these in both outputs. See docs/evidence/v029-acceptance.json.
Every release must name implemented requirement IDs on Development progress, link to the chronological version log and include direct links to affected practice booklets alongside the teaching resources. Publish and verify Cloudflare and ADA, finish the recovery archive and handoff, then send the full HTML Luisa Report as the final release action. Only the private SMTP outcome record follows sending. Physical iPad confirmation is with the owner.
Updated: 2026-11-05. Read AGENTS.md and docs/agentic/LEAD-RULES.md first.

## Completed v0.28 — issue #18 / PR #19
Branch task/v028-library-offline. Owner clarified Practice Chapter means the existing chapter-folder PDFs, not generated Print topic PDFs. All 45 Maths chapters now have practice resources; Further Maths retains textbook buttons. Missing Statistics/Moments textbook extracts restored. Offline inventory includes print PDFs and supplementary skill packs; new files require refreshing downloads. Toolbar focused fullscreen and Edexcel-only Further topic print implemented. Browser tests under / and /AL/ pass; physical iPad not newly tested. See docs/evidence/v028-acceptance.json. Published revision e87f9b3662db322872ac5c569668161290f97e13 verified on both Cloudflare and ADA: all 6,941 manifest entries match, with 92 changed/core resources fetched and hash-checked per host. Clean build/test/scan and independent review passed. Recovery ZIP saved; only latest release retained on ADA. See docs/evidence/v028-release.json. Final HTML report submitted through the configured SMTP adapter; private send evidence records acceptance. Work complete; wait for owner instructions.

## Mandatory release email — all future agents
FR-024 is a standing owner requirement, reaffirmed 2026-11-05. Every published release must end with the full HTML report emailed using the existing private SMTP adapter, unless explicitly deferred by the owner. Do not interpret a new chat as removal of authorisation. Read docs/handoff/RELEASE-EMAIL.md for the command, content, checks and failure handling. The private WORKSPACE.json mailSender resolves the configured account; no Apple Mail or unlocked desktop is required. Public v0.27 is unchanged by this documentation task. Delivery for v0.25–v0.27 has not been verified here; do not infer sent status from publication.

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

### v0.32
Use each chapter’s catalogue resources for the first column of development progress. Keep mouse drag and touch swipe navigation consistent. Check slide 26’s grouped median-rule reveal and slide 28’s nine independent answer positions against the printed student booklet. Only mark Statistics chapters checked after full source, interaction, visual and print acceptance. Keep the final Luisa Report and disable the separate Cloudflare deployment email only.
