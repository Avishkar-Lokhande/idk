import os
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Vendor Grading System", layout="wide")


DEFAULT_WEIGHTS = {
    "accuracy": 0.30,
    "crisis": 0.30,
    "resilience": 0.20,
    "cost": 0.10,
    "credit": 0.10,
}

DEFAULT_THRESHOLDS = {
    "A": 8.5,
    "B": 7.0,
    "C": 5.0,
}

HISTORY_FILE = "vendor_history.csv"


def init_state():
    if "weights" not in st.session_state:
        st.session_state.weights = DEFAULT_WEIGHTS.copy()
    if "thresholds" not in st.session_state:
        st.session_state.thresholds = DEFAULT_THRESHOLDS.copy()
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def valid_credit_days(value: str) -> bool:
    text = value.strip().lower()
    if not text:
        return False
    if text in {"advance", "0 (advance)", "na", "n/a"}:
        return True
    return text.isdigit()


def get_resilience_label(score: float) -> str:
    if score >= 9:
        return "Elite"
    if score >= 7.5:
        return "Strong"
    if score >= 6:
        return "Moderate"
    return "Weak"


def grade_and_action(total_score: float, thresholds: dict):
    if total_score >= thresholds["A"]:
        return "A", "Priority Partner", "Give first right of refusal on new bookings.", "grade-A"
    if total_score >= thresholds["B"]:
        return "B", "Standard Partner", "Maintain current volumes and monitor monthly.", "grade-B"
    if total_score >= thresholds["C"]:
        return "C", "Backup Only", "Use only when stronger vendors are unavailable.", "grade-C"
    return "D/F", "Immediate Termination", "Phase out this vendor and replace.", "grade-DF"


def save_evaluation(row: dict):
    row_df = pd.DataFrame([row])
    if os.path.exists(HISTORY_FILE):
        row_df.to_csv(HISTORY_FILE, mode="a", index=False, header=False)
    else:
        row_df.to_csv(HISTORY_FILE, index=False)


def load_history() -> pd.DataFrame:
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()
    return pd.read_csv(HISTORY_FILE)


init_state()

