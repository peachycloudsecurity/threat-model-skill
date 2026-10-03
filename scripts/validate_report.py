#!/usr/bin/env python3
"""Validate a threat-model report against the fixed report-<service>.md structure.

This skill uses one fixed heading set, every report, in this exact order:
Overview / Trust Boundary Model / Threats / Architectural Risk.

Usage: python3 validate_report.py <path-to-report.md>
Exits non-zero with a list of problems if the structure doesn't match.
"""
import re
import sys

REQUIRED_HEADINGS = [
    r"^## 1\. Overview$",
    r"^## 2\. Trust Boundary Model$",
    r"^## 3\. Threats$",
    r"^## 4\. Architectural Risk$",
]


def fail(problems):
    print("FAIL - report does not match the required format:")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_report.py <path-to-report.md>")
        sys.exit(2)

    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    problems = []

    if not re.match(r"^# Threat Model: .+", lines[0] if lines else ""):
        problems.append("Title (line 1) must start with '# Threat Model: '")

    for pattern in REQUIRED_HEADINGS:
        if not re.search(pattern, text, re.MULTILINE):
            problems.append(f"Missing required heading: {pattern}")

    heading_positions = [m.start() for p in REQUIRED_HEADINGS for m in re.finditer(p, text, re.MULTILINE)]
    if heading_positions != sorted(heading_positions):
        problems.append("Required headings are present but out of order")

    if "```mermaid" not in text or "graph LR" not in text:
        problems.append("Missing mandatory mermaid 'graph LR' trust boundary diagram")

    boundaries_section = _section(text, "## 2. Trust Boundary Model", "## 3. Threats")
    if boundaries_section and "Enforcement:" not in boundaries_section:
        problems.append(
            "Trust Boundary Model bullets should each name an 'Enforcement:' mechanism"
        )

    threats_section = _section(text, "## 3. Threats", "## 4. Architectural Risk")
    if threats_section:
        titles = re.findall(r"^\*\*(.+?)\*\*$", threats_section, re.MULTILINE)
        if not titles:
            problems.append("No bold threat titles found under Threats")
        chunks = re.split(r"^\*\*.+?\*\*$", threats_section, flags=re.MULTILINE)[1:]
        for i, chunk in enumerate(chunks, start=1):
            title = titles[i - 1] if i - 1 < len(titles) else f"#{i}"
            for field in ("- Risk:", "- Mitigation:", "- Validation:"):
                if field not in chunk:
                    problems.append(f"Threat '{title}' is missing '{field}' bullet")
            if "file:" not in chunk:
                problems.append(f"Threat '{title}' is missing a 'file: path:line' citation")
            if "```" not in chunk:
                problems.append(f"Threat '{title}' is missing a fenced proof snippet")

    risk_section = _section(text, "## 4. Architectural Risk", None)
    if risk_section and not re.search(r"^\*\*(.+?)\*\*$", risk_section, re.MULTILINE):
        problems.append("No bold titles found under Architectural Risk")

    if problems:
        fail(problems)

    print("PASS - report structure matches the required format.")


def _section(text, start_heading, end_heading):
    start_idx = text.find(start_heading)
    if start_idx == -1:
        return None
    start_idx += len(start_heading)
    if end_heading:
        end_idx = text.find(end_heading, start_idx)
        if end_idx == -1:
            end_idx = len(text)
    else:
        end_idx = len(text)
    return text[start_idx:end_idx]


if __name__ == "__main__":
    main()
