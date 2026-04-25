import os
import concurrent.futures
from dataclasses import dataclass, field
from dotenv import load_dotenv
import anthropic

load_dotenv()

MODEL = "claude-sonnet-4-6"

_api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=_api_key) if _api_key else None


@dataclass
class Finding:
    severity: str  # HIGH | MEDIUM | LOW
    title: str
    description: str
    location: str = ""


@dataclass
class AgentReport:
    agent_name: str
    emoji: str
    findings: list[Finding] = field(default_factory=list)
    summary: str = ""


@dataclass
class CoordinatorSummary:
    overall_health: str  # CRITICAL | NEEDS_WORK | GOOD | EXCELLENT
    critical_issues: list[str] = field(default_factory=list)
    key_strengths: list[str] = field(default_factory=list)
    recommended_actions: list[dict] = field(default_factory=list)
    narrative: str = ""


@dataclass
class ReviewResult:
    reports: list[AgentReport]
    coordinator: CoordinatorSummary


# ---------------------------------------------------------------------------
# Tool schemas — each specialist agent uses the shared findings schema;
# the coordinator uses its own summary schema.
# ---------------------------------------------------------------------------

_FINDINGS_TOOL: dict = {
    "name": "report_findings",
    "description": "Report all findings from your code analysis.",
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "description": "All findings discovered. Empty array if none found.",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "enum": ["HIGH", "MEDIUM", "LOW"],
                            "description": "Severity of the finding.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Short, specific title for the finding.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed explanation: what it is, why it matters, how it manifests.",
                        },
                        "location": {
                            "type": "string",
                            "description": "Line number(s), function name, or code construct where the issue occurs.",
                        },
                    },
                    "required": ["severity", "title", "description"],
                    "additionalProperties": False,
                },
            },
            "summary": {
                "type": "string",
                "description": "One or two sentence overview of the analysis.",
            },
        },
        "required": ["findings", "summary"],
        "additionalProperties": False,
    },
}

_COORDINATOR_TOOL: dict = {
    "name": "report_summary",
    "description": "Report the synthesized executive summary of all agent findings.",
    "input_schema": {
        "type": "object",
        "properties": {
            "overall_health": {
                "type": "string",
                "enum": ["CRITICAL", "NEEDS_WORK", "GOOD", "EXCELLENT"],
                "description": "Overall code health rating.",
            },
            "critical_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Must-fix issues across all categories, prioritized.",
            },
            "key_strengths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "What the code does well.",
            },
            "recommended_actions": {
                "type": "array",
                "description": "Prioritized recommended actions (priority 1 = most urgent).",
                "items": {
                    "type": "object",
                    "properties": {
                        "priority": {
                            "type": "integer",
                            "description": "Priority rank, 1 being most urgent.",
                        },
                        "action": {
                            "type": "string",
                            "description": "Specific, actionable recommendation.",
                        },
                    },
                    "required": ["priority", "action"],
                    "additionalProperties": False,
                },
            },
            "narrative": {
                "type": "string",
                "description": "2–3 paragraph narrative synthesis readable by engineers and stakeholders.",
            },
        },
        "required": ["overall_health", "critical_issues", "recommended_actions", "narrative"],
        "additionalProperties": False,
    },
}


# ---------------------------------------------------------------------------
# System prompts — one per agent, cached by Anthropic on first use.
# ---------------------------------------------------------------------------

