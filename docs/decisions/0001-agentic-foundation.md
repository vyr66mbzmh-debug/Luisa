# ADR 0001 — Portable static delivery and agent handoff
Date: 2026-11-01. Owner approved: supplied Davide playbook; rename GitHub only; future publication automatic after checks.

Keep existing static app and public Cloudflare address. Rename existing repo without recreating it or losing history. Retain _LUISA as local master; update remote/integration references. Do not copy the 2GB private materials tree into the public repository.

Adapt the supplied playbook rather than claiming unprovided template scripts were installed verbatim. Use issues, bounded branch/PRs, build/test/scan gates, proportional review, private operational state and concise handoffs. Single-agent sequential foundation work is efficient here; role separation applies if delegation is authorised. No Linux earlyoom, swap changes, watchdog/cron, paid services or automatic reset redemption are needed or authorised by adopting a document.

Agent-independent files are AGENTS.md, HANDOFF.md and the numbered canonical register. CLAUDE.md is a pointer. Requirements summaries are generated. Old statuses are imported as historical assertions pending current evidence. Later owner requirements supersede historic ?/tick/title-background/MARS/version rules.

No LLM/API key is required to build or serve the static site. Human review is not required for every future release once agreed gates and risk review pass; existing security-sensitive access changes remain owner actions. Full authoring reproducibility is a future issue because generated content and private original materials are a separate layer.
