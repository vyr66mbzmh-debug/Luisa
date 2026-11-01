# Start Luisa work in a new chat

Setup checkpoint: until the foundation PR is merged, use branch `chore/agentic-devops-foundation` (commit 68e5166). Its build/test/scan and Cloudflare preview passed; main does not yet contain these files. Check HANDOFF.md on that branch for remaining owner unlock/sign-in actions.

Give the agent access to this GitHub repository:
https://github.com/vyr66mbzmh-debug/Luisa

Paste this (replace the last line with the work you want):

> Work on Luisa: https://github.com/vyr66mbzmh-debug/Luisa . Check out chore/agentic-devops-foundation if these files are not yet on main. Read AGENTS.md, HANDOFF.md and docs/agentic/LEAD-RULES.md first. Inspect the current branch/worktrees and preserve unfinished work. Use the authoritative requirements in docs/requirements/register.json; read only IDs relevant to this task. Track provider/model usage honestly with scripts/usage.py. Follow the issue/branch/check/review/release process in docs/DEVOPS.md. Automatic publication is authorised after checks; verify actual live links. Update HANDOFF.md and the requirements evidence before finishing. My task is: [describe the next bounded job].

For ChatGPT/Codex: choose a local task with the existing website folder or connect the GitHub repo. For Claude/other coding agents: open/clone the same repo; CLAUDE.md points to shared rules. A chat with no filesystem or GitHub write tools can plan/review, but cannot perform deployment.

For lesson/booklet work, the agent also needs the relevant original deck, textbook/solution pages and private authoring tools from the owner's _LUISA materials folder. A cloud clone includes published outputs and development docs, not those private originals. Grant only the files required for the assigned chapter. No need to paste this long conversation.

Useful links:
- Handoff: https://github.com/vyr66mbzmh-debug/Luisa/blob/chore/agentic-devops-foundation/HANDOFF.md
- Requirements: https://github.com/vyr66mbzmh-debug/Luisa/blob/chore/agentic-devops-foundation/docs/requirements/REQUIREMENTS.md
- Rules: https://github.com/vyr66mbzmh-debug/Luisa/blob/chore/agentic-devops-foundation/AGENTS.md
- Live website: https://fmq-6d9.pages.dev/
- Progress: https://fmq-6d9.pages.dev/development-progress

To pause: say “Pause after saving a handoff.” To resume: start a new task with the prompt above. No automatic resume schedule is installed. Credentials are never pasted into the handoff or stored in Git.
