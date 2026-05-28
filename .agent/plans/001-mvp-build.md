# 001 - Textile Workflow Platform MVP Build

Complexity: Medium
Status: Implemented initial MVP scaffold
Created: 2026-05-28

## Goal

Create a new React + Flask app that combines fabric feasibility checking, AI-assisted review, and sticker/label artifact generation into one hackathon-ready workflow.

## Build Decisions

- New repo path: `G:\codex x outskill\textile-workflow-platform`.
- Frontend: React with Vite.
- Backend: Flask API with SQLite persistence.
- Feasibility gate: deterministic rules only.
- AI assistant: OpenAI Responses API with JSON schema when configured; deterministic fallback otherwise.
- Artifacts: generated Excel files stored under `.runtime/artifacts`, ignored by git.

## Validation

- Backend unit and API tests.
- Frontend production build.
- Browser verification after dev servers are running.
- Docs freshness script to warn when source changes without planning doc updates.
