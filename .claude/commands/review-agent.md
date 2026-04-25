# Review Agent

Run a focused review using a single specialist agent against the current file or a code snippet.

## Usage

```
/project:review-agent <agent> [language]
```

**Arguments:**
- `agent` — one of: `security`, `bugs`, `quality`, `improvements`
- `language` — optional; inferred from file extension if omitted

## What This Does

Applies one of the four specialist agents from `.claude/agents/<agent>.md` to the code in the current open file. This is useful when:
- You want faster feedback focused on one dimension (e.g., security only before a deploy)
- You already have findings from other agents and want to dig into one area
- You're iterating on a fix and want to re-check only that domain

## Steps

1. Read `.claude/agents/$ARGUMENTS.md` to load the agent's focus areas, severity criteria, and output format
2. Read `.claude/skills/severity-rating.md` and `.claude/skills/finding-format.md` for output standards
3. Read `.claude/skills/language-rules.md` and apply the section for the detected or specified language
4. Analyze the code in the active editor file using only the loaded agent's domain
5. Output findings using the finding format from `finding-format.md`, grouped by severity (HIGH → MEDIUM → LOW)
6. End with a one-paragraph summary of the analysis

## Output Format

```
## 🔒 Security Agent (or 🐛 Bugs / 📋 Quality / 💡 Improvements)
**Language detected:** Python

### 🔴 HIGH
**[title]** — `location`
[description]

### 🟡 MEDIUM
...

### 🟢 LOW
...

---
**Summary:** [1–2 sentences]
```

If no findings in a category, omit that section. If no findings at all, say so clearly.
