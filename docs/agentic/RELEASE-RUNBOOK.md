# Luisa release runbook

These steps work for any AI agent, any engine and any person, and need no earlier conversation. Every command is in this repository. Private values come from `WORKSPACE.json` through `scripts/release/private.py` and are never printed. `<state>` means the private state folder: `$LUISA_STATE_DIR`, or `~/.local/share/luisa-agent-state` by default. `<v>` is the version, for example `0.73`, and `<vv>` is the same without the dot (`073`). Commands assume the bootstrapped interpreter, `python3` = `<state>/env/bin/python`, with `<state>/env/bin` first on `PATH`.

Stop only for a genuine blocker: an expired login, a macOS permission only the owner can grant, a doctor MISSING line that needs a human, or a usage limit. Never stop because of repository state (an open PR, an odd version number, a missing or duplicate file). Decide using the defaults in the brief, record the decision in the issue and in HANDOFF.md, and continue.

## A. Cold start
1. Clone `https://github.com/vyr66mbzmh-debug/Luisa` and read `AGENTS.md`, `HANDOFF.md` and the assigned issue. Run `git status` and `git worktree list`, and check open PRs with `gh pr list`.
2. Run `python3 scripts/bootstrap.py`, then apply the two `export` lines it prints.
3. Run `python3 scripts/luisa.py doctor`. Every line must say PASS. For each MISSING line, carry out its `action:` or report it to the owner as a blocker.
4. Record the start with `python3 scripts/usage.py start v<vv> --provider <engine> --model <model>`. Write `<state>/v<vv>/PROGRESS.md` (the resume point) and keep it current.
5. Record the brief's requirements on the issue and in `docs/requirements/register.json` before or while implementing (OPS-063). Regenerate `REQUIREMENTS.md` with `python3 scripts/luisa.py requirements`.

## B. Work and tests
6. Create a worktree and branch from `origin/main`, for example `git worktree add ../Luisa-v<vv> -b v<v>-<topic> origin/main`.
7. For a past-paper import, follow `scripts/import/README.md`. Source PDFs are read-only, are read with `python -I`, and never enter Git (the privacy gate enforces this).
8. Write the release spec `docs/releases/v<v>.json` and its handoff block `docs/releases/v<v>-handoff.md` (copy the latest pair). Then run `python3 scripts/release/docs.py apply docs/releases/v<v>.json --tokens "<token sentence so far>"`. It updates release.json, version-history.json, CHANGELOG.md, docs/ROADMAP.md, the HANDOFF.md release block (the old block moves to `docs/handoff/HISTORY.md`) and the release report.
9. Run `python3 scripts/luisa.py gate`. It runs check, report, the unit tests, scan, privacy and build, and must pass with 0 skips. Then run the browser suites with `python3 -m unittest tests.test_papers_selection tests.papers_print_browser` (the print suite is not part of discovery; it prints every past paper in every layout as real PDFs).
10. Run the dry-run QA against the local build: `python3 scripts/luisa.py build`, then `python3 scripts/release/qa_live.py owner --url http://127.0.0.1:<port>/` (serve `dist/` with `python3 scripts/luisa.py serve`) and `python3 scripts/release/qa_offline.py --local`.
11. Commit with the required trailers, push, and open a PR that names the issue and the requirement IDs.

## C. Independent review
12. Ask a reviewer under the reviewer role (`docs/agentic/REVIEWER-RULES.md`): any engine or person who did not write the change. Inputs: the PR number, head SHA, base SHA, issue, requirement IDs and the release spec. Output: one JSON record valid against `docs/agentic/review-record.schema.json`, kept privately at `<state>/releases/v<v>/review.json`.
13. If the verdict is `fix`, fix every finding, record its `resolution`, push, and request a new review of the new head. Land only on `ship` for the exact head.

## D. Land and build
14. From the PR worktree, run `python3 scripts/release/land_build.py --pr <N> --review-record <state>/releases/v<v>/review.json`. It waits for green exact-head CI, lands with `scripts/land.py` (no force, no skipped checks), fast-forwards the main checkout, proves the merged tree, builds the owner, staff and student editions, and runs check-artifact on each. Every later step runs **from the main checkout at the merged revision**.

## E. Deploy and verify
15. Cloudflare (owner edition) deploys main automatically. Run `python3 scripts/release/verify_owner.py`. It waits for the live manifest to show the merged revision, then runs `qa_live.py owner` (which includes the single-handoff check of the published report) and `qa_offline.py`.
16. Stage on ADA with `python3 scripts/release/ada.py stage`. It uploads dist-staff and dist-student into a new release folder, verifies the manifests and runs `nginx -t`.
17. Activate with `python3 scripts/release/ada.py activate`. It takes a private snapshot of the account database, switches the start script and restarts the service. It refuses if auth-server code changed unless `--allow-server-change` is given; that flag needs a reviewed server change.
18. Run `python3 scripts/release/qa_live.py ada` (staff and pupil, with temporary accounts that are removed afterwards), then `python3 scripts/release/ada.py accounts-check`. Accounts must be unchanged, apart from first sign-ins with `--allow-completed-first-signin`.
19. Rollback: if step 18 fails, run `python3 scripts/release/ada.py rollback` and record the failure. For Cloudflare, revert the merge with a new reviewed PR (never force-push), or roll back to the previous deployment in the Cloudflare dashboard (owner).

## F. Archive, report, close
20. Run `python3 scripts/release/finish.py archive`, which writes a recovery ZIP to `<master>/backups` and keeps the newest five. Then run `python3 scripts/release/finish.py cleanup`, which leaves ADA with only the active release folder.
21. Run `python3 scripts/release/finish.py check-published`. The live release report must equal the manifest and carry exactly one `Luisa v<v> handoff`.
22. Run `python3 scripts/release/finish.py report --intro "<one paragraph: what is live, what changed, decisions applied>"`. It sends the SMTP owner report with exactly one handoff and no private values (`docs/handoff/RELEASE-EMAIL.md`). If sending fails, record "notification pending" and tell the owner.
23. Post issue evidence: the merged revision, CI, review verdict, live checks (owner, offline, ADA staff and pupil), the archive name, the report status and every decision applied.
24. Log tokens: `python3 scripts/release/tokens.py since --transcript <session transcript> --state <state>/v<vv>/tokens-baseline.json` for the lead, and `tokens.py total --transcript <...>` for reviewers. Post the totals on the issue **with their source**. When the engine has no counter, write "token counts unavailable" and name the source used instead (`scripts/usage.py` account percentage, which is an estimate). Then run `python3 scripts/usage.py end v<vv> --tokens <total or unavailable>`.
25. Update HANDOFF.md if anything changed after the release, through a small docs PR. Set the register entries to implemented and verified with their evidence. Then run `python3 scripts/release/finish.py complete`. The release is not complete until it passes (OPS-070): HANDOFF.md, the register, issue evidence, the token log with its source, and the SMTP record. Close the issue.

## Usage limits
On a usage limit, stop. Write the exact resume point (branch, worktree, last completed step number, next command) to `<state>/v<vv>/PROGRESS.md`, and do not schedule wakeups or timers. The owner restarts the work, and the next agent resumes from PROGRESS.md and this runbook.
