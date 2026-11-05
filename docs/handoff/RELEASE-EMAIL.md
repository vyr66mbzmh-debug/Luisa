# Mandatory release email (FR-024)

The owner has given standing authorisation: after every published Luisa release, email the final report to the configured owner recipient using the configured Luisa Reports sender. This survives agent, provider and chat changes. Only an explicit owner instruction to defer/suppress that report overrides it. Do not create hourly schedules or send interim emails by default.

## Private adapter, portable instructions

Read `WORKSPACE.json` under `LUISA_STATE_DIR` (on the original Mac, the private Luisa agent-state directory). Its `mailSender` identifies the existing SMTP script. Sender, recipient and credentials remain private, outside Git. The adapter uses authenticated SMTP and supports HTML plus plain text; it does not require Apple Mail or an unlocked desktop. Never log passwords, copy credentials into the repository, or rerun credential setup without need/authority.

Resolve the adapter path from private state, then run:

```sh
python3 "$mail_sender" --subject "Luisa v${release_version} report" \
  --body-file "$plain_report" --html-file "$html_report"
```

These variables mean the existing private adapter, the actual published version, and prepared private UTF-8 text/HTML files. Inspect the adapter's supported arguments first on a different machine. If private state or credentials are missing, ask for secure provisioning; do not switch sender or silently fall back to a draft. Preserve a precise pending-email handoff.

## Content and checks

- Include the full report in the email, plus links to the live release report and development progress.
- Name chapters as full textbook + chapter number + title, with live slides and booklet hyperlinks and output counts. Include only verified destinations; check the slide URL actually fetches lesson JSON rather than an HTML fallback.
- Use the same HTML progress table as the website: Slides uploaded, Slides checked, Booklet uploaded, Booklet checked. Every cell shows count/total and percentage. Green at 100%, amber for partial progress, red at zero; omit Slides sourced. Use inline styles for email compatibility.
- Order courses Pure 1, Pure 2, Mechanics 1, Mechanics 2, Statistics 1, Statistics 2, then Core Pure 1 and Core Pure 2 separately.
- State checked release/deployment results, outstanding work and limitations, honest available usage information, and legacy completed questions /3,423 (percentage) and sections /132 separately from expanded indexes. Never substitute automated extraction for final acceptance.

## Completion evidence and failures

Verify the release on required hosts before reporting it live. Check private send records for this version to avoid duplicate notifications. Record timestamp, version, recipient configuration reference, adapter exit status and SMTP outcome privately. Successful SMTP submission means the server accepted the message; it does not prove inbox receipt. Do not label a report delivered unless receipt is independently confirmed.

If sending fails, save both report files and the non-secret error, mark notification pending in HANDOFF/checkpoint and tell the owner. Publication can be successful while notification remains incomplete. Never silently omit this step or claim the report was sent. No historic catch-up emails are implied by a documentation-only task.
