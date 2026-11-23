# Luisa release runbook

These steps work for any AI agent, any engine or any person, and need no earlier conversation. Every command is in this repository. Private values come from `WORKSPACE.json` through `scripts/release/private.py`, and scripts never print them.

**Placeholders and folders.**
- `<state>` is the private state folder: `$LUISA_STATE_DIR`, or by default `~/.local/share/luisa-agent-state`.
- `<v>` is the version (for example `0.73`) and `<vv>` is the version without the dot (`073`).
- Two private folders per release:
  - `<state>/v<vv>/` holds the agent's own notes: `PROGRESS.md` and the token baseline.
  - `<state>/releases/v<v>/` is the tools' work folder: QA results, printed PDFs, the review record and the merged revision.

**Interpreter and shell.**
- Commands assume the bootstrapped interpreter: `python3` means `<state>/env/bin/python`, with `<state>/env/bin` first on `PATH`.
- The `export` lines that bootstrap prints are for POSIX shells (sh, bash, zsh). In csh or tcsh, use `setenv PATH "<state>/env/bin:$PATH"` and `setenv LUISA_BROWSER_CHANNEL <channel>`, with the folder and channel bootstrap printed.

**When to stop.** Stop only for a genuine blocker: an expired login, a macOS permission only the owner can grant, a doctor MISSING line that needs a human, or a usage limit. Never stop because of repository state (an open PR, an odd version number, a missing or duplicate file). Decide using the defaults in the brief, record the decision in the issue and in HANDOFF.md, and continue.

## A. Cold start
1. Clone `https://github.com/vyr66mbzmh-debug/Luisa`. Read `AGENTS.md`, `HANDOFF.md` and the assigned issue. Inspect the current state with `git status`, `git worktree list` and `gh pr list`.
2. Run `python3 scripts/bootstrap.py`, then apply the two environment lines it prints.
3. Run `python3 scripts/luisa.py doctor`. Every line must say PASS. For each MISSING line, carry out its `action:` or report it to the owner as a blocker.
4. Record the start:
   - `python3 scripts/usage.py start v<vv> --provider <engine> --model <model>`
   - If the engine writes a JSON Lines transcript (see step 24), also run `python3 scripts/release/tokens.py baseline --transcript <transcript> --state <state>/v<vv>/tokens-baseline.json`. Otherwise note the start time (UTC, ISO 8601) in PROGRESS.md.
   - Write `<state>/v<vv>/PROGRESS.md` (the resume point) and keep it current.
5. Record the brief's requirements on the issue and in `docs/requirements/register.json` before or while implementing (OPS-063). Then regenerate `REQUIREMENTS.md` with `python3 scripts/luisa.py requirements`.

## B. Work and tests
6. Create a worktree and branch from `origin/main`, for example `git worktree add ../Luisa-v<vv> -b v<v>-<topic> origin/main`. Keep a separate clean worktree with `main` checked out (the primary clone usually is one); `land_build.py` fast-forwards it.
7. For a past-paper import, follow `scripts/import/README.md`. Source PDFs are read-only, are read with `python -I`, and never enter Git; the privacy gate enforces this.
8. Write the release spec `docs/releases/v<v>.json` and its handoff block `docs/releases/v<v>-handoff.md` (copy the latest pair). Write the handoff block as it should read **after** the release, because the report is built and published before deployment. Point to the issue for the live evidence, and set the register entries to `implemented`/`agent_checked` with the issue as evidence. Then run `python3 scripts/release/docs.py apply docs/releases/v<v>.json --tokens "<token sentence so far>"`. This updates:
   - release.json and version-history.json;
   - CHANGELOG.md and docs/ROADMAP.md;
   - the HANDOFF.md release block (the old block moves to `docs/handoff/HISTORY.md`);
   - the release report.
9. Run `python3 scripts/luisa.py gate`. It runs check, report, the unit tests, scan, privacy and build, and must pass with 0 skips. Then run the browser suites with `python3 -m unittest tests.test_papers_selection tests.papers_print_browser` (about 7 minutes; the print suite is not part of discovery, and it prints every past paper in every layout as real PDFs).
10. Dry-run QA against the local build:
    - `python3 scripts/luisa.py build`
    - In the background, `python3 scripts/luisa.py serve`, which serves `dist/` at `http://127.0.0.1:8778/`.
    - `python3 scripts/release/qa_live.py owner --url http://127.0.0.1:8778/`, then stop the server.
    - `python3 scripts/release/qa_offline.py --local` (it serves `dist/` itself).
11. Commit with the required trailers, push, and open a PR that names the issue and the requirement IDs.

## C. Independent review
12. Get an independent reviewer under the reviewer role (`docs/agentic/REVIEWER-RULES.md`). Any engine or person who did not write the change will do:
    - a fresh session of any engine with no earlier conversation;
    - another provider's model;
    - the owner or another person.

    Inputs: the PR number, head SHA, base SHA, issue, requirement IDs and the release spec. Output: one JSON record valid against `docs/agentic/review-record.schema.json`. The reviewer needs no private configuration. The lead saves the reviewer's JSON verbatim to `<state>/releases/v<v>/review.json`.
13. If the verdict is `fix`, fix every finding, push, and request a new review of the new head; the new record lists each `resolution`. Land only on `ship` for the exact head. Never edit a record's verdict.

