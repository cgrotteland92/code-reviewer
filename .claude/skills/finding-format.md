# Skill: Finding Format

Standard format and writing guidelines for expressing code review findings consistently across all four specialist agents. All findings are structured data submitted via the `report_findings` tool.

## Required Fields

```json
{
  "severity": "HIGH | MEDIUM | LOW",
  "title": "Short specific label",
  "description": "Detailed explanation of the issue",
  "location": "Where in the code this occurs"
}
```

---

## Field Guidelines

### `severity`

One of exactly three values: `HIGH`, `MEDIUM`, or `LOW`.

Apply the framework in [severity-rating.md](severity-rating.md). When in doubt between two levels, default to the lower one — overinflating severity erodes trust in the review.

---

### `title`

A short, specific label that uniquely identifies the finding. Aim for 5–12 words.

**Good titles — specific and actionable:**
- "SQL injection in `get_user()` via unparameterized query"
- "Mutable default argument `items=[]` shared across calls"
- "N+1 database query in `render_dashboard()` loop"
- "Missing null check before `.split()` on optional field"
- "Use `enumerate()` instead of `range(len(items))`"

**Bad titles — vague or generic:**
- "Security issue" (doesn't say what kind)
- "Bug in loop" (doesn't identify the function or mechanism)
- "Code quality problem" (not actionable)
- "Consider refactoring" (no specific target)
- "Improvement opportunity" (could be anything)

**Conventions:**
- Use backticks around function names, variable names, and code literals: `` `get_user()` ``, `` `items` ``
- Use present tense: "Missing null check" not "There is no null check"
- Name the function or class if known: "in `render_dashboard()`" not "in the dashboard code"

---

### `description`

The substantive body of the finding. 2–6 sentences. Must answer three questions:

1. **What is the issue?** Describe the specific code pattern or construct that is problematic.
2. **Why does it matter?** Explain the consequence: crash, data corruption, exploitability, maintainability harm.
3. **Under what conditions?** Describe when the problem manifests — always, under specific inputs, only concurrently, etc.

**Optionally include:**
- A code fix using the format in [code-fix-generation.md](code-fix-generation.md) (especially for the Improvements agent)
- The attack vector for security findings
- The triggering condition for bugs

**Good description (Security):**
> The `username` parameter is concatenated directly into the SQL query string on line 42: `f"SELECT * FROM users WHERE name = '{username}'"`. An attacker can supply `' OR '1'='1` as the username to return all users, or use a UNION-based payload to exfiltrate arbitrary table data. Use a parameterized query: `cursor.execute("SELECT * FROM users WHERE name = ?", (username,))`.

**Good description (Bug):**
> `process_items()` uses `items=[]` as a default argument. In Python, default argument values are evaluated once at function definition time — the same list object is reused across all calls that omit the argument. If one call mutates `items`, subsequent calls see those mutations. Use `items=None` and initialize `items = []` inside the function body.

**Good description (Quality):**
> `handle_request()` fetches user data from the database, validates permissions, transforms the response payload, and writes to the audit log — four distinct responsibilities in one 80-line function. This makes it impossible to test permission logic independently, and any change to one concern risks breaking the others. Extract into `fetch_user()`, `check_permissions()`, `build_response()`, and `audit_access()`.

**Good description (Improvements):**
> `allowed_roles` is defined as a list and checked with `in` on every request. List membership testing is O(n). Converting to a set makes lookups O(1) and makes intent clearer (sets model membership, not order). Move the definition to module level as a constant.

**Bad descriptions:**
- "This is a security vulnerability." (says nothing new beyond the title)
- "The code is hard to read and understand." (vague, no specific target)
- "You should add error handling here." (doesn't explain what kind or why)

---

### `location`

Where in the code the finding occurs. Be as specific as possible.

**Preferred formats (most to least specific):**

| Specificity | Example |
|---|---|
| Line number + function | `Line 42 in get_user()` |
| Function name | `get_user()` function |
| Method + class | `UserService.authenticate()` |
| Variable or expression | `username` parameter in `get_user()` |
| Block or section | `except` clause in `process_payment()` |
| File-level pattern | "All `SELECT` queries across the module" |

**When location is unknown:** Provide the best approximation you can from context. If the code lacks line numbers and function names aren't obvious, describe the pattern: "the `for` loop iterating over `results`".

**Never leave location empty if a function or variable name is identifiable from the code.**

---

## Summary Field

The `summary` field on `report_findings` is a 1–2 sentence overview of the entire analysis, not a list of findings.

**Good summary:**
> "The code contains two HIGH-severity injection vulnerabilities and several resource management issues. Overall security posture is weak for a public-facing endpoint."

> "No bugs detected. The code is defensive and handles edge cases consistently."

**Bad summary:**
- "I found some issues." (uninformative)
- A list of finding titles (that's what the findings array is for)

---

## Volume Guidelines

Report every genuine finding — don't filter by importance at the finding stage. The coordinator and the severity rating handle prioritization. However:

- Do not manufacture LOW findings to seem thorough if the code is genuinely clean
- Do not duplicate the same finding across multiple locations — consolidate into one finding with multiple locations
- Do not split one finding into multiple findings for the same root cause — one root cause = one finding with the full explanation
