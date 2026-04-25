# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# AI Code Reviewer

A Streamlit application that uses a multi-agent Claude pipeline to review code across four specialist dimensions: security, bugs, quality, and improvements. Four specialist agents run in parallel, and a coordinator agent synthesizes their findings into an executive summary.

## Tech Stack

| Component   | Technology                              |
| ----------- | --------------------------------------- |
| UI          | Streamlit                               |
| AI          | Anthropic Claude (`claude-sonnet-4-6`)  |
| SDK         | `anthropic` Python SDK                  |
| Config      | `python-dotenv` (`.env` file)           |
| Parallelism | `concurrent.futures.ThreadPoolExecutor` |

## Project Structure

```
ai-code-reviewer/
├── app.py              # Streamlit UI — renders tabs, metrics, findings
├── reviewer.py         # Agent logic — prompts, tools, parallel execution
├── requirements.txt
├── .env                # ANTHROPIC_API_KEY (not committed)
├── .env.example
├── CLAUDE.md           # This file
└── .claude/
    ├── agents/         # Agent documentation (purpose, focus, severity)
    │   ├── security.md
    │   ├── bugs.md
    │   ├── quality.md
    │   ├── improvements.md
    │   └── coordinator.md
    ├── skills/         # Reusable capability documentation
    │   ├── severity-rating.md
    │   ├── code-fix-generation.md
    │   ├── language-rules.md
    │   └── finding-format.md
    └── commands/       # Custom slash commands
        ├── review-agent.md
        ├── add-agent.md
        └── explain-finding.md
```

## Architecture

### Agent Pipeline

```
User submits code
       │
       ├─── 🔒 Security Agent ────┐
       ├─── 🐛 Bugs Agent ────────┤  (parallel, ThreadPoolExecutor)
       ├─── 📋 Quality Agent ─────┤
       └─── 💡 Improvements Agent ┘
                                   │
                           🎯 Coordinator Agent
                                   │
                           ReviewResult returned to UI
```

### Key Data Types (`reviewer.py`)

```python
Finding          # severity, title, description, location
AgentReport      # agent_name, emoji, findings: list[Finding], summary
CoordinatorSummary  # overall_health, critical_issues, key_strengths,
                    # recommended_actions, narrative
ReviewResult     # reports: list[AgentReport], coordinator: CoordinatorSummary
```

### Tool Use Pattern

Each specialist agent uses forced tool use (`tool_choice: {type: "tool", name: "report_findings"}`) with a shared JSON schema. This guarantees structured output without text parsing. The coordinator uses a separate `report_summary` tool with a richer schema.

### Prompt Caching

Each agent's system prompt is marked `cache_control: {type: "ephemeral"}`. After the first call, Anthropic caches the prompt server-side for 5 minutes. Subsequent reviews with the same prompt (same agent, same model) pay only the cache-read cost (~10% of normal input cost).

## Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-...

# Run the app
streamlit run app.py
```

## Common Development Tasks

### Adding a new specialist agent

Use the `/project:add-agent` command, or do it manually:

1. Create `.claude/agents/<name>.md` describing the agent's domain, focus areas, severity criteria, and output format
2. Add a `_<NAME>_PROMPT` system prompt constant in `reviewer.py`
3. Add a `_run_<name>(code, language)` function that calls `_call_agent()` with `_FINDINGS_TOOL`
4. Add `executor.submit(_run_<name>, code, language)` to the futures list in `review_code()`
5. The UI auto-adapts to any number of reports — no changes to `app.py` needed

### Modifying an agent's behavior

Edit the corresponding `_<NAME>_PROMPT` constant in `reviewer.py`. The system prompt is the agent's complete instruction set. Reference `.claude/agents/<name>.md` for the intended behavior — keep them in sync.

### Changing the output schema

Edit `_FINDINGS_TOOL` or `_COORDINATOR_TOOL` in `reviewer.py`, then update the corresponding dataclass (`Finding`, `AgentReport`, or `CoordinatorSummary`) and the rendering code in `app.py`.

### Running a focused single-agent review

Use the `/project:review-agent` slash command in Claude Code:

```
/project:review-agent security Python
/project:review-agent bugs
```

### Understanding a specific finding type

Use the `/project:explain-finding` slash command:

```
/project:explain-finding sql-injection
/project:explain-finding mutable-default-argument
/project:explain-finding n+1-query
```

## .claude/ Structure Reference

### agents/

One file per specialist agent. Each file documents:

- **Role** — what the agent is responsible for and what it should NOT report
- **Focus Areas** — the specific patterns and constructs it checks
- **Severity Criteria** — domain-specific HIGH/MEDIUM/LOW examples
- **Output Format** — field requirements and what to exclude
- **Domain Boundaries** — in-scope vs out-of-scope table

Read these files to understand agent behavior before modifying prompts in `reviewer.py`.

### skills/

Reusable capability documentation referenced by agent files:

| File                     | Purpose                                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------- |
| `severity-rating.md`     | Framework for assigning HIGH/MEDIUM/LOW with decision tests and examples                           |
| `code-fix-generation.md` | Format and guidelines for before/after code fix suggestions                                        |
| `language-rules.md`      | Language-specific pitfalls, idioms, and best practices (Python, JS, TS, Java, Go, Rust, SQL, Bash) |
| `finding-format.md`      | Standard format for `severity`, `title`, `description`, `location` fields                          |

### commands/

Custom slash commands available in Claude Code sessions within this project:

| Command                                   | Purpose                                               |
| ----------------------------------------- | ----------------------------------------------------- |
| `/project:review-agent <agent> [lang]`    | Run a single specialist agent on the current file     |
| `/project:add-agent <name> <description>` | Scaffold a new specialist agent end-to-end            |
| `/project:explain-finding <type>`         | Deep-dive explanation of a finding type with examples |

## Design Decisions

**Why tool use for structured output?**
Forcing structured JSON via `tool_choice` eliminates brittle text parsing. The finding schema is the contract between agents and UI — changing it in one place propagates correctly.

**Why parallel agents instead of one large prompt?**
Each agent has a focused system prompt cached separately. This produces sharper, more domain-specific findings versus a single prompt juggling all four concerns. Parallel execution means the wall-clock time is bounded by the slowest agent, not the sum of all agents.

**Why a coordinator agent instead of UI aggregation?**
The coordinator performs semantic synthesis — identifying cross-cutting root causes, weighing findings from different domains against each other, and producing a coherent narrative. This can't be done with simple UI-level aggregation of bullet points.

**Why `claude-sonnet-4-6`?**
Balance of cost and capability for this use case. Each review makes 5 API calls (4 agents + coordinator). Using Sonnet keeps costs reasonable while maintaining strong code analysis quality.
