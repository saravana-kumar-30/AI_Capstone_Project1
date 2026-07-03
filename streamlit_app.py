import streamlit as st
import requests
import json
import anthropic
from config import Config
from schemas import ApplicantProfileData, LoanApplicationData

st.set_page_config(
    page_title="Loan Approval AI System",
    page_icon="🏦",
    layout="wide",
)

API_BASE_URL = f"http://{Config.FASTAPI_HOST}:{Config.FASTAPI_PORT}/api"

_claude = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY) if Config.ANTHROPIC_API_KEY else None

SYSTEM_PROMPT = """You are a loan application intake assistant. Extract structured loan application fields from a user's natural-language message.

Return ONLY a JSON object (no markdown, no explanation):
{
  "applicant_id": "<string, generate 'APP-<4 digits>' if not given>",
  "age": <integer 18-100>,
  "income": <float annual income in USD>,
  "employment_type": "<Full-time|Self-employed|Part-time|Retired>",
  "location": "<city or state>",
  "credit_score": <integer 300-850>,
  "loan_amount": <float in USD>,
  "loan_tenure_months": <integer months>,
  "existing_liabilities": <float annual existing debt payments in USD, default 0>,
  "missing_fields": ["<field name>", ...]
}

If any field is absent, include it in "missing_fields" with a null value. Do not invent values."""


# ── Shared helpers ────────────────────────────────────────────────────────────

