import streamlit as st
from reviewer import review_code, ReviewResult, AgentReport, CoordinatorSummary

LANGUAGES = [
    "Auto-detect",
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C#",
    "C++",
    "Go",
    "Rust",
    "PHP",
    "Ruby",
    "SQL",
    "Shell / Bash",
    "Other",
]

SEVERITY_CONFIG = {
    "HIGH":   {"icon": "🔴", "color": "#c0392b"},
    "MEDIUM": {"icon": "🟡", "color": "#d68910"},
    "LOW":    {"icon": "🟢", "color": "#1e8449"},
}

HEALTH_CONFIG = {
    "CRITICAL":   {"icon": "🚨", "label": "CRITICAL",   "color": "#c0392b"},
    "NEEDS_WORK": {"icon": "⚠️", "label": "NEEDS WORK", "color": "#d68910"},
    "GOOD":       {"icon": "✅", "label": "GOOD",        "color": "#1e8449"},
    "EXCELLENT":  {"icon": "⭐", "label": "EXCELLENT",   "color": "#1a5276"},
}


def _tab_label(report: AgentReport) -> str:
    total = len(report.findings)
    high = sum(1 for f in report.findings if f.severity == "HIGH")
    if total == 0:
        return f"{report.emoji} {report.agent_name}"
    if high:
        return f"{report.emoji} {report.agent_name} ({total} · {high} HIGH)"
    return f"{report.emoji} {report.agent_name} ({total})"


def render_agent_tab(report: AgentReport) -> None:
    if report.summary:
        st.caption(report.summary)

    if not report.findings:
        st.success(f"No {report.agent_name.lower()} findings detected.")
        return

    for severity in ("HIGH", "MEDIUM", "LOW"):
        bucket = [f for f in report.findings if f.severity == severity]
        if not bucket:
            continue
        cfg = SEVERITY_CONFIG[severity]
        st.markdown(
            f"### {cfg['icon']} {severity} &nbsp; "
            f"<span style='color:{cfg['color']};font-weight:bold'>{len(bucket)} finding{'s' if len(bucket) != 1 else ''}</span>",
            unsafe_allow_html=True,
        )
        for finding in bucket:
            with st.expander(finding.title, expanded=(severity == "HIGH")):
                if finding.location:
                    st.caption(f"📍 {finding.location}")
                st.markdown(finding.description)
        st.write("")


def render_summary_tab(coordinator: CoordinatorSummary) -> None:
    health = HEALTH_CONFIG.get(coordinator.overall_health, HEALTH_CONFIG["NEEDS_WORK"])
    st.markdown(
        f"<h2 style='margin-top:0'>{health['icon']} Overall Health: "
        f"<span style='color:{health['color']}'>{health['label']}</span></h2>",
        unsafe_allow_html=True,
    )

    col_issues, col_strengths = st.columns(2)

    with col_issues:
        st.markdown("#### 🚨 Critical Issues")
        if coordinator.critical_issues:
            for issue in coordinator.critical_issues:
                st.markdown(f"- {issue}")
        else:
            st.success("No critical issues identified.")

    with col_strengths:
        st.markdown("#### ✅ Key Strengths")
        if coordinator.key_strengths:
            for strength in coordinator.key_strengths:
                st.markdown(f"- {strength}")
        else:
            st.info("No specific strengths noted.")

    if coordinator.recommended_actions:
        st.divider()
        st.markdown("#### 📋 Recommended Actions")
        actions = sorted(coordinator.recommended_actions, key=lambda x: x.get("priority", 99))
        for action in actions:
            st.markdown(f"**{action.get('priority', '·')}.** {action.get('action', '')}")

    if coordinator.narrative:
        st.divider()
        st.markdown("#### 📝 Analysis")
        st.markdown(coordinator.narrative)


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AI Code Reviewer")
st.caption(
    "Multi-agent analysis powered by Claude claude-sonnet-4-6 · "
    "Four specialist agents run in parallel, then a coordinator synthesizes results."
)

input_col, options_col = st.columns([4, 1])

with input_col:
    code_input = st.text_area(
        "Code",
        height=320,
        placeholder="Paste your code here…",
        label_visibility="collapsed",
    )

with options_col:
    language = st.selectbox("Language", LANGUAGES)
    st.write("")
    review_clicked = st.button("Review Code", type="primary", use_container_width=True)
    if st.button("Clear", use_container_width=True):
        st.session_state.pop("last_review", None)
        st.rerun()

if review_clicked:
    if not code_input.strip():
        st.warning("Please paste some code before clicking Review.")
    else:
        lang = "unspecified" if language == "Auto-detect" else language
        with st.spinner("Running 4 specialist agents in parallel — Security · Bugs · Quality · Improvements…"):
            try:
                result = review_code(code_input, lang)
                st.session_state["last_review"] = result
            except RuntimeError as e:
                st.error(str(e))

if "last_review" in st.session_state:
    result: ReviewResult = st.session_state["last_review"]

    st.divider()

    # Metrics bar
    all_findings = [f for r in result.reports for f in r.findings]
    high_n   = sum(1 for f in all_findings if f.severity == "HIGH")
    medium_n = sum(1 for f in all_findings if f.severity == "MEDIUM")
    low_n    = sum(1 for f in all_findings if f.severity == "LOW")
    health   = HEALTH_CONFIG.get(result.coordinator.overall_health, HEALTH_CONFIG["NEEDS_WORK"])

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Findings", len(all_findings))
    m2.metric("🔴 High",   high_n)
    m3.metric("🟡 Medium", medium_n)
    m4.metric("🟢 Low",    low_n)
    m5.metric("Health", f"{health['icon']} {health['label']}")

    st.divider()

    # Agent tabs + summary tab
    tab_labels = [_tab_label(r) for r in result.reports] + ["🎯 Summary"]
    tabs = st.tabs(tab_labels)

    for tab, report in zip(tabs[:4], result.reports):
        with tab:
            render_agent_tab(report)

    with tabs[4]:
        render_summary_tab(result.coordinator)