_SECURITY_PROMPT = """You are a specialized security code auditor with deep expertise in identifying vulnerabilities across all major programming languages and frameworks.

Your sole focus is security. Analyze the submitted code exclusively for security vulnerabilities.

## YOUR DOMAIN

Look carefully for:
- SQL injection via string concatenation or interpolation in queries
- Command injection via unsanitized input passed to shell commands or subprocesses
- Path traversal when constructing file paths from user input
- Cross-site scripting (XSS) in rendered user-supplied content
- Hardcoded credentials, API keys, secrets, or tokens in source code
- Insecure deserialization (pickle.loads on untrusted data, eval on user input)
- Improper input validation or missing sanitization at trust boundaries
- Sensitive data exposure in logs, error messages, or stack traces
- Missing or insufficient authentication and authorization checks
- Weak or broken cryptographic algorithms (MD5/SHA1 for security, DES, ECB mode)
- Insecure random number generation where cryptographic randomness is required
- Timing attacks due to non-constant-time comparisons of secrets
- SSRF when URLs are constructed from user input
- Unrestricted file uploads without type or size validation
- XML External Entity (XXE) injection in XML parsers
- Prototype pollution in JavaScript/TypeScript
- Missing CSRF protection in web forms
- Overly permissive CORS configuration
- Use of assert for security-critical checks (disabled in optimized mode)

## SEVERITY GUIDANCE

- HIGH: Directly exploitable in common attack scenarios; enables data breach, RCE, or auth bypass
- MEDIUM: Exploitable under specific conditions; meaningfully degrades security posture
- LOW: Defense-in-depth issue; increases attack surface but unlikely directly exploitable alone

## LANGUAGE HANDLING

Apply language-specific security pitfalls. If language is unspecified, infer from syntax.

## OUTPUT

Call report_findings with all security vulnerabilities discovered. Be specific: reference exact lines, variable names, or patterns. Explain the attack vector and potential impact, not just the vulnerability class name."""

_BUGS_PROMPT = """You are a specialized bug hunter and defect analyst with deep expertise in identifying correctness issues, runtime errors, and logic flaws across all major programming languages.

Your sole focus is bugs, defects, and potential runtime errors. Do not report security issues or code quality concerns — only correctness problems.

## YOUR DOMAIN

Look carefully for:
- Off-by-one errors in loops or array/list indexing
- Null, None, or undefined dereferences without proper guards
- Unchecked return values from functions that can fail
- Incorrect type assumptions (treating string as number, etc.)
- Integer overflow or underflow in arithmetic operations
- Race conditions or shared-state issues in concurrent/async code
- Unhandled exceptions, missing try/except or try/catch blocks
- Missing or incorrect loop termination conditions (infinite loops)
- Resource leaks: unclosed files, database connections, sockets, or handles
- Incorrect mutable default arguments (common Python pitfall)
- Logic errors in conditional branches (wrong operator, inverted condition)
- Shallow copies when deep copies are required
- Incorrect string formatting or encoding assumptions
- Silent failures from overly broad exception handling (bare except:)
- Use of deprecated or removed APIs
- Incorrect async/await usage (missing await, blocking in async context)
- Concurrency issues: missing locks, deadlocks, double-checked locking

## SEVERITY GUIDANCE

- HIGH: Will cause crashes, data corruption, or incorrect behavior in common usage scenarios
- MEDIUM: Causes errors or wrong behavior under specific but realistic conditions
- LOW: Potential edge-case bug that may not manifest in typical usage

## LANGUAGE HANDLING

Apply language-specific bug patterns. If language is unspecified, infer from syntax.

## OUTPUT

Call report_findings with all bugs and defects discovered. Reference exact lines or constructs. Explain why it is a bug and under what conditions it manifests."""

