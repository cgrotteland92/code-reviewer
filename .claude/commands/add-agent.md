# Add Agent

Scaffold a new specialist agent for the code reviewer.

## Usage

```
/project:add-agent <name> <focus-description>
```

**Arguments:**
- `name` — the agent's short name (e.g., `performance`, `accessibility`, `docs`)
- `focus-description` — 1–2 sentences describing what this agent reviews

## What This Does

Creates all the pieces needed to add a new specialist agent to the multi-agent review pipeline:
1. A new agent markdown file in `.claude/agents/<name>.md`
2. Updates `reviewer.py` to add the agent to the parallel execution pool
3. Updates `app.py` to show the new agent's tab in the UI
4. Updates `CLAUDE.md` to document the new agent

## Steps

1. Read `CLAUDE.md` to understand the project structure
2. Read `.claude/agents/security.md` as a reference template for agent markdown files
3. Read `reviewer.py` to understand the agent function pattern (`_run_security`, `_run_bugs`, etc.)
4. Read `app.py` to understand the tab layout

5. **Create** `.claude/agents/<name>.md` with:
   - Role section describing the agent's purpose and boundaries
   - Focus Areas section listing what the agent specifically looks for
   - Severity Criteria section with domain-specific HIGH/MEDIUM/LOW examples
   - Output Format section
   - Domain Boundaries table (in scope / out of scope)

6. **Edit** `reviewer.py`:
   - Add a `_<NAME>_PROMPT` constant with the agent's system prompt
   - Add a `_run_<name>()` function following the pattern of `_run_security()`
   - Add the new function to the `futures` list in `review_code()`

7. **Edit** `app.py`:
   - Update `_tab_label()` and `render_agent_tab()` if any agent-specific UI logic is needed
   - Verify the tab count in `st.tabs(tab_labels)` picks up the new agent automatically

8. Summarize what was created and what to test

## Constraints

- The new agent must use `_FINDINGS_TOOL` (the shared tool schema) — do not create a new tool schema unless the output format genuinely differs
- The agent's domain must not overlap with existing agents (Security, Bugs, Quality, Improvements) — define clear boundaries in the Domain Boundaries table
- The system prompt must include explicit instructions for what NOT to report (the domain boundaries)
- Do not modify the coordinator agent — it already synthesizes all agents generically
