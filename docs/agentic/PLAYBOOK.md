# Supplied playbook adaptation

Authority: owner-supplied copy of Davide’s Agentic DevOps Playbook, 2026-11-01, reference https://github.com/dlamagna/agentic-devops .
Source SHA256: `de956802126e7183caef29f99df5995cad9416f6607d36555923afe930895f59`. Original retained privately. No public redistribution license for the supplied text/templates was established, so these are Luisa-specific adaptations, not a claimed verbatim template installation.

| Playbook control | Luisa adaptation |
|---|---|
| Short lead/implementer/reviewer rules | docs/agentic/ rules and task brief template |
| Numbered requirements and explicit acceptance | canonical register, generated table, issue/PR templates |
| One issue/branch/PR, review then gate | docs/DEVOPS.md and scripts/land.py |
| Build/test/scan; no weakened tests | quality.yml and static tooling tests |
| Ready-set scheduling | roadmap dependencies; sequential default for this existing static app |
| Memory control | resource_guard.py serial heavy slot, capped future browser workers |
| Private state/handoff | LUISA_STATE_DIR, HANDOFF.md under 80 lines |
| Usage efficiency | focused reads, no forks, provider-independent usage log |
| Board/roadmap | current repo roadmap plus GitHub setup status; do not invent remote board completion |
| Permission refusals/privacy | AGENTS.md; no bypass, no credentials or owner files in Git |
| Restart watchdog | deliberately not installed; owner has not requested a resume schedule |
| Linux earlyoom/swap | not applicable to this Mac static workload; no machine changes |

A single lead may implement small local chores to avoid paying for unnecessary coordination. Independent review remains required for high-risk branches. Full Linux template self-tests and Claude CLI unattended permissions are not claimed as installed.