_QUALITY_PROMPT = """You are a specialized code quality and maintainability expert who reviews code for design, structure, and clarity issues across all major programming languages.

Your sole focus is code quality and maintainability. Do not report security vulnerabilities or runtime bugs — only structural and clarity issues.

## YOUR DOMAIN

Look carefully for:
- Functions or methods that do too many things (violating single responsibility)
- Poor naming: ambiguous variables, non-descriptive functions, Hungarian notation
- Duplicated logic that should be extracted into shared functions or utilities
- Excessive nesting depth making code hard to follow (3–4+ levels is a warning sign)
- Magic numbers and unexplained constants that should be named
- Missing or misleading comments, docstrings, or type annotations
- Dead code: unused imports, unused variables, commented-out blocks
- Overly complex conditionals that can be simplified
- Long parameter lists suggesting a missing abstraction (data class, config object)
- Inconsistent coding style or formatting within the same file
- Returning multiple types from the same function without clear intent
- Global mutable state that makes code hard to test and reason about
- Classes that exist only to wrap a single function (unnecessary abstraction)
- Missing separation of concerns (mixing IO, business logic, and presentation)
- Hard-to-test code due to tight coupling or lack of dependency injection
- Overly long functions (generally >50 lines is a signal)

## SEVERITY GUIDANCE

- HIGH: Structural issues that actively harm maintainability; will cause team velocity problems
- MEDIUM: Quality issues that meaningfully impede understanding or modification
- LOW: Style or convention issues; nice to fix but don't block progress

## LANGUAGE HANDLING

Apply language-specific idioms, conventions, and best practices. If language is unspecified, infer from syntax.

## OUTPUT

Call report_findings with all quality issues discovered. Reference specific constructs. Explain why it matters for maintainability, not just what it is."""

_IMPROVEMENTS_PROMPT = """You are a specialized code optimization and improvement advisor who identifies opportunities to make code faster, more idiomatic, more readable, and more robust across all major programming languages.

Your sole focus is improvement opportunities. Do not report bugs, security vulnerabilities, or clear defects — only constructive suggestions to elevate good code to excellent code.

## YOUR DOMAIN

Look for opportunities to:
- Improve performance: eliminate redundant computation, use efficient data structures/algorithms
- Use idiomatic language features (list comprehensions, optional chaining, generators, etc.)
- Apply modern language features that simplify code (pattern matching, walrus operator, etc.)
- Improve error handling: more specific exception types, meaningful messages, proper propagation
- Increase testability: decouple dependencies, extract pure functions, add clear interfaces
- Reduce complexity: flatten nested conditionals with early returns or guard clauses
- Apply design patterns where they genuinely simplify the design
- Add meaningful logging or observability that would help debugging in production
- Improve documentation for non-obvious business logic or external constraints
- Handle edge cases and boundary conditions not currently addressed
- Use standard library functions instead of manual re-implementations
- Improve memory efficiency with generators or lazy evaluation
- Better utilize the type system for safety and self-documentation

## SEVERITY GUIDANCE

- HIGH: Significant performance, reliability, or developer-experience gain with high ROI
- MEDIUM: Meaningful improvement that enhances maintainability or efficiency
- LOW: Nice-to-have refinement; small but worthwhile when time allows

## LANGUAGE HANDLING

Apply language-specific idioms and modern features. If language is unspecified, infer from syntax.

## OUTPUT

Call report_findings with all improvement opportunities. Be specific and constructive — show what to improve and why, not just flag a gap."""

_COORDINATOR_PROMPT = """You are a senior engineering lead who synthesizes reports from four specialized code review agents into a cohesive, actionable executive summary.

You will receive structured findings from four agents:
1. Security Agent — vulnerabilities and security risks
2. Bugs Agent — defects and runtime errors
3. Quality Agent — code quality and maintainability issues
4. Improvements Agent — optimization and enhancement opportunities

## YOUR TASK

Produce a structured executive summary containing:
- Overall code health: CRITICAL (production-blocking), NEEDS_WORK (significant issues), GOOD (solid with room to improve), EXCELLENT (production-ready, well-crafted)
- Critical issues requiring immediate action, across all categories
- Key strengths worth acknowledging
- Prioritized recommended actions (priority 1 = most urgent)
- A narrative synthesis of 2–3 paragraphs, readable by technical leads and stakeholders

## SYNTHESIS GUIDELINES

- Identify cross-cutting patterns (e.g., a quality issue + security issue sharing a root cause)
- Prioritize by impact: a LOW security finding may outweigh a HIGH style finding
- Be constructive and specific — general advice is unhelpful
- Acknowledge good code when agents find little to critique
- Don't repeat every finding verbatim — synthesize and prioritize

## OUTPUT

Call report_summary with your structured synthesis."""


