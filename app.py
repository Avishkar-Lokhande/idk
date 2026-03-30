import streamlit as st
import pandas as pd
import io
import json
from datetime import datetime
from config import (
    VENDOR_PRESETS, TIER_OPTIONS, LANE_OPTIONS, SCORING_WEIGHTS,
    RESILIENCE_WEIGHTS, GRADE_THRESHOLDS, MONTHLY_EVALUATION
)
from utils import (
    calculate_resilience_score, get_resilience_label, calculate_final_score,
    get_grade_and_action, get_grade_css_class, create_breakdown_dataframe,
    create_resilience_breakdown, export_to_csv
)

st.set_page_config(
    page_title="Vendor Grading System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if "vendor_data" not in st.session_state:
    st.session_state.vendor_data = {}
if "calculation_done" not in st.session_state:
    st.session_state.calculation_done = False
if "results" not in st.session_state:
    st.session_state.results = {}

# --- Custom CSS (Dark Mode Compatible) ---
st.markdown("""
<style>
    :root {
        --primary-color: #1f77b4;
        --success-color: #2ca02c;
        --warning-color: #ff7f0e;
        --danger-color: #d62728;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 0.95rem;
        color: #e0e0e0;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        border-left: 4px solid #1f77b4;
        padding-left: 12px;
        margin: 1.5rem 0 1rem 0;
    }
    
    .grade-box {
        padding: 30px;
        border-radius: 8px;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 20px 0;
        border-left: 6px solid;
    }
    
    .grade-A {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border-left-color: #28a745;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.15);
    }
    
    .grade-B {
        background: linear-gradient(135deg, #cce5ff 0%, #b8daff 100%);
        color: #004085;
        border-left-color: #007bff;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
    }
    
    .grade-C {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        color: #856404;
        border-left-color: #ffc107;
        box-shadow: 0 4px 12px rgba(255, 193, 7, 0.15);
    }
    
    .grade-DF {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border-left-color: #dc3545;
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.15);
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #e9ecef;
        text-align: center;
        margin: 10px 0;
    }
    
    .weak-area {
        background: #2d2d2d;
        border-left: 4px solid #dc3545;
        padding: 12px;
        border-radius: 4px;
        color: #f0f0f0;
    }
    
    .strong-area {
        background: #2d2d2d;
        border-left: 4px solid #28a745;
        padding: 12px;
        border-radius: 4px;
        color: #f0f0f0;
    }
    
    .formula-box {
        background: #2d2d2d;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #444444;
        font-family: monospace;
        margin: 10px 0;
        color: #f0f0f0;
    }

    .info-box {
        background: #2d2d2d;
        border-left: 4px solid #0066cc;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
        color: #f0f0f0;
    }

    .success-box {
        background: #2d2d2d;
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
        color: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-title">Vendor Grading & Management System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Professional vendor evaluation with preset values, weighted scoring, and actionable insights</div>',
    unsafe_allow_html=True
)

# --- SIDEBAR: Quick Presets & Settings ---
with st.sidebar:
    st.markdown("### Quick Settings")
    
    preset_vendor = st.selectbox(
        "Load Vendor Preset",
        ["—— Custom Entry ——"] + list(VENDOR_PRESETS.keys()),
        help="Select a preset vendor to auto-fill basic info"
    )
    
    if preset_vendor != "—— Custom Entry ——" and preset_vendor in VENDOR_PRESETS:
        preset_data = VENDOR_PRESETS[preset_vendor]
        st.session_state.vendor_data = {
            "name": preset_vendor,
            **preset_data
        }

    st.divider()
    
    st.markdown("### Scoring Weights")
    st.info("""
    **Current Weights:**
    - Accuracy: 30%
    - Crisis Response: 30%
    - Resilience/RTC: 20%
    - Cost: 10%
    - Credit Facility: 10%
    """)

st.divider()

# ============================================================
# SECTION 1: VENDOR BASIC INFORMATION
# ============================================================
st.markdown('<div class="section-header">Vendor Information</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    vendor_name = st.text_input(
        "Vendor Name *",
        value=st.session_state.vendor_data.get("name", ""),
        placeholder="e.g. XYZ Logistics"
    )
    st.session_state.vendor_data["name"] = vendor_name

with col2:
    tier = st.selectbox(
        "Tier *",
        TIER_OPTIONS,
        index=TIER_OPTIONS.index(st.session_state.vendor_data.get("tier", "Tier 2")) if st.session_state.vendor_data.get("tier") in TIER_OPTIONS else 1
    )
    st.session_state.vendor_data["tier"] = tier

with col3:
    lane = st.selectbox(
        "Primary Lane / Service *",
        LANE_OPTIONS,
        index=LANE_OPTIONS.index(st.session_state.vendor_data.get("lane", "Nhava Sheva - Factory")) if st.session_state.vendor_data.get("lane") in LANE_OPTIONS else 0
    )
    st.session_state.vendor_data["lane"] = lane

col4, col5 = st.columns(2)

with col4:
    cost_score = st.slider("Cost Score (1–10) *", 1, 10, st.session_state.vendor_data.get("cost_score", 7))
    st.session_state.vendor_data["cost_score"] = cost_score

with col5:
    credit_days = st.text_input(
        "Credit Period (Days) *",
        value=str(st.session_state.vendor_data.get("credit_days", "30")),
        placeholder="e.g. 30 or 0 (Advance)"
    )
    st.session_state.vendor_data["credit_days"] = credit_days

st.divider()

# ============================================================
# SECTION 2: SCORING SYSTEM (5 Categories)
# ============================================================
st.markdown('<div class="section-header">Vendor Performance Scoring</div>', unsafe_allow_html=True)

with st.expander("View Scoring Formula & Reference", expanded=False):
    col_formula, col_reference = st.columns(2)
    
    with col_formula:
        st.markdown("**Scoring Formula:**")
        st.latex(r"""
        Total\ Score = (A \times 0.30) + (B \times 0.30) + (C \times 0.20) + (D \times 0.10) + (E \times 0.10)
        """)
        
    with col_reference:
        st.markdown("**Grade Mapping:**")
        st.markdown("""
        | Grade | Score | Status |
        |:---:|:---:|---|
        | **A** | 8.5–10.0 | Priority Partner |
        | **B** | 7.0–8.4 | Standard Partner |
        | **C** | 5.0–6.9 | Backup Only |
        | **D/F** | <5.0 | Termination |
        """)

st.markdown("**Rate each category (1–10):**")

col_score1, col_score2 = st.columns(2)

with col_score1:
    st.markdown("**A. Accuracy** *(Weight: 30%)*")
    st.caption("On-time delivery, compliance, order accuracy")
    accuracy = st.slider("Accuracy Score", 1, 10, 7, key="accuracy", help="How accurate & reliable is this vendor?")
    
    st.markdown("**B. Crisis Response** *(Weight: 30%)*")
    st.caption("Problem-solving speed, emergency handling")
    crisis = st.slider("Crisis Response Score", 1, 10, 7, key="crisis", help="How do they handle urgent issues?")
    
    st.markdown("**D. Cost** *(Weight: 10%)*")
    st.caption("Pricing competitiveness")
    cost = st.slider("Cost Score (1–10)", 1, 10, cost_score, key="cost", help="Competitive pricing?")

with col_score2:
    st.markdown("**E. Credit Availing Facility** *(Weight: 10%)*")
    st.caption("Payment terms & flexibility")
    credit = st.slider("Credit Score (1–10)", 1, 10, 7, key="credit", help="Flexible payment terms?")

st.divider()

# ============================================================
# SECTION 3: RESILIENCE / RTC SUB-FORMULA
# ============================================================
st.markdown('<div class="section-header">Resilience / RTC Assessment</div>', unsafe_allow_html=True)
st.caption("*(Weight: 20% in Final Score)*")

with st.expander("View Resilience Calculation", expanded=False):
    st.latex(r"""
    Resilience\ Score = (PA \times 0.4) + (ES \times 0.4) + (RA \times 0.2)
    """)
    col_res_ref1, col_res_ref2 = st.columns(2)
    with col_res_ref1:
        st.markdown("""
        **Components:**
        - **PA** = Priority Access (The "Hold")
        - **ES** = Exception Success (The "Waiver")
        - **RA** = Response Agility (The "Hustle")
        """)
    with col_res_ref2:
        st.markdown("""
        **Description:**
        - Can we hold inventory with them?
        - Do they waive exceptions?
        - Can they move quickly?
        """)

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.markdown("**Priority Access** *(0.4 weight)*")
    st.caption("Can they hold inventory for us?")
    priority_access = st.slider("Priority Access (1–10)", 1, 10, 9, key="pa")

with col_r2:
    st.markdown("**Exception Success** *(0.4 weight)*")
    st.caption("Do they waive exceptions?")
    exception_success = st.slider("Exception Success (1–10)", 1, 10, 8, key="es")

with col_r3:
    st.markdown("**Response Agility** *(0.2 weight)*")
    st.caption("How quickly can they respond?")
    response_agility = st.slider("Response Agility (1–10)", 1, 10, 10, key="ra")

# Calculate Resilience Score
resilience_score = calculate_resilience_score(priority_access, exception_success, response_agility)
res_label = get_resilience_label(resilience_score)

col_res_display1, col_res_display2, col_res_display3 = st.columns(3)
with col_res_display1:
    st.metric("PA Weighted", f"{priority_access * 0.4:.1f}")
with col_res_display2:
    st.metric("ES Weighted", f"{exception_success * 0.4:.1f}")
with col_res_display3:
    st.metric("RA Weighted", f"{response_agility * 0.2:.1f}")

st.markdown(f'<div class="info-box"><strong>Resilience Score: {resilience_score:.1f}/10</strong> — {res_label}</div>', unsafe_allow_html=True)

st.divider()

# ============================================================
# SECTION 4: CALCULATE FINAL GRADE
# ============================================================
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

with col_btn1:
    if st.button("Calculate Final Grade & Recommendation", use_container_width="auto", type="primary"):
        if not vendor_name.strip():
            st.error("Please enter a vendor name.")
        else:
            st.session_state.calculation_done = True
            
            # Calculate final score
            final_score = calculate_final_score(accuracy, crisis, resilience_score, cost, credit)
            grade, status, action = get_grade_and_action(final_score)
            grade_class = get_grade_css_class(grade)
            
            # Store results
            st.session_state.results = {
                "vendor_name": vendor_name,
                "tier": tier,
                "lane": lane,
                "credit_days": credit_days,
                "final_score": final_score,
                "grade": grade,
                "status": status,
                "action": action,
                "accuracy": accuracy,
                "crisis": crisis,
                "resilience": resilience_score,
                "cost": cost,
                "credit": credit,
                "breakdown": create_breakdown_dataframe(accuracy, crisis, resilience_score, cost, credit),
                "resilience_breakdown": create_resilience_breakdown(priority_access, exception_success, response_agility)
            }

with col_btn2:
    if st.button("Reset", use_container_width="auto"):
        st.session_state.calculation_done = False
        st.session_state.results = {}
        st.rerun()

with col_btn3:
    if st.session_state.calculation_done:
        csv_data = export_to_csv(st.session_state.results)
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name=f"vendor_grade_{vendor_name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ============================================================
# DISPLAY RESULTS
# ============================================================
if st.session_state.calculation_done and st.session_state.results:
    results = st.session_state.results
    
    st.divider()
    st.markdown('<div class="section-header">Evaluation Results</div>', unsafe_allow_html=True)
    
    st.markdown(
        f"**Vendor:** {results['vendor_name']} · **Tier:** {results['tier']} · **Lane:** {results['lane']}"
    )
    
    # Grade Box
    st.markdown(
        f"""<div class="grade-box {grade_class}">
        Grade: {results['grade']} — {results['status']}
        </div>""",
        unsafe_allow_html=True
    )
    
    # Score & Action
    col_score_display, col_action = st.columns([1, 2])
    
    with col_score_display:
        st.metric("Final Score", f"{results['final_score']:.2f} / 10", 
                  delta=f"{results['final_score'] - 5:.1f} above baseline")
    
    with col_action:
        st.markdown(f"### Recommended Action")
        st.markdown(f"**{results['action']}**")
    
    st.divider()
    
    # Full Calculation
    st.markdown("### Detailed Score Breakdown")
    st.latex(
        rf"Total = ({accuracy} \times 0.30) + ({crisis} \times 0.30) + ({resilience_score:.1f} \times 0.20) + ({cost} \times 0.10) + ({credit} \times 0.10) = {results['final_score']:.2f}"
    )
    
    # Breakdown Table
    col_table1, col_chart = st.columns([1.5, 1])
    
    with col_table1:
        st.dataframe(results['breakdown'], width='stretch', hide_index=True)
    
    with col_chart:
        st.bar_chart(results['breakdown'].set_index("Category")["Rating (1–10)"])
    
    st.divider()
    
    # Resilience Breakdown
    st.markdown("### Resilience Component Breakdown")
    col_res_table, col_res_chart = st.columns([1.5, 1])
    
    with col_res_table:
        st.dataframe(results['resilience_breakdown'], width='stretch', hide_index=True)
    
    with col_res_chart:
        st.bar_chart(results['resilience_breakdown'].set_index("Component")["Rating (1–10)"])
    
    st.divider()
    
    # Recommendations
    st.markdown("### Performance Analysis & Recommendations")
    
    col_weak, col_strong = st.columns(2)
    
    with col_weak:
        weak_areas = results['breakdown'][results['breakdown']["Rating (1–10)"] < 6]["Category"].tolist()
        if weak_areas:
            st.markdown(f"""
            <div class="weak-area">
            <strong>Areas for Improvement:</strong><br/>
            {', '.join(weak_areas)}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-box">
            <strong>No Critical Weak Areas</strong>
            </div>
            """, unsafe_allow_html=True)
    
    with col_strong:
        strong_areas = results['breakdown'][results['breakdown']["Rating (1–10)"] >= 8]["Category"].tolist()
        if strong_areas:
            st.markdown(f"""
            <div class="strong-area">
            <strong>Strengths:</strong><br/>
            {', '.join(strong_areas)}
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# FOOTER: MONTHLY EVALUATION REFERENCE
# ============================================================
st.divider()
st.markdown("### Monthly Evaluation Reference Guide")

eval_table = pd.DataFrame([
    {"Score Range": k, "Status": v["status"], "Action": v["action"]}
    for k, v in MONTHLY_EVALUATION.items()
])

st.dataframe(eval_table, width='stretch', hide_index=True)

st.caption("Use this table to evaluate vendors monthly and track performance trends over time.")