## D. Land and build
14. From the PR worktree (clean, at the reviewed head), run `python3 scripts/release/land_build.py --pr <N> --review-record <state>/releases/v<v>/review.json`. It does the following:
    - waits for green exact-head CI;
    - lands with `scripts/land.py`, which validates the record and reruns the full gate (about 3–4 minutes); there is no force and no skipped check;
    - fast-forwards the main worktree and proves the merged tree;
    - builds the owner, staff and student editions, and runs check-artifact on each.

    If it stops after the merge, rerun it with `--skip-land` to resume at the build. Every later step runs **from the main worktree at the merged revision**.

## E. Deploy and verify
15. Cloudflare (owner edition) deploys main automatically. Run `python3 scripts/release/verify_owner.py`. It waits for the live manifest to show the merged revision, then runs:
    - `qa_live.py owner`, which includes the single-handoff check of the published report;
    - `qa_offline.py`.
16. Stage on ADA with `python3 scripts/release/ada.py stage`. It uploads dist-staff and dist-student into a new release folder, verifies the manifests and runs `nginx -t`. `python3 scripts/release/ada.py status` shows the live release at any time.
17. Activate with `python3 scripts/release/ada.py activate`. It snapshots the account database privately (`<state>/ada-student/`), switches the start script and restarts the service. It refuses if the auth-server code changed, unless `--allow-server-change` is given, which needs a reviewed server change.
18. Run `python3 scripts/release/qa_live.py ada`. It covers staff and pupil, using temporary accounts that it creates only if unused and removes afterwards. Then run `python3 scripts/release/ada.py accounts-check`. Accounts must be unchanged, except for first sign-ins allowed with `--allow-completed-first-signin`. If a QA run was interrupted, `python3 scripts/release/qa_live.py ada-cleanup` removes its temporary accounts; they are recorded privately.
19. Rollback.
    - **ADA:** if step 18 fails, run `python3 scripts/release/ada.py rollback` (back to the previous release folder), record the failure on the issue, and stop the release.
    - **Account database:** if `accounts-check` reports changed accounts, do **not** restore the database yourself. A restore would discard any sign-ins or password changes since the snapshot. Report the failure and the snapshot's file name (not its path) to the owner, who decides.
    - **Cloudflare:** revert the merge with a new reviewed PR (never force-push), or ask the owner to roll back to the previous deployment in the Cloudflare dashboard.

## F. Archive, report, close
20. Run `python3 scripts/release/finish.py archive`, which writes the recovery ZIP to `<master>/backups` and keeps the newest five. Then run `python3 scripts/release/finish.py cleanup`, which leaves ADA with only the active release folder.
21. Run `python3 scripts/release/finish.py check-published`. The live release report must equal the manifest and carry exactly one `Luisa v<v> handoff`.
22. Run `python3 scripts/release/finish.py report --intro "<one paragraph: what is live, what changed, decisions applied>"`. It sends the SMTP owner report with exactly one handoff and no private values (`docs/handoff/RELEASE-EMAIL.md`). If sending fails, record "notification pending" and tell the owner.
23. Post the evidence with `gh issue comment <issue> --body-file <file>`, written in a private file first. The comment must name the merged revision (full SHA) and cover:
    - CI and the review verdict;
    - the live checks: owner, offline, ADA staff and pupil, and accounts;
    - the archive name and the report status;
    - every decision applied.
24. Log tokens in a second comment that contains the word "tokens" and states the **source**.
    - **Transcript format:** engines that write a JSON Lines transcript, with per-call records carrying `message.id`, `message.usage` (integer token fields) and `timestamp`, can use `python3 scripts/release/tokens.py since --transcript <file> --state <state>/v<vv>/tokens-baseline.json`, or `tokens.py total --transcript <file> --after <start time>`. Reviewers' transcripts use `tokens.py total`.
    - **Other engines:** use their own per-call counter.
    - **No counter available:** write "token counts unavailable", and name the source used instead, such as `scripts/usage.py` account percentages, which are estimates.

    Then run `python3 scripts/usage.py end v<vv> --tokens <integer total>`. Omit `--tokens` when counts are unavailable.
25. Run `python3 scripts/release/finish.py complete`. The release is not complete until it passes (OPS-070); it checks:
    - HANDOFF.md and the report agree with release.json;
    - the register names the issue;
    - the issue has the evidence and token-log comments;
    - the SMTP record exists.

    Then close the issue with `gh issue close <issue>`.

**Corrections after the release.**
- A docs-only follow-up PR may change only files that no edition ships: `docs/` (including the register) and `CHANGELOG.md`.
- It needs its own review record and `land_build.py --pr <N> --review-record <file>`. land_build keeps the recorded release revision and notes the follow-up separately.
- Then rerun `finish.py complete` from the new main head.
- Expect Cloudflare to show the follow-up revision and ADA the release revision afterwards; their shipped content is identical. `finish.py check-published` then checks the follow-up's live report.
- Restarting a release under the same version after a rollback is a normal landing: land_build replaces the recorded revision whenever the change is not docs-only.
- `HANDOFF.md` changes alter the published report in every edition. A HANDOFF correction after release therefore goes on the issue as a comment and into the next release's block; it is not a separate redeploy.

## Usage limits
On a usage limit, stop. Write the exact resume point to `<state>/v<vv>/PROGRESS.md` (branch, worktree, last completed step number, next command), and do not schedule wakeups or timers. The owner restarts the work. The next agent resumes from PROGRESS.md and this runbook.
