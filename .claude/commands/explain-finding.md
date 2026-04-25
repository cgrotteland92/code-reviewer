# Explain Finding

Get a deep-dive explanation of a specific finding type, including how to detect it, why it matters, and how to fix it.

## Usage

```
/project:explain-finding <finding-type>
```

**Arguments:**
- `finding-type` — the name of a vulnerability, bug pattern, or quality issue (e.g., `sql-injection`, `mutable-default-argument`, `n+1-query`, `god-class`)

## What This Does

Provides an educational explanation of a specific finding type that the review agents may report. Useful when:
- A developer receives a finding and wants to understand it deeply before fixing it
- You're onboarding a new team member to common code issues
- You want concrete examples to use in code review discussions

## Steps

1. Identify which agent domain the finding-type belongs to:
   - Security: `.claude/agents/security.md`
   - Bugs: `.claude/agents/bugs.md`
   - Quality: `.claude/agents/quality.md`
   - Improvements: `.claude/agents/improvements.md`

2. Read the relevant agent file to locate the finding-type in the focus areas

3. Read `.claude/skills/language-rules.md` for language-specific context

4. Read `.claude/skills/code-fix-generation.md` for fix format guidelines

5. Produce a structured explanation with these sections:

## Output Format

```
# [Finding Type Name]

**Domain:** Security / Bugs / Quality / Improvements
**Typical Severity:** HIGH / MEDIUM / LOW (with brief justification)

## What It Is
[2–3 sentences: definition and what makes it a problem]

## Why It Matters
[2–3 sentences: real-world consequences, impact on users or codebase]

## How to Detect It
[Patterns to look for — code signatures, grep patterns, tool flags]

## Examples

### Vulnerable / Problematic Code
```[language]
[example showing the issue]
```

### Fixed Code
```[language]
[corrected version]
```

## Language-Specific Notes
[Any nuances in Python / JavaScript / Go / etc. that affect this finding]

## Further Reading
[1–3 reference links or concepts to explore (only well-known, stable references)]
```