# --- Custom CSS (dark/light safe) ---
st.markdown(
    """
<style>
    .grade-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
        border: 2px solid transparent;
    }
    .grade-A { background: #d4edda; color: #155724; border-color: #28a745; }
    .grade-B { background: #cce5ff; color: #004085; border-color: #007bff; }
    .grade-C { background: #fff3cd; color: #856404; border-color: #ffc107; }
    .grade-DF { background: #f8d7da; color: #721c24; border-color: #dc3545; }
    .hint-box {
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(127, 127, 127, 0.35);
        background: rgba(127, 127, 127, 0.08);
        color: var(--text-color);
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("Vendor Grading and Management System")
st.caption("Manual input dashboard with fixed weighted logic for vendor grading")

# ============================================================
# SIDEBAR: READ-ONLY SETTINGS
# ============================================================
with st.sidebar:
    st.subheader("Settings")
    st.caption("Scoring logic is fixed for all users.")

    with st.expander("Weights", expanded=True):
        st.write(f"Accuracy: {st.session_state.weights['accuracy']:.2f}")
        st.write(f"Crisis: {st.session_state.weights['crisis']:.2f}")
        st.write(f"Resilience: {st.session_state.weights['resilience']:.2f}")
        st.write(f"Cost: {st.session_state.weights['cost']:.2f}")
        st.write(f"Credit: {st.session_state.weights['credit']:.2f}")

    with st.expander("Grade Thresholds", expanded=False):
        st.write(f"A >= {st.session_state.thresholds['A']:.1f}")
        st.write(f"B >= {st.session_state.thresholds['B']:.1f}")
        st.write(f"C >= {st.session_state.thresholds['C']:.1f}")

weights_sum = sum(st.session_state.weights.values())
if abs(weights_sum - 1.0) > 0.0001:
    st.error(f"Weights must total 1.00, current total is {weights_sum:.2f}. Fix settings before calculating.")

st.divider()

# ============================================================
# SECTION 1: VENDOR BASIC INFO
# ============================================================
st.subheader("Vendor Information")
col1, col2, col3 = st.columns(3)

with col1:
    vendor_name = st.text_input("Vendor Name", placeholder="e.g. XYZ Logistics")
with col2:
    tier = st.selectbox("Tier", ["Tier 1", "Tier 2", "Tier 3"])
with col3:
    lane = st.text_input("Primary Lane / Service", placeholder="e.g. Nhava Sheva - Factory")

col4, col5 = st.columns(2)
with col4:
    cost_score = st.slider("Cost Score (1-10)", 1, 10, 7)
with col5:
    credit_days = st.text_input("Credit Period (Days)", placeholder="e.g. 30 or Advance")

st.divider()

# ============================================================
# SECTION 2: SCORING SYSTEM
# ============================================================
st.subheader("Scoring System")

with st.expander("View Scoring Formula", expanded=True):
    st.latex(r"""
    Total\ Score = (A \times w_A) + (B \times w_B) + (C \times w_C) + (D \times w_D) + (E \times w_E)
    """)
    st.caption(
        f"Current weights: A={st.session_state.weights['accuracy']:.2f}, "
        f"B={st.session_state.weights['crisis']:.2f}, "
        f"C={st.session_state.weights['resilience']:.2f}, "
        f"D={st.session_state.weights['cost']:.2f}, "
        f"E={st.session_state.weights['credit']:.2f}"
    )

st.markdown('<div class="hint-box"><b>Scoring Guide</b><br>1-3: Poor, 4-6: Average, 7-8: Good, 9-10: Excellent</div>', unsafe_allow_html=True)

st.markdown("#### Rate each category (1-10):")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"**A. Accuracy** *(Weight: {st.session_state.weights['accuracy']:.0%})*")
    accuracy = st.slider("Accuracy Score", 1, 10, 7, key="accuracy")

    st.markdown(f"**B. Crisis Response** *(Weight: {st.session_state.weights['crisis']:.0%})*")
    crisis = st.slider("Crisis Response Score", 1, 10, 7, key="crisis")

    st.markdown(f"**D. Cost** *(Weight: {st.session_state.weights['cost']:.0%})*")
    cost = st.slider("Cost Score", 1, 10, cost_score, key="cost")

with col_b:
    st.markdown(f"**E. Credit Availing Facility** *(Weight: {st.session_state.weights['credit']:.0%})*")
    credit = st.slider("Credit Score", 1, 10, 7, key="credit")

st.divider()

# ============================================================
# SECTION 3: RESILIENCE / RTC SUB-FORMULA
# ============================================================
st.subheader(f"Resilience / RTC Score (Category C - Weight: {st.session_state.weights['resilience']:.0%})")

with st.expander("View Resilience Formula"):
    st.latex(r"""
    Resilience\ Score = (PA \times 0.4) + (ES \times 0.4) + (RA \times 0.2)
    """)

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.markdown("**Priority Access**")
    priority_access = st.slider("Priority Access (1-10)", 1, 10, 9, key="pa")

with col_r2:
    st.markdown("**Exception Success**")
    exception_success = st.slider("Exception Success (1-10)", 1, 10, 8, key="es")

with col_r3:
    st.markdown("**Response Agility**")
    response_agility = st.slider("Response Agility (1-10)", 1, 10, 10, key="ra")

resilience_score = (priority_access * 0.4) + (exception_success * 0.4) + (response_agility * 0.2)
res_label = get_resilience_label(resilience_score)

col_res1, col_res2, col_res3 = st.columns(3)
with col_res1:
    st.metric("Priority Access Weighted", f"{priority_access * 0.4:.1f}")
with col_res2:
    st.metric("Exception Success Weighted", f"{exception_success * 0.4:.1f}")
with col_res3:
    st.metric("Response Agility Weighted", f"{response_agility * 0.2:.1f}")

st.info(f"Final Resilience Score: {resilience_score:.1f} - {res_label}")

st.latex(
    rf"Resilience = ({priority_access} \times 0.4) + ({exception_success} \times 0.4) + ({response_agility} \times 0.2) = {resilience_score:.1f}"
)

st.divider()

# ============================================================
# SECTION 4: CALCULATE FINAL GRADE
# ============================================================
can_calculate = abs(weights_sum - 1.0) <= 0.0001

if st.button("Calculate Final Grade", width="stretch", type="primary", disabled=not can_calculate):
    validation_errors = []
    if not vendor_name.strip():
        validation_errors.append("Vendor name is required.")
    if not lane.strip():
        validation_errors.append("Primary lane/service is required.")
    if not valid_credit_days(credit_days):
        validation_errors.append("Credit period must be numeric days or Advance.")

    if validation_errors:
        for msg in validation_errors:
            st.warning(msg)
    else:
        total_score = (
            (accuracy * st.session_state.weights["accuracy"])
            + (crisis * st.session_state.weights["crisis"])
            + (resilience_score * st.session_state.weights["resilience"])
            + (cost * st.session_state.weights["cost"])
            + (credit * st.session_state.weights["credit"])
        )

        grade, status, action, grade_class = grade_and_action(total_score, st.session_state.thresholds)

        st.subheader(f"Results: {vendor_name} ({tier})")
        st.markdown(f"**Lane/Service:** {lane} | **Credit Period:** {credit_days}")

        st.markdown(
            f"""
        <div class=\"grade-box {grade_class}\">
            Grade: {grade} - {status}
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(f"### Action: *{action}*")
        st.divider()

        st.markdown("#### Full Calculation")
        st.latex(
            rf"Total = ({accuracy} \times {st.session_state.weights['accuracy']:.2f}) + ({crisis} \times {st.session_state.weights['crisis']:.2f}) + "
            rf"({resilience_score:.1f} \times {st.session_state.weights['resilience']:.2f}) + ({cost} \times {st.session_state.weights['cost']:.2f}) + "
            rf"({credit} \times {st.session_state.weights['credit']:.2f}) = {total_score:.2f}"
        )

        st.metric("Final Total Score", f"{total_score:.2f} / 10")

        breakdown = pd.DataFrame(
            {
                "Category": [
                    "A. Accuracy",
                    "B. Crisis Response",
                    "C. Resilience/RTC",
                    "D. Cost",
                    "E. Credit Facility",
                ],
                "Rating (1-10)": [accuracy, crisis, round(resilience_score, 2), cost, credit],
                "Weight": [
                    f"{st.session_state.weights['accuracy']:.0%}",
                    f"{st.session_state.weights['crisis']:.0%}",
                    f"{st.session_state.weights['resilience']:.0%}",
                    f"{st.session_state.weights['cost']:.0%}",
                    f"{st.session_state.weights['credit']:.0%}",
                ],
                "Weighted Score": [
                    round(accuracy * st.session_state.weights["accuracy"], 2),
                    round(crisis * st.session_state.weights["crisis"], 2),
                    round(resilience_score * st.session_state.weights["resilience"], 2),
                    round(cost * st.session_state.weights["cost"], 2),
                    round(credit * st.session_state.weights["credit"], 2),
                ],
            }
        )
        st.dataframe(breakdown, width="stretch", hide_index=True)
        st.bar_chart(breakdown.set_index("Category")["Rating (1-10)"])

        weak = breakdown[breakdown["Rating (1-10)"] < 6]["Category"].tolist()
        if weak:
            st.warning(f"Weak areas to address: {', '.join(weak)}")
        else:
            st.success("No critical weak areas found.")

        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "vendor_name": vendor_name,
            "tier": tier,
            "lane": lane,
            "credit_days": credit_days,
            "accuracy": accuracy,
            "crisis": crisis,
            "resilience": round(resilience_score, 2),
            "cost": cost,
            "credit": credit,
            "final_score": round(total_score, 2),
            "grade": grade,
            "status": status,
            "action": action,
        }
        save_evaluation(row)
        st.success("Evaluation saved to vendor_history.csv")
        st.session_state.last_result = row

