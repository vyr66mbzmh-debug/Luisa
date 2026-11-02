# Usage and efficiency records
Use `python3 scripts/usage.py start TASK --provider codex --model MODEL` then `python3 scripts/usage.py end TASK --artifacts N --rework N`. Task IDs use letters/numbers/hyphens.
Records are append-only JSONL in private LUISA_STATE_DIR (default ~/.local/share/luisa-agent-state). Do not commit raw account IDs, resets, allowance snapshots or prompts. Optional `--remaining`, `--reset-at` and `--tokens` store genuine reported values; absent values stay null. Log a fresh start/end allowance through the provider tool if available, never stale values from chat.

Account remaining-% difference is an approximate shared-account observation, not exact task cost. A reset or window change invalidates the delta. Counters may be rounded; no invented 1dp precision, free-credit promises or cross-provider equivalence. Token totals only from provider-reported task metrics; elapsed time is measured independently.

Optimise verified outputs/check passes per task: short fresh handoffs, targeted reads, one heavy job, representative trial before bulk changes, cache evidence by artifact hash, no redundant re-renders, no large context forks. Model recommendations are choices for the owner/runtime, not claims of automatic switching. Escalate difficult maths/shared layout after two focused failed fixes; do not reduce final acceptance to save usage.
