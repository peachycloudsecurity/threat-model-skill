# Lab Workshop: Threat Modeling with a Claude Code Skill

A hands-on lab for running the `threat-model-skill` against a real open-source codebase on your
own machine. By the end you will understand what a Claude Code skill is, how to build one well,
how to install this one, and how to drive it to produce an evidence-backed threat model report.

Target for the demo: **[openreplay/openreplay](https://github.com/openreplay/openreplay)** — a
large, real-world session-replay and observability platform (multiple services, databases,
message queues, auth boundaries), which gives the skill plenty of genuine trust boundaries and
code paths to reason about.

---

## 1. What is a Claude Code skill?

A skill is a small, self-contained package of instructions that teaches Claude Code how to do one
specific job well, every time. It is loaded on demand: Claude reads the skill's `SKILL.md` only
when the task matches, so skills cost nothing until they are needed.

A skill is just a directory:

```
threat-model-skill/
├── SKILL.md                      # required: the instructions + frontmatter
├── references/                   # optional: longer reference material loaded as needed
│   └── report-format.md
└── scripts/                      # optional: helper scripts the skill can run
    └── validate_report.py
```

The only required file is `SKILL.md`. Its YAML frontmatter is what Claude matches against:

```yaml
---
name: threat-model-skill
description: Generates a standalone, code-driven, evidence-backed threat model report ...
             Use when asked to "threat model this codebase/repo/service" ...
metadata:
  version: 1.0.0
---
```

The `description` is the single most important field — it is how Claude decides *when* to reach
for the skill. Everything below the frontmatter is the workflow Claude follows once the skill
fires.

---

## 2. Best practices for writing skills

These are the principles this skill follows, and good defaults for any skill you build:

1. **Write a trigger-rich description.** Name the exact phrases a user would say ("threat model
   this repo", "create report-<name>.md"). Claude matches on this text — vague descriptions mean
   the skill never fires or fires at the wrong time.
2. **One skill, one job.** A skill should do a single thing deterministically. Don't bundle
   unrelated workflows; split them into separate skills.
3. **Make the output format explicit and fixed.** If the result should look the same every run,
   spell out the exact sections, order, and structure. This skill pins four headings in a fixed
   order so every report is comparable.
4. **Demand evidence, forbid guessing.** Instruct Claude to verify every claim against real
   source and cite it. "Open the file and copy the proving line" beats "describe the likely
   vulnerability." This is what separates a useful report from plausible-sounding fiction.
5. **Keep `SKILL.md` lean; push detail into `references/`.** Load heavy material (format
   skeletons, long checklists) only when needed, so the always-loaded part stays small.
6. **Ship a validator.** A `scripts/` check that enforces the contract (headings present, proof
   snippets attached) catches a half-followed skill before the user sees it.
7. **Version it.** Bump `metadata.version` on changes so you can tell which behavior produced a
   given report.
8. **No secrets, no internal data.** Skills get shared and cloned. Keep them generic — no
   credentials, no company-internal paths or names.

### Create your own skill in 60 seconds

```bash
mkdir -p ~/.claude/skills/my-skill
cat > ~/.claude/skills/my-skill/SKILL.md <<'EOF'
---
name: my-skill
description: One-line job summary. Use when the user asks to "<exact trigger phrase>".
metadata:
  version: 0.1.0
---

# My Skill

Step-by-step instructions Claude should follow when this skill fires.
EOF
```

Restart Claude Code and the skill is available. (Anthropic also ships a `skill-creator` skill that
scaffolds this for you — ask Claude to "create a new skill".)

---

## 3. Install the threat-model-skill

```bash
# One-step install straight into your Claude Code skills folder:
git clone https://github.com/peachycloudsecurity/threat-model-skill.git ~/.claude/skills/threat-model-skill
```

Or clone anywhere and copy it in:

```bash
git clone https://github.com/peachycloudsecurity/threat-model-skill.git
cp -R threat-model-skill ~/.claude/skills/
```

Verify the files landed:

```bash
ls ~/.claude/skills/threat-model-skill
# SKILL.md  references  scripts
```

**Restart Claude Code** (quit and relaunch, or start a new session) so it picks up the new skill.

---

## 4. Get the target code

The skill reads *real source*, so clone the target locally first:

```bash
cd ~/Desktop   # or wherever you keep lab work
git clone https://github.com/openreplay/openreplay.git
```

---

## 5. Run the skill

Start Claude Code in a working directory (where you want the report written), then ask:

```
Threat model the codebase at ~/Desktop/openreplay and write report-openreplay.md
```

Claude will match the `threat-model-skill`, then:

1. Map components, entry points, and high-risk operations from the real tree.
2. Derive trust boundaries from actual auth/middleware/config code.
3. Draw a mermaid trust-boundary diagram.
4. Enumerate 3–6 threats, each with a verbatim proof snippet and file citation.
5. Identify architectural risks.
6. Validate the report with the bundled script.

### Validate the output yourself

```bash
python3 ~/.claude/skills/threat-model-skill/scripts/validate_report.py report-openreplay.md
```

A clean run means every section is present and every threat is backed by cited code.

---

## 6. Talking points for the demo

- Show `SKILL.md` first — point out the `description` is what made Claude pick the skill.
- After the report is generated, open one Threat entry and show the proof snippet traces to a
  real line in the openreplay source. That's the "evidence over assumption" principle paying off.
- Re-run with "extend report-openreplay.md with a threat about <component>" to show skills treat
  the report as a living artifact rather than regenerating from scratch.
- Run the validator live to show the contract is machine-enforced, not just convention.

---

## Troubleshooting

- **Skill doesn't fire.** Restart Claude Code; confirm `~/.claude/skills/threat-model-skill/SKILL.md`
  exists. Rephrase the ask to match the description ("threat model this repo").
- **Report reads generic.** The verification step was skipped — ask Claude to open the real files
  and attach proof snippets, or drop unproven threats.
- **Validator flags a missing proof block or diagram.** Both are mandatory; have Claude add them.