# ---------------------------------------------------------------------------
# Core execution
# ---------------------------------------------------------------------------

def _extract_tool_result(response: anthropic.types.Message, tool_name: str) -> dict:
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input
    return {}


def _call_agent(system_prompt: str, user_msg: str, tool: dict) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": user_msg}],
    )
    return _extract_tool_result(response, tool["name"])


def _make_findings(raw: dict) -> list[Finding]:
    return [
        Finding(
            severity=f.get("severity", "LOW"),
            title=f.get("title", ""),
            description=f.get("description", ""),
            location=f.get("location", ""),
        )
        for f in raw.get("findings", [])
    ]


def _run_security(code: str, language: str) -> AgentReport:
    raw = _call_agent(_SECURITY_PROMPT, f"Language: {language}\n\n```\n{code}\n```", _FINDINGS_TOOL)
    return AgentReport("Security", "🔒", _make_findings(raw), raw.get("summary", ""))


def _run_bugs(code: str, language: str) -> AgentReport:
    raw = _call_agent(_BUGS_PROMPT, f"Language: {language}\n\n```\n{code}\n```", _FINDINGS_TOOL)
    return AgentReport("Bugs", "🐛", _make_findings(raw), raw.get("summary", ""))


def _run_quality(code: str, language: str) -> AgentReport:
    raw = _call_agent(_QUALITY_PROMPT, f"Language: {language}\n\n```\n{code}\n```", _FINDINGS_TOOL)
    return AgentReport("Quality", "📋", _make_findings(raw), raw.get("summary", ""))


def _run_improvements(code: str, language: str) -> AgentReport:
    raw = _call_agent(_IMPROVEMENTS_PROMPT, f"Language: {language}\n\n```\n{code}\n```", _FINDINGS_TOOL)
    return AgentReport("Improvements", "💡", _make_findings(raw), raw.get("summary", ""))


def _format_reports_for_coordinator(reports: list[AgentReport]) -> str:
    lines: list[str] = []
    for r in reports:
        lines.append(f"## {r.emoji} {r.agent_name} Agent")
        lines.append(f"Summary: {r.summary}")
        if r.findings:
            for f in r.findings:
                loc = f" (at: {f.location})" if f.location else ""
                lines.append(f"- [{f.severity}] {f.title}{loc}: {f.description}")
        else:
            lines.append("- No findings.")
        lines.append("")
    return "\n".join(lines)


def _run_coordinator(reports: list[AgentReport], language: str) -> CoordinatorSummary:
    report_text = _format_reports_for_coordinator(reports)
    raw = _call_agent(
        _COORDINATOR_PROMPT,
        f"Language: {language}\n\nAgent Reports:\n\n{report_text}",
        _COORDINATOR_TOOL,
    )
    return CoordinatorSummary(
        overall_health=raw.get("overall_health", "NEEDS_WORK"),
        critical_issues=raw.get("critical_issues", []),
        key_strengths=raw.get("key_strengths", []),
        recommended_actions=raw.get("recommended_actions", []),
        narrative=raw.get("narrative", ""),
    )


def review_code(code: str, language: str) -> ReviewResult:
    if client is None:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Please add it to your .env file.")

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(_run_security, code, language),
                executor.submit(_run_bugs, code, language),
                executor.submit(_run_quality, code, language),
                executor.submit(_run_improvements, code, language),
            ]
            reports = [f.result() for f in futures]

        coordinator = _run_coordinator(reports, language)

    except anthropic.AuthenticationError:
        raise RuntimeError("Invalid API key. Please check your ANTHROPIC_API_KEY in .env.")
    except anthropic.RateLimitError:
        raise RuntimeError("Rate limit reached. Please wait a moment and try again.")
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"API error ({e.status_code}): {e.message}")

    return ReviewResult(reports=reports, coordinator=coordinator)
