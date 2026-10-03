---
name: threat-model-skill
description: Generates a standalone, code-driven, evidence-backed threat model report with a fixed four-section format (Overview, Trust Boundary Model with mermaid diagram, Threats with Risk/Mitigation/Validation and a cited proof snippet, Architectural Risk) in the report-<service-name>.md format. Every claim is verified against real source before the report is written. Use when asked to "threat model this codebase/repo/service", "write a threat model report", or "create report-<name>.md".
metadata:
  version: 1.0.0
---

# Threat Model Report Generator

Produces a single markdown file, `report-<service-name>.md`, that threat-models a real codebase by
reading its actual source. The output format is fixed and must be matched exactly every time: same
four section headings, same order, same mermaid diagram style, same per-scenario bullet structure.
This is a self-contained report meant for someone with no other context — one document, evidence
attached inline, nothing to track across other files. Only the security *content* changes per
target; never invent a new heading, drop a section, or reorder them. Treat the report as a living
artifact: re-run this skill to extend an existing one with new findings rather than starting over.

## When to use

- Threat modeling a repo/service/codebase from real source code (a local path or cloned repo).
- A report matching the `report-<service-name>.md` format is requested specifically.

## Required inputs

- A path to the actual source code of the target system. This format is built by reading real code —
  routers, auth dependencies, schema, docker-compose/helm charts, background workers, integration
  modules — not by guessing architecture from a README alone. If only a design doc is available with
  no code, say so and ask whether a lighter, doc-only pass is acceptable.
- The target's service/product name, used for the title and the output filename.

## Workflow

1. **Map components, entry points, and high-risk operations — narrowly.** Read the directory
   structure, entrypoints, `docker-compose`/helm charts, README, main API routers, database
   schemas/migrations, background workers/schedulers, and third-party integration modules. Name the
   actual entry points (HTTP routes, RPC handlers, CLI commands, scheduled jobs) and high-risk
   operations (deserialization, templating, parsing untrusted input, native bindings) you find, not a
   generic checklist swept over the whole tree. If the target has a CHANGELOG, security advisories, or
   past CVEs, skim them first — prior fixed bug classes are the strongest signal for what's still
   plausible here. Note which components are optional/enterprise-only (tag these `(EE)` or equivalent
   in prose, matching how the codebase itself distinguishes them).
2. **Set scope.** Decide and state explicitly, in one closing sentence of the Overview, what this
   model covers and what it deliberately excludes (e.g. a separate ingestion pipeline, a mobile
   client). Do not silently omit major components — call out the exclusion.
3. **Derive trust boundaries from code, not assumption.** For each boundary, identify: what is
   trusted, from whom/what, and the exact enforcement mechanism as it exists in code — name the real
   class, dependency, decorator, or middleware (e.g. `JWTAuth`, `ProjectAuthorizer`, a specific env
   var used as a shared secret). Include boundaries for: unauthenticated/public routes, authenticated
   user sessions, API-key/service-to-service auth, storage layer trust (does the DB itself enforce
   anything, or is it all application-layer?), any internal service-to-service calls, and any
   federated/delegated auth (SSO, SAML, OAuth) if present.
4. **Draw the trust boundary diagram.** A mermaid `graph LR` is mandatory — see **Mermaid diagram
   conventions** below and `references/report-format.md` for the exact style (subgraph per boundary,
   distinct fill/stroke per boundary, dashed borders, labeled edges).
5. **Enumerate threats, each with proof.** 3–6 threats, each grounded in an actual code path found in
   step 1–3. Before writing a threat, open the actual file and confirm the vulnerable line still
   exists as described — verify against the live source rather than relying on memory or an
   assumption about a framework's default behaviour. Copy the exact snippet (verbatim, not
   paraphrased) that proves the issue, with its file path. If you cannot find a real line that proves
   it, the threat is speculative — drop it or reduce it to an Architectural Risk instead. Format each
   threat exactly as described in **Output format**.
