# Skill: Severity Rating

Reusable guidance for assigning HIGH / MEDIUM / LOW severity to code review findings. Apply this framework consistently across all four specialist agents.

## The Core Question

Before assigning a severity, ask: **"What is the realistic worst-case outcome if this finding is ignored in production?"**

- Immediate, likely harm to users or data → **HIGH**
- Harm under specific but plausible conditions → **MEDIUM**
- Theoretical or minor inconvenience → **LOW**

## Severity Definitions

### HIGH

Reserved for findings that must be fixed before the code ships. A HIGH finding means:
- Exploitation or failure is possible in **common usage scenarios** (not edge cases)
- The impact is severe: data breach, crash, data corruption, or complete feature failure
- A developer reviewing a PR would block the merge on this finding alone

**Decision test for HIGH:** If this code went to production today with 1,000 users, would at least one encounter this problem within a week? If yes → HIGH.

**Examples by domain:**

| Domain | HIGH Example |
|---|---|
| Security | SQL injection on a login form (exploitable immediately) |
| Security | Hardcoded API key or password in source code |
| Bugs | `NullPointerException` on every POST request with a missing optional field |
| Bugs | File handle never closed, leaking one handle per request |
| Quality | 300-line function with 7 nesting levels making safe modification impossible |
| Improvements | N+1 DB query in a loop called on every page load (100+ queries per request) |

---

### MEDIUM

For findings that cause real problems but require specific conditions to trigger. A MEDIUM finding means:
- The issue affects a realistic subset of users or usage patterns (not just edge cases)
- Impact is meaningful: feature degradation, misleading output, security posture reduction
- A developer would flag this in code review with "should fix before release"

**Decision test for MEDIUM:** Could a user who actively uses this feature encounter this problem within a month? If yes → MEDIUM.

**Examples by domain:**

| Domain | MEDIUM Example |
|---|---|
| Security | CSRF missing on a low-privilege action (exploitable with social engineering) |
| Security | Weak password hashing algorithm (bcrypt → MD5) for non-critical accounts |
| Bugs | Off-by-one that skips the last item only when pagination hits an exact page boundary |
| Bugs | Race condition that causes duplicate processing under concurrent load |
| Quality | Duplicated validation logic in 4 places (one copy will get updated, others won't) |
| Improvements | Missing `lru_cache` on a pure function called 500 times per request |

---

### LOW

For findings that are worth fixing but don't affect production reliability or security posture. A LOW finding means:
- The issue is theoretical, cosmetic, or only manifests in rare edge cases
- Impact is minor: developer inconvenience, slightly worse performance, reduced future safety
- A developer would note this in review as "fix when you're in this area"

**Decision test for LOW:** Is this an improvement in principle, but no realistic user would notice if it weren't fixed? If yes → LOW.

**Examples by domain:**

| Domain | LOW Example |
|---|---|
| Security | Missing `HttpOnly` flag on a non-sensitive cookie |
| Security | `random` used for a non-security display token |
| Bugs | Mutable default argument that only matters when callers omit the argument |
| Bugs | Integer overflow only with inputs >2 billion |
| Quality | Unused import that doesn't affect runtime |
| Improvements | `for i in range(len(x))` → `enumerate(x)` (idiomatic but not impactful) |

---

## Common Pitfalls to Avoid

**Inflating to HIGH:**
- "This could be a problem if..." → If the conditions are rare or require malicious intent from an authenticated admin, it's not HIGH
- Theoretical vulnerabilities with no realistic attack path → MEDIUM or LOW
- Code smell without behavioral consequence → never HIGH

**Deflating to LOW:**
- Any SQL injection is at least MEDIUM; if on a public endpoint, it's HIGH
- Any hardcoded credential is HIGH regardless of what the credential accesses
- Any crash on a common code path is HIGH regardless of the domain

**Scope creep:**
- Security agent should not label a bug as HIGH just because the bug could theoretically be exploited
- Quality agent should not label a missing docstring as HIGH
- Each agent rates within its own domain

## Multi-Agent Severity Interaction

When the coordinator synthesizes findings, severity from different agents is not additive — a HIGH quality finding and a HIGH bug finding do not make something "critical" individually. However, a pattern of MEDIUM findings across all four agents pointing to the same root cause can collectively warrant CRITICAL health rating.
