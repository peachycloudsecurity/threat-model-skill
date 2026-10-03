# Report skeleton (annotated)

This is the exact section structure to reproduce for every `report-<service-name>.md`. Placeholder
text in `{curly braces}` describes what goes there — replace it with real content derived from the
inspected codebase. Do not add, remove, reorder, or reword sections.

The four heading strings below (`Overview`, `Trust Boundary Model`, `Threats`, `Architectural Risk`)
are fixed and must be reproduced exactly, every report, in this exact order and wording.

```markdown
# Threat Model: {Product/Service Name} {one-line descriptor of what it is}

## 1. Overview

{1-2 paragraphs: what the system is, who operates/uses it, and how data flows through it at a high
level. Then a bullet list of main components, one line each naming the component and its role.}

Main components:

- {Component}: {one-line role}
- {Component}: {one-line role}
- ...

{Closing sentence stating scope: what this model covers and what is explicitly out of scope.}

## 2. Trust Boundary Model

- The {component} trusts {actor/caller} for {purpose}. Enforcement: {exact mechanism named from
  code - class, dependency, middleware, shared secret, etc.}
- The {component} trusts {actor/caller} for {purpose}. Enforcement: {exact mechanism}.
- ...(one bullet per boundary; cover public/unauthenticated routes, authenticated-session trust,
  API-key/service auth, storage-layer trust, internal service-to-service trust, and any
  federated/delegated auth such as SSO/SAML/OAuth if present)

\`\`\`mermaid
graph LR
    Actor1(["👤 {Role}"])
    Actor2(["👤 {Role}"])

    subgraph boundaryA["── {Boundary A Name} ──"]
        NodeA["{Component}"]
    end

    subgraph boundaryB["── {Boundary B Name} ──"]
        NodeB["{Component}"]
    end

    subgraph storage["── Storage Boundary ──"]
        DB[("{Datastore}")]
    end

    Actor1 -.->|"{protocol/mechanism}"| NodeA
    NodeA -->|"{mechanism}"| NodeB
    NodeB -->|"{queries/writes}"| DB

    style boundaryA fill:#eef2ff,stroke:#5577cc,stroke-width:2px,stroke-dasharray:7 4
    style boundaryB fill:#f0fff4,stroke:#4a9970,stroke-width:2px,stroke-dasharray:7 4
    style storage   fill:#fff7ed,stroke:#b45309,stroke-width:2px,stroke-dasharray:7 4
\`\`\`

## 3. Threats

**{One-line scenario title naming the attack}{ (EE) if scoped to an optional/enterprise component}**
{One paragraph: the concrete mechanism - what the attacker does, which real endpoint/parameter/
config surface is involved, and the concrete consequence for confidentiality/integrity/availability.}
file: {path/to/file.ext:line}
```{lang}
{verbatim snippet, <=10 lines, copied from the file you actually opened this run - the proof the
threat is real, not a paraphrase or a guess}
```
- Risk: {Low|Medium|High} likelihood, {Low|Medium|High} impact
- Mitigation: {concrete, actionable fix naming the real component/control to change}
- Validation: {how to prove it - pentest steps, code-review target, config audit, or automated test}

**{Next scenario title}**
{paragraph}
file: {path:line}
```{lang}
{snippet}
```
- Risk: ...
- Mitigation: ...
- Validation: ...

(repeat for 3-6 scenarios total)

## 4. Architectural Risk

**{One-line fragility title}**
{One paragraph explaining the structural weakness: what enforces it today, what the blast radius is
if the single control fails, and why there is no compensating/secondary control. This is an
architectural concern, not a restatement of a Threat Scenario - it describes a systemic property of
the design, not one exploitable path.}

(repeat for 1-3 fragilities total)
```

## Notes on fidelity

- The mermaid diagram always uses `graph LR`, one `subgraph` per trust boundary, a distinct
  `fill`/`stroke` pair per subgraph with `stroke-dasharray:7 4`, and every cross-boundary edge
  labeled with the protocol/mechanism.
- Risk/Mitigation/Validation are exactly one bullet each, in that order, every time.
- Every threat carries a `file: path:line` citation and a verbatim fenced snippet as proof, placed
  right after the descriptive paragraph and before the Risk bullet. No snippet, no threat - drop or
  demote it to Architectural Risk instead of asserting it unproven.
- Do not add a findings table, severity summary table, or an executive summary section - this format
  is intentionally flat and does not use those constructs.
- Do not add a references/appendix section unless the target report explicitly asks for one.
