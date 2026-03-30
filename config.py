# Preset Configuration for Vendor Grading System

VENDOR_PRESETS = {
    "XYZ Logistics": {
        "tier": "Tier 3",
        "lane": "Nhava Sheva - Factory",
        "cost_score": 8,
        "credit_days": 30
    },
    "ABC Shipping": {
        "tier": "Tier 1",
        "lane": "India - Europe",
        "cost_score": 6,
        "credit_days": "0 (Advance)"
    },
    "National Express": {
        "tier": "Tier 2",
        "lane": "Delhi - Mumbai",
        "cost_score": 7,
        "credit_days": 15
    },
    "FastFreight Co": {
        "tier": "Tier 1",
        "lane": "Chennai - Bangalore",
        "cost_score": 9,
        "credit_days": 7
    }
}

TIER_OPTIONS = ["Tier 1", "Tier 2", "Tier 3"]

LANE_OPTIONS = [
    "Nhava Sheva - Factory",
    "India - Europe",
    "Delhi - Mumbai",
    "Chennai - Bangalore",
    "Port Processing",
    "Cross Border",
    "Special Handling"
]

# Scoring weights (must sum to 1.0)
SCORING_WEIGHTS = {
    "Accuracy": 0.30,
    "Crisis Response": 0.30,
    "Resilience/RTC": 0.20,
    "Cost": 0.10,
    "Credit Facility": 0.10
}

# Resilience sub-formula weights
RESILIENCE_WEIGHTS = {
    "Priority Access": 0.4,
    "Exception Success": 0.4,
    "Response Agility": 0.2
}

# Grade thresholds
GRADE_THRESHOLDS = {
    "A": {"min": 8.5, "max": 10.0, "status": "Priority Partner ⭐", "color": "#28a745"},
    "B": {"min": 7.0, "max": 8.4, "status": "Standard Partner ✅", "color": "#007bff"},
    "C": {"min": 5.0, "max": 6.9, "status": "Backup Only ⚠️", "color": "#ffc107"},
    "D/F": {"min": 0, "max": 4.9, "status": "Immediate Termination ❌", "color": "#dc3545"}
}

# Actions for each grade
GRADE_ACTIONS = {
    "A": "Priority Partner — Give them first right of refusal on all new bookings.",
    "B": "Standard Partner — Solid performance. Maintain current volumes.",
    "C": "Backup Only — High risk of brand damage. Use only when A/B vendors unavailable.",
    "D/F": "Immediate Termination — Their uncivilized behavior is costing more than they're worth."
}

# Monthly Evaluation mapping
MONTHLY_EVALUATION = {
    "8.5 - 10.0": {"status": "A", "action": "Priority Partner. Give them first right of refusal on all new bookings."},
    "7.0 - 8.4": {"status": "B", "action": "Standard Partner. Solid performance. Maintain current volumes."},
    "5.0 - 6.9": {"status": "C", "action": "Backup Only. High risk of brand damage. Use only when Gold/Platinum are unavailable."},
    "Below 5.0": {"status": "D/F", "action": "Immediate Termination. Their uncivilized behavior is costing you more than they are worth."}
}
