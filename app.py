import streamlit as st
from reviewer import review_code

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

SECTION_HEADERS = [
    "🐛 Bugs & Potential Errors",
    "🔒 Security Vulnerabilities",
    "📋 Code Quality Issues",
    "💡 Suggested Improvements",
]

TAB_LABELS = ["🐛 Bugs", "🔒 Security", "📋 Quality", "💡 Improvements"]


def parse_review(raw: str) -> dict[str, str]:
    sections = {h: [] for h in SECTION_HEADERS}
    current = None
    for line in raw.splitlines():
        matched = False
        for header in SECTION_HEADERS:
            if header in line:
                current = header
                matched = True
                break
        if not matched and current is not None:
            sections[current].append(line)
    return {h: "\n".join(lines).strip() for h, lines in sections.items()}


st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AI Code Reviewer")
st.caption("Powered by Claude claude-sonnet-4-6 · Paste code below and click **Review**")

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
        with st.spinner("Analyzing your code…"):
            try:
                result = review_code(code_input, lang)
                st.session_state["last_review"] = result
            except RuntimeError as e:
                st.error(str(e))

if "last_review" in st.session_state:
    st.divider()
    st.subheader("Review Results")

    parsed = parse_review(st.session_state["last_review"])
    tabs = st.tabs(TAB_LABELS)

    for tab, header in zip(tabs, SECTION_HEADERS):
        with tab:
            content = parsed.get(header, "")
            if content:
                st.markdown(content)
            else:
                st.info("No issues found in this category.")
