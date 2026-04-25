# Skill: Code Fix Generation

Reusable guidance for generating actionable fix suggestions within finding descriptions. Used primarily by the Improvements agent, and optionally by the Bugs and Security agents when a fix is unambiguous.

## When to Include a Fix

**Always include a fix suggestion when:**
- The Improvements agent identifies an idiomatic rewrite (the fix *is* the finding)
- The Bugs agent identifies a defect with a clear, unambiguous correct pattern
- The fix is 1–5 lines and the before/after is self-explanatory

**Omit a fix suggestion when:**
- The Security agent identifies a vulnerability requiring architectural decisions (e.g., "add an auth layer") — describe the attack vector instead
- The Quality agent identifies a structural problem requiring significant refactoring — describe the problem and the target state, not the code
- The fix depends on unknown business requirements or external context
- The change is large enough to warrant its own PR discussion

## Fix Format

Use a before/after code block within the `description` field. Keep it concise — the goal is to show the pattern, not rewrite the function.

### Standard Format

```
**Before:**
```python
# problematic code (just the relevant lines)
```

**After:**
```python
# corrected code
```
```

### Guidelines

**Be surgical.** Show only the lines that change, plus 1–2 lines of surrounding context for orientation. Do not paste the entire function.

**Use the file's actual language.** Match the exact syntax of the code under review — don't show Python fixes for JavaScript code.

**Preserve variable names.** Use the same variable names as the original code so the connection is obvious.

**Don't over-explain.** If the fix is self-evident from the before/after, a one-sentence explanation before the code is enough.

---

## Fix Examples by Category

### Idiomatic Rewrite (Improvements Agent)

**Finding:** "Use `enumerate()` instead of manual index tracking"

```
Using `range(len(...))` for index access is non-idiomatic and obscures intent.

**Before:**
```python
for i in range(len(items)):
    print(i, items[i])
```

**After:**
```python
for i, item in enumerate(items):
    print(i, item)
```
```

---

### Bug Fix (Bugs Agent)

**Finding:** "Mutable default argument causes state sharing between calls"

```
The default value `[]` is created once at function definition time and shared
across all calls that omit the argument. Callers that modify `items` will see
mutations in subsequent calls.

**Before:**
```python
def process(items=[]):
    items.append("done")
    return items
```

**After:**
```python
def process(items=None):
    if items is None:
        items = []
    items.append("done")
    return items
```
```

---

### Security Hardening (Security Agent — simple cases only)

**Finding:** "Use `secrets` module instead of `random` for token generation"

```
`random` is not cryptographically secure and its output is predictable given
knowledge of the seed. Use `secrets` for any value used in authentication,
session management, or access control.

**Before:**
```python
import random
token = str(random.randint(100000, 999999))
```

**After:**
```python
import secrets
token = secrets.token_hex(16)
```
```

---

### Performance Fix (Improvements Agent)

**Finding:** "Use a set for O(1) membership testing instead of list"

```
Checking membership in a list is O(n). If this check runs inside a loop,
the overall complexity is O(n²). Converting to a set makes each lookup O(1).

**Before:**
```python
allowed = ["admin", "editor", "viewer"]
if user.role in allowed:
    ...
```

**After:**
```python
ALLOWED_ROLES = {"admin", "editor", "viewer"}
if user.role in ALLOWED_ROLES:
    ...
```

Move the set definition outside the function if called repeatedly.
```

---

## What NOT to Do

- Do not generate fixes that change behavior beyond fixing the described issue
- Do not suggest fixes that depend on libraries not already in the codebase
- Do not show fixes for structural refactors that require understanding business logic
- Do not generate complete rewrites of functions — show the minimal change
- Do not add error handling that wasn't part of the fix (scope creep)
- Do not use type annotations in the fix if the original code has none (keep style consistent)