st.divider()

# ============================================================
# SECTION 5: LATEST COMPARISON (NO HISTORICAL MODELING)
# ============================================================
st.subheader("Latest Vendor Comparison")
history_df = load_history()

if history_df.empty:
    st.caption("No saved evaluations yet. Calculate at least one vendor to enable comparison.")
else:
    latest_df = (
        history_df.sort_values("timestamp").groupby("vendor_name", as_index=False).tail(1).sort_values("vendor_name")
    )
    vendors = latest_df["vendor_name"].tolist()

    if len(vendors) < 2:
        st.caption("Need at least two saved vendors for side-by-side comparison.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            v1 = st.selectbox("Vendor 1", vendors, index=0)
        with c2:
            v2_default = 1 if len(vendors) > 1 else 0
            v2 = st.selectbox("Vendor 2", vendors, index=v2_default)

        left = latest_df[latest_df["vendor_name"] == v1].iloc[0]
        right = latest_df[latest_df["vendor_name"] == v2].iloc[0]

        comp = pd.DataFrame(
            {
                "Metric": ["Final Score", "Grade", "Accuracy", "Crisis", "Resilience", "Cost", "Credit"],
                v1: [
                    left["final_score"],
                    left["grade"],
                    left["accuracy"],
                    left["crisis"],
                    left["resilience"],
                    left["cost"],
                    left["credit"],
                ],
                v2: [
                    right["final_score"],
                    right["grade"],
                    right["accuracy"],
                    right["crisis"],
                    right["resilience"],
                    right["cost"],
                    right["credit"],
                ],
            }
        )
        st.dataframe(comp, width="stretch", hide_index=True)
