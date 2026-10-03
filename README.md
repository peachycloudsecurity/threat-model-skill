# threat-model-skill

A Claude Code skill that generates a standalone, code-driven, evidence-backed threat model
report (`report-<service-name>.md`) by reading a target's real source code.

Fixed four-section format: Overview, Trust Boundary Model (with mermaid diagram), Threats
(each with Risk / Mitigation / Validation and a cited proof snippet), and Architectural Risk.
Every claim is verified against actual source before the report is written.

## Install

Copy this directory into your skills folder:

```bash
cp -R threat-model-skill ~/.claude/skills/
```

## Usage

Ask Claude Code to "threat model this codebase/repo/service" or "create report-<name>.md".

## Contents

- `SKILL.md` — the skill definition and workflow
- `references/report-format.md` — annotated report skeleton
- `scripts/validate_report.py` — validates heading order, mermaid block, and per-threat evidence
