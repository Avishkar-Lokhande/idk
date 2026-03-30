import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vendor Grading System", page_icon="🚚", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    .grade-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .grade-A { background: #d4edda; color: #155724; border: 2px solid #28a745; }
    .grade-B { background: #cce5ff; color: #004085; border: 2px solid #007bff; }
    .grade-C { background: #fff3cd; color: #856404; border: 2px solid #ffc107; }
    .grade-DF { background: #f8d7da; color: #721c24; border: 2px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

st.title("🚚 Vendor Grading & Management System")
st.caption("Based on your custom scoring system — input values, get instant grade & recommendation")

st.divider()

# ============================================================
# SECTION 1: VENDOR BASIC INFO
# ============================================================
st.subheader("📋 Vendor Information")
col1, col2, col3 = st.columns(3)

with col1:
    vendor_name = st.text_input("Vendor Name", placeholder="e.g. XYZ Logistics")
with col2:
    tier = st.selectbox("Tier", ["Tier 1", "Tier 2", "Tier 3"])
with col3:
    lane = st.text_input("Primary Lane / Service", placeholder="e.g. Nhava Sheva - Factory")

col4, col5 = st.columns(2)
with col4:
    cost_score = st.slider("Cost Score (1–10)", 1, 10, 7)
with col5:
    credit_days = st.text_input("Credit Period (Days)", placeholder="e.g. 30 or 0 (Advance)")

st.divider()

# ============================================================
# SECTION 2: SCORING SYSTEM (5 Categories)
# ============================================================
st.subheader(" Scoring System")

with st.expander(" View Scoring Formula", expanded=True):
    st.latex(r"""
    Total\ Score = (A \times 0.30) + (B \times 0.30) + (C \times 0.20) + (D \times 0.10) + (E \times 0.10)
    """)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("""
        | Category | Description | Weight |
        |---|---|---|
        | **A** | Accuracy | 30% |
        | **B** | Crisis Response | 30% |
        | **C** | Resilience / RTC | 20% |
        | **D** | Cost | 10% |
        | **E** | Credit Availing Facility | 10% |
        """)
    with col_f2:
        st.markdown("""
        | Grade | Score Range | Status |
        |---|---|---|
        | **A** | 8.5 – 10.0 | Priority Partner  |
        | **B** | 7.0 – 8.4 | Standard Partner  |
        | **C** | 5.0 – 6.9 | Backup Only  |
        | **D/F** | Below 5.0 | Immediate Termination  |
        """)

st.markdown("#### Rate each category (1–10):")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**A. Accuracy** *(Weight: 30%)*")
    accuracy = st.slider("Accuracy Score", 1, 10, 7, key="accuracy")

    st.markdown("**B. Crisis Response** *(Weight: 30%)*")
    crisis = st.slider("Crisis Response Score", 1, 10, 7, key="crisis")

    st.markdown("**D. Cost** *(Weight: 10%)*")
    cost = st.slider("Cost Score", 1, 10, cost_score, key="cost")

with col_b:
    st.markdown("**E. Credit Availing Facility** *(Weight: 10%)*")
    credit = st.slider("Credit Score", 1, 10, 7, key="credit")

st.divider()

# ============================================================
# SECTION 3: RESILIENCE / RTC SUB-FORMULA
# ============================================================
st.subheader(" Resilience / RTC Score (Category C — Weight: 20%)")

with st.expander(" View Resilience Formula"):
    st.latex(r"""
    Resilience\ Score = (PA \times 0.4) + (ES \times 0.4) + (RA \times 0.2)
    """)
    st.markdown("""
    | Component | Description | Multiplier |
    |---|---|---|
    | **PA** | Priority Access — "The Hold" | 0.4 |
    | **ES** | Exception Success — "The Waiver" | 0.4 |
    | **RA** | Response Agility — "The Hustle" | 0.2 |
    """)

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.markdown("**Priority Access** *(The Hold)*")
    priority_access = st.slider("Priority Access (1–10)", 1, 10, 9, key="pa")

with col_r2:
    st.markdown("**Exception Success** *(The Waiver)*")
    exception_success = st.slider("Exception Success (1–10)", 1, 10, 8, key="es")

with col_r3:
    st.markdown("**Response Agility** *(The Hustle)*")
    response_agility = st.slider("Response Agility (1–10)", 1, 10, 10, key="ra")

# Calculate Resilience Score
resilience_score = (priority_access * 0.4) + (exception_success * 0.4) + (response_agility * 0.2)

# Resilience label
if resilience_score >= 9:
    res_label = "Elite "
elif resilience_score >= 7.5:
    res_label = "Strong "
elif resilience_score >= 6:
    res_label = "Moderate "
else:
    res_label = "Weak "

col_res1, col_res2, col_res3 = st.columns(3)
with col_res1:
    st.metric("Priority Access Weighted", f"{priority_access * 0.4:.1f}")
with col_res2:
    st.metric("Exception Success Weighted", f"{exception_success * 0.4:.1f}")
with col_res3:
    st.metric("Response Agility Weighted", f"{response_agility * 0.2:.1f}")

st.info(f"**Final Resilience Score: {resilience_score:.1f}** — {res_label}")

# Show resilience formula filled
st.latex(
    rf"Resilience = ({priority_access} \times 0.4) + ({exception_success} \times 0.4) + ({response_agility} \times 0.2) = {resilience_score:.1f}"
)

st.divider()

# ============================================================
# SECTION 4: CALCULATE FINAL GRADE
# ============================================================
if st.button(" Calculate Final Grade", use_container_width=True, type="primary"):

    if not vendor_name.strip():
        st.warning("⚠️ Please enter a vendor name.")
    else:
        # Final weighted score
        total_score = (accuracy * 0.30) + (crisis * 0.30) + (resilience_score * 0.20) + \
                      (cost * 0.10) + (credit * 0.10)

        # Grade + Action
        if total_score >= 8.5:
            grade = "A"
            status = "Priority Partner "
            action = "Give them first right of refusal on all new bookings."
            grade_class = "grade-A"
        elif total_score >= 7.0:
            grade = "B"
            status = "Standard Partner "
            action = "Solid performance. Maintain current volumes."
            grade_class = "grade-B"
        elif total_score >= 5.0:
            grade = "C"
            status = "Backup Only "
            action = "High risk of brand damage. Use only when A/B vendors are unavailable."
            grade_class = "grade-C"
        else:
            grade = "D/F"
            status = "Immediate Termination "
            action = "Their uncivilized behavior is costing you more than they are worth."
            grade_class = "grade-DF"

        # Results
        st.subheader(f" Results: {vendor_name} ({tier})")
        st.markdown(f"**Lane/Service:** {lane} | **Credit Period:** {credit_days} days")

        # Grade box
        st.markdown(f"""
        <div class="grade-box {grade_class}">
            Grade: {grade} — {status}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"###  Action: *{action}*")

        st.divider()

        # Score breakdown
        st.markdown("####  Full Calculation")
        st.latex(
            rf"Total = ({accuracy} \times 0.30) + ({crisis} \times 0.30) + "
            rf"({resilience_score:.1f} \times 0.20) + ({cost} \times 0.10) + "
            rf"({credit} \times 0.10) = {total_score:.2f}"
        )

        st.metric("**Final Total Score**", f"{total_score:.2f} / 10")

        # Table breakdown
        breakdown = pd.DataFrame({
            "Category": ["A. Accuracy", "B. Crisis Response", "C. Resilience/RTC", "D. Cost", "E. Credit Facility"],
            "Rating (1–10)": [accuracy, crisis, round(resilience_score, 2), cost, credit],
            "Weight": ["30%", "30%", "20%", "10%", "10%"],
            "Weighted Score": [
                round(accuracy * 0.30, 2),
                round(crisis * 0.30, 2),
                round(resilience_score * 0.20, 2),
                round(cost * 0.10, 2),
                round(credit * 0.10, 2)
            ]
        })
        st.dataframe(breakdown, use_container_width=True, hide_index=True)

        # Bar chart
        st.bar_chart(breakdown.set_index("Category")["Rating (1–10)"])

        # Weak areas
        weak = breakdown[breakdown["Rating (1–10)"] < 6]["Category"].tolist()
        if weak:
            st.warning(f"Weak areas to address: **{', '.join(weak)}**")
        else:
            st.success("No critical weak areas found!")
