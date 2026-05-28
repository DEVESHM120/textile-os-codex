# Agent Context

This repo is the combined hackathon MVP for an AI-powered Textile Workflow Automation Platform.

## Product Shape

The app helps textile mills and fashion brands move from fabric data to feasibility review and production label output in one flow.

Primary demo path:

1. Load or upload a cloth card.
2. Run deterministic feasibility checks.
3. Review PASS, WARNING, or ERROR gate with issue details.
4. Generate structured AI communication text.
5. Generate and download a sticker/technical-sheet Excel artifact.

Sticker Agent must support both single checked-fabric output and standalone bulk Excel + optional template generation. Bulk mode is critical because designers often already have an Excel master and a sticker template.

## Source Inspiration

- `DEVESHM120/Fabric-feasibility`: textile parser, feasibility rules, workflow concepts, approvals.
- `DEVESHM120/Sticker-Agent`: Excel label generation, K-code article logic, buyer conversion.

The old repos are source material. This repo is the combined MVP.

## Non-Negotiables

- Do not use AI to decide final feasibility gate.
- Do not commit real mill data, generated outputs, logs, SQLite DB files, or uploads.
- Preserve raw cloth-card visibility in review screens so users can audit parser/rule findings.
- Every meaningful change must update `docs/DECISIONS.md`, `docs/WORKLOG.md`, `.agent/tasks/task.md`, and `docs/VALIDATION_NOTES.md`.