def _submit_application(fields: dict) -> dict:
    profile = ApplicantProfileData(
        applicant_id=fields["applicant_id"],
        age=int(fields["age"]),
        income=float(fields["income"]),
        employment_type=fields["employment_type"],
        location=fields["location"],
    )
    application = LoanApplicationData(
        applicant_id=fields["applicant_id"],
        credit_score=int(fields["credit_score"]),
        loan_amount=float(fields["loan_amount"]),
        loan_tenure_months=int(fields["loan_tenure_months"]),
        existing_liabilities=float(fields.get("existing_liabilities") or 0),
        applicant_profile=profile,
    )
    response = requests.post(
        f"{API_BASE_URL}/submit-loan-application",
        json=application.model_dump(mode="json"),
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def _extract_fields(user_message: str) -> dict | None:
    if _claude is None:
        return None
    try:
        response = _claude.messages.create(
            model=Config.MODEL_NAME,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)
    except Exception:
        return None


def _render_result_card(result: dict, key_suffix: str = ""):
    decision = result["decision"]
    color = {"Approve": "green", "Reject": "red", "Review": "orange"}.get(decision, "gray")
    icon  = {"Approve": "🟢",   "Reject": "🔴",  "Review": "🟡"}.get(decision, "❓")

    st.markdown(
        f"""
        <div style="border:2px solid {color}; border-radius:10px; padding:16px; margin-top:12px;">
          <h3 style="color:{color}; margin:0 0 8px 0">{icon} Decision: {decision}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Risk Score",  f"{result['risk_score']:.1f} / 100")
    m2.metric("Confidence",  f"{result['confidence_level']:.0%}")
    m3.metric("Case ID",     result["case_id"])

    st.markdown("**Key Decision Factors:**")
    for f in result.get("key_factors", []):
        st.markdown(f"&nbsp;&nbsp;• {f}")

    st.markdown("**Explanation:**")
    st.info(result.get("explanation", ""))

    unique_key = f"dl_{result['case_id']}_{key_suffix}"
    st.download_button(
        "⬇ Download JSON",
        data=json.dumps(result, indent=2, default=str),
        file_name=f"loan_{result['application_id']}.json",
        mime="application/json",
        use_container_width=True,
        key=unique_key,
    )


def _chat_format_result(result: dict) -> str:
    icon = {"Approve": "🟢", "Reject": "🔴", "Review": "🟡"}.get(result["decision"], "❓")
    factors = "\n".join(f"  • {f}" for f in result.get("key_factors", []))
    return (
        f"**{icon} Decision: {result['decision']}**\n\n"
        f"**Risk Score:** {result['risk_score']:.1f}/100  |  "
        f"**Confidence:** {result['confidence_level']:.0%}  |  "
        f"**Case ID:** {result['case_id']}\n\n"
        f"**Key Factors:**\n{factors}\n\n"
        f"**Explanation:** {result.get('explanation', '')}"
    )


# ── Session state ─────────────────────────────────────────────────────────────

for key, default in [
    ("messages", []),
    ("pending_fields", None),
    ("form_result", None),
    ("results_history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Page header ───────────────────────────────────────────────────────────────

st.markdown(
    """
    <h1 style="margin-bottom:0">🏦 Intelligent Loan Approval System</h1>
    <p style="color:gray; margin-top:4px">Multi-Agent AI-Powered Loan Application Analysis</p>
    <hr style="margin:12px 0 20px 0">
    """,
    unsafe_allow_html=True,
)


# ── Main two-column layout ────────────────────────────────────────────────────

form_col, divider_col, chat_col = st.columns([5, 0.1, 3], gap="small")


# ════════════════════════════════════════════════════
# LEFT — Structured application form
# ════════════════════════════════════════════════════

with form_col:
    st.markdown("### 📋 Loan Application Form")
    st.caption("Fill in all fields below and click **Submit Application** to get an instant AI decision.")

    # ── Section 1: Applicant Information ──────────────
    st.markdown(
        "<div style='background:#f0f4ff; border-left:4px solid #4a6cf7; "
        "padding:8px 14px; border-radius:4px; margin:12px 0 8px 0'>"
        "<strong>Step 1 — Applicant Information</strong></div>",
        unsafe_allow_html=True,
    )

    ai_c1, ai_c2 = st.columns(2)
    with ai_c1:
        applicant_id = st.text_input(
            "Applicant ID",
            placeholder="e.g. APP001",
            help="Unique identifier for this applicant",
        )
        age = st.number_input(
            "Age",
            min_value=18, max_value=100, value=35, step=1,
            help="Applicant's age in years",
        )
    with ai_c2:
        employment_type = st.selectbox(
            "Employment Type",
            ["Full-time", "Self-employed", "Part-time", "Retired"],
            help="Current employment status",
        )
        location = st.text_input(
            "Location",
            placeholder="e.g. New York",
            help="City or state of residence",
        )

    income = st.number_input(
        "Annual Income ($)",
        min_value=1_000, max_value=10_000_000, value=85_000, step=1_000,
        help="Total gross annual income in USD",
    )

    # ── Section 2: Loan Details ────────────────────────
    st.markdown(
        "<div style='background:#f0f4ff; border-left:4px solid #4a6cf7; "
        "padding:8px 14px; border-radius:4px; margin:20px 0 8px 0'>"
        "<strong>Step 2 — Loan Details</strong></div>",
        unsafe_allow_html=True,
    )

    ld_c1, ld_c2 = st.columns(2)
    with ld_c1:
        credit_score = st.number_input(
            "Credit Score",
            min_value=300, max_value=850, value=700, step=1,
            help="FICO credit score (300–850)",
        )
        loan_amount = st.number_input(
            "Loan Amount ($)",
            min_value=1_000, max_value=int(Config.MAX_LOAN_AMOUNT), value=50_000, step=1_000,
            help=f"Requested loan amount (max ${Config.MAX_LOAN_AMOUNT:,.0f})",
        )
    with ld_c2:
        loan_tenure_months = st.number_input(
            "Loan Tenure (Months)",
            min_value=6, max_value=360, value=60, step=6,
            help="Repayment period in months (e.g. 60 = 5 years)",
        )
        existing_liabilities = st.number_input(
            "Existing Annual Liabilities ($)",
            min_value=0, max_value=10_000_000, value=0, step=500,
            help="Total existing annual debt obligations in USD",
        )

    # ── Section 3: Review summary ──────────────────────
    st.markdown(
        "<div style='background:#f0f4ff; border-left:4px solid #4a6cf7; "
        "padding:8px 14px; border-radius:4px; margin:20px 0 8px 0'>"
        "<strong>Step 3 — Review &amp; Submit</strong></div>",
        unsafe_allow_html=True,
    )

    with st.expander("Review your application before submitting", expanded=False):
        s1, s2 = st.columns(2)
        s1.markdown(f"**Applicant ID:** {applicant_id or '—'}")
        s1.markdown(f"**Age:** {age}")
        s1.markdown(f"**Annual Income:** ${income:,.0f}")
        s1.markdown(f"**Employment:** {employment_type}")
        s1.markdown(f"**Location:** {location or '—'}")
        s2.markdown(f"**Credit Score:** {credit_score}")
        s2.markdown(f"**Loan Amount:** ${loan_amount:,.0f}")
        s2.markdown(f"**Tenure:** {loan_tenure_months} months")
        s2.markdown(f"**Existing Liabilities:** ${existing_liabilities:,.0f}")

    # ── Submit button ──────────────────────────────────
    st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)
    submit_clicked = st.button(
        "🚀 Submit Application",
        use_container_width=True,
        type="primary",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if submit_clicked:
        errors = []
        if not applicant_id.strip():
            errors.append("Applicant ID is required.")
        if not location.strip():
            errors.append("Location is required.")
        if income <= 0:
            errors.append("Annual income must be greater than 0.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            with st.spinner("Processing your application through the AI pipeline…"):
                try:
                    result = _submit_application({
                        "applicant_id": applicant_id.strip(),
                        "age": age,
                        "income": income,
                        "employment_type": employment_type,
                        "location": location.strip(),
                        "credit_score": credit_score,
                        "loan_amount": loan_amount,
                        "loan_tenure_months": loan_tenure_months,
                        "existing_liabilities": existing_liabilities,
                    })
                    st.session_state.form_result = result
                    st.session_state.results_history.append(result)
                    st.success("Application processed successfully!")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not reach the loan API. Make sure all services are running.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ API error: {e.response.text}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {e}")

    # ── Result card (shown below submit button) ────────
    if st.session_state.form_result:
        st.markdown("---")
        st.markdown("### 📊 Decision Result")
        _render_result_card(st.session_state.form_result, key_suffix="form")
        if st.button("🔄 New Application", use_container_width=True):
            st.session_state.form_result = None
            st.rerun()


# ════════════════════════════════════════════════════
# THIN DIVIDER
# ════════════════════════════════════════════════════

with divider_col:
    st.markdown(
        "<div style='border-left:1px solid #e0e0e0; min-height:700px; margin:0 auto'></div>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════
# RIGHT — Chatbot alternative
# ════════════════════════════════════════════════════

with chat_col:
    st.markdown("### 💬 AI Chat Assistant")
    st.caption("Alternatively, describe your application in plain language and let AI fill in the details.")

    # Scrollable message history
    chat_box = st.container(height=520, border=True)
    with chat_box:
        if not st.session_state.messages:
            welcome = (
                "Hello! I'm your AI loan advisor.\n\n"
                "Describe your application in natural language, for example:\n\n"
                "> *\"I'm 34, earn \\$90k/year full-time in Chicago, "
                "credit score 740, want to borrow \\$120k over 5 years.\"*\n\n"
                "I'll extract the details and process it instantly."
            )
            st.session_state.messages.append({"role": "assistant", "content": welcome})

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input pinned below the box
    user_input = st.chat_input("Describe your loan application…")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Analysing…"):
            # Merge with pending fields if a follow-up
            if st.session_state.pending_fields:
                supplement = _extract_fields(user_input)
                if supplement:
                    for k, v in supplement.items():
                        if k != "missing_fields" and v is not None:
                            st.session_state.pending_fields[k] = v
                    still_missing = [
                        f for f in st.session_state.pending_fields.get("missing_fields", [])
                        if st.session_state.pending_fields.get(f) is None
                    ]
                    st.session_state.pending_fields["missing_fields"] = still_missing
                fields = st.session_state.pending_fields
            else:
                fields = _extract_fields(user_input)

            if fields is None:
                reply = (
                    "Sorry, I couldn't parse that. Please include your income, "
                    "credit score, loan amount, and employment type."
                )
            elif fields.get("missing_fields"):
                st.session_state.pending_fields = fields
                reply = (
                    "I need a bit more information. Could you provide: "
                    f"**{', '.join(fields['missing_fields'])}**?"
                )
            else:
                st.session_state.pending_fields = None
                try:
                    result = _submit_application(fields)
                    st.session_state.results_history.append(result)
                    reply = _chat_format_result(result)
                except requests.exceptions.ConnectionError:
                    reply = "❌ Could not reach the loan API. Please make sure all services are running."
                except Exception as e:
                    reply = f"❌ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🗑 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_fields = None
        st.rerun()


# ════════════════════════════════════════════════════
# BOTTOM — History & FAQ tabs
# ════════════════════════════════════════════════════

st.markdown("---")
tab_history, tab_faq = st.tabs(["📊 Results History", "📋 FAQ"])

with tab_history:
    history = st.session_state.results_history
    if not history:
        st.info("No applications processed yet in this session.")
    else:
        for i, result in enumerate(reversed(history)):
            decision = result["decision"]
            icon = {"Approve": "🟢", "Reject": "🔴", "Review": "🟡"}.get(decision, "❓")
            with st.expander(
                f"{icon} {result['application_id']} — **{decision}**  |  "
                f"Risk {result['risk_score']:.0f}/100  |  Case {result['case_id']}"
            ):
                _render_result_card(result, key_suffix=f"hist_{i}")

with tab_faq:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. What loan amounts can I apply for?")
        st.write(f"Up to **${Config.MAX_LOAN_AMOUNT:,.0f}**.")

        st.subheader("2. What credit score do I need?")
        st.write(f"Minimum recommended: **{Config.CREDIT_SCORE_THRESHOLD}**.")

        st.subheader("3. What's the maximum DTI ratio?")
        st.write(f"Generally approved below **{Config.DTI_THRESHOLD:.0%}**.")

    with c2:
        st.subheader("4. How long does approval take?")
        st.write("Most applications are processed **within seconds**.")

        st.subheader("5. What does 'Review' mean?")
        st.write("Borderline cases are flagged for manual review by the compliance team.")

        st.subheader("6. How is the risk score calculated?")
        st.write(
            "Claude AI analyses: credit history, DTI ratio, employment stability, "
            "loan-to-income ratio, and income consistency."
        )

    st.divider()
    st.info(
        "**System Architecture:** "
        "Streamlit UI → FastAPI → LangGraph StateGraph → "
        "FastMCP specialist servers (ports 8001–8004) → Claude AI decision"
    )

if __name__ == "__main__":
    pass