6. **Identify architectural fragilities.** 1–3 systemic/structural weaknesses — not point bugs. A
   fragility is a design property whose blast radius or lack of a compensating control makes it
   architecturally significant even if no single line of code is "wrong". Explain why it is
   structural, not just cite an example.
7. **Validate before presenting.** Run `scripts/validate_report.py <path-to-report>` to check the
   exact heading text/order, presence of the mermaid block, and that every Threat entry has all three
   of Risk/Mitigation/Validation plus a fenced proof snippet. Fix anything it flags before showing the
   report to the user — a flag means a claim isn't backed by cited code, not that the wording is off.

## Output format (exact — match section-for-section)

See `references/report-format.md` for the full annotated skeleton with placeholder text explaining
what belongs in each slot. Section headings and order, in this order, are fixed:

1. `# Threat Model: {Product/Service Name} — {one-line descriptor}`
2. `## 1. Overview` — 1–2 paragraphs: what the system is, its main components as a bullet list, then
   a closing sentence stating scope/exclusions.
3. `## 2. Trust Boundary Model` — a bullet list, one bullet per boundary, each in the form: *"The
   \<component\> trusts \<X\> for \<purpose\>. Enforcement: \<exact mechanism from code\>."* Followed
   by the mandatory mermaid `graph LR` trust-boundary diagram.
4. `## 3. Threats` — one subsection per scenario:
   - Bold one-line title naming the attack (append `(EE)`/equivalent tag if scoped to an
     optional/enterprise component).
   - One paragraph describing the concrete mechanism: the attacker-victim model (remote
     unauthenticated / remote authenticated low-privilege / cross-tenant), what that attacker does,
     which real endpoint/parameter/config surface is involved, and the concrete consequence.
   - A fenced code block, immediately after the paragraph, holding the verbatim snippet (≤10 lines)
     that proves the issue, headed by a one-line `file: path/to/file.ext:line` citation. This is the
     evidence the claim rests on — copied from a file actually opened this run.
   - `- Risk: <Low|Medium|High> likelihood, <Low|Medium|High> impact`
   - `- Mitigation: <concrete, actionable fix naming the real component/control to change>`
   - `- Validation: <how to prove it — pentest steps, code-review target, config audit, or automated
     test, phrased as an instruction>`
5. `## 4. Architectural Risk` — one subsection per fragility: bold one-line title, then a paragraph
   explaining the structural weakness and why it's architecturally significant (blast radius, absence
   of a compensating/secondary control), not just restating a Threat entry.

## Heading set (fixed, always use these exact four)

`Overview` / `Trust Boundary Model` / `Threats` / `Architectural Risk`, in this exact order, every
report this skill produces. Do not substitute synonyms and do not vary the wording per report.

## Mermaid diagram conventions

- `graph LR`; one `subgraph` per trust boundary (em-dash-free label, e.g. `public["── Public
  Boundary ──"]`), distinct `fill`/`stroke` + dashed `stroke-dasharray` per boundary, every
  cross-boundary edge labeled with its protocol/mechanism (`"JWT bearer"`, `"API key header"`).

## Style rules

- Plain, precise English; normal hyphens, no em dashes.
- Fact over assumption: every claim in Trust Boundary Model and Threats must trace to a line
  personally read this run — name real files/classes/config keys, backed by evidence rather than a
  generic boilerplate claim.
- Risk/Mitigation/Validation are each exactly one bullet; the proof snippet is the only block-level
  addition allowed inside a Threat entry.
- Keep the report tight — a standalone document read once. No findings table, tracking ids, or
  resolution-tracking table; the four fixed sections are the whole document.

## Output location

Write to `report-<service-name-kebab-case>.md` in the current working directory unless the user
specifies otherwise. Confirm the filename with the user before writing if it's ambiguous which
directory they want it in.

## Troubleshooting

**Report reads generic, or a snippet can't be found.** Step 5's verification was skipped and the
threat was written from assumption. Go back, open the real file, and either find the proving line or
drop the threat.

**Validator flags a missing proof block or mermaid diagram.** Both are mandatory, not optional — add
per **Output format** / **Mermaid diagram conventions**.
