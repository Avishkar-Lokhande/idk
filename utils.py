import pandas as pd
from config import SCORING_WEIGHTS, RESILIENCE_WEIGHTS, GRADE_THRESHOLDS, GRADE_ACTIONS

def calculate_resilience_score(priority_access, exception_success, response_agility):
    """Calculate resilience score from three components"""
    return (priority_access * RESILIENCE_WEIGHTS["Priority Access"] +
            exception_success * RESILIENCE_WEIGHTS["Exception Success"] +
            response_agility * RESILIENCE_WEIGHTS["Response Agility"])

def get_resilience_label(score):
    """Get label for resilience score"""
    if score >= 9:
        return "Elite 🏆"
    elif score >= 7.5:
        return "Strong 💪"
    elif score >= 6:
        return "Moderate ⚠️"
    else:
        return "Weak ❌"

def calculate_final_score(accuracy, crisis, resilience, cost, credit):
    """Calculate final weighted score"""
    return (accuracy * SCORING_WEIGHTS["Accuracy"] +
            crisis * SCORING_WEIGHTS["Crisis Response"] +
            resilience * SCORING_WEIGHTS["Resilience/RTC"] +
            cost * SCORING_WEIGHTS["Cost"] +
            credit * SCORING_WEIGHTS["Credit Facility"])

def get_grade_and_action(score):
    """Determine grade and action based on score"""
    for grade, threshold in GRADE_THRESHOLDS.items():
        if threshold["min"] <= score <= threshold["max"]:
            return grade, threshold["status"], GRADE_ACTIONS[grade]
    return "D/F", GRADE_THRESHOLDS["D/F"]["status"], GRADE_ACTIONS["D/F"]

def get_grade_css_class(grade):
    """Get CSS class name for grade styling"""
    grade_map = {
        "A": "grade-A",
        "B": "grade-B",
        "C": "grade-C",
        "D/F": "grade-DF"
    }
    return grade_map.get(grade, "grade-DF")

def create_breakdown_dataframe(accuracy, crisis, resilience, cost, credit):
    """Create breakdown table for display"""
    breakdown = pd.DataFrame({
        "Category": [
            "A. Accuracy",
            "B. Crisis Response",
            "C. Resilience/RTC",
            "D. Cost",
            "E. Credit Facility"
        ],
        "Rating (1–10)": [accuracy, crisis, round(resilience, 2), cost, credit],
        "Weight": ["30%", "30%", "20%", "10%", "10%"],
        "Weighted Score": [
            round(accuracy * SCORING_WEIGHTS["Accuracy"], 2),
            round(crisis * SCORING_WEIGHTS["Crisis Response"], 2),
            round(resilience * SCORING_WEIGHTS["Resilience/RTC"], 2),
            round(cost * SCORING_WEIGHTS["Cost"], 2),
            round(credit * SCORING_WEIGHTS["Credit Facility"], 2)
        ]
    })
    return breakdown

def create_resilience_breakdown(priority_access, exception_success, response_agility):
    """Create resilience sub-component breakdown"""
    breakdown = pd.DataFrame({
        "Component": ["Priority Access", "Exception Success", "Response Agility"],
        "Rating (1–10)": [priority_access, exception_success, response_agility],
        "Multiplier": ["0.4", "0.4", "0.2"],
        "Weighted Value": [
            round(priority_access * 0.4, 2),
            round(exception_success * 0.4, 2),
            round(response_agility * 0.2, 2)
        ]
    })
    return breakdown

def export_to_csv(result_data):
    """Convert result data to CSV format"""
    csv_data = []
    csv_data.append("Vendor Grading System - Export Report")
    csv_data.append("")
    csv_data.append(f"Vendor Name,{result_data.get('vendor_name', '')}")
    csv_data.append(f"Tier,{result_data.get('tier', '')}")
    csv_data.append(f"Lane/Service,{result_data.get('lane', '')}")
    csv_data.append(f"Credit Period,{result_data.get('credit_days', '')}")
    csv_data.append("")
    csv_data.append(f"Final Score,{result_data.get('final_score', '')}")
    csv_data.append(f"Grade,{result_data.get('grade', '')}")
    csv_data.append(f"Status,{result_data.get('status', '')}")
    csv_data.append(f"Action,{result_data.get('action', '')}")
    csv_data.append("")
    csv_data.append("Category,Rating,Weight,Weighted Score")
    
    breakdown = result_data.get('breakdown', pd.DataFrame())
    for idx, row in breakdown.iterrows():
        csv_data.append(f"{row['Category']},{row['Rating (1–10)']},{row['Weight']},{row['Weighted Score']}")
    
    return "\n".join(csv_data)

def export_to_excel(result_data):
    """Create Excel export with multiple sheets"""
    with pd.ExcelWriter("vendor_grading_report.xlsx", engine="openpyxl") as writer:
        # Summary sheet
        summary_df = pd.DataFrame({
            "Field": ["Vendor Name", "Tier", "Lane/Service", "Credit Period", "Final Score", "Grade", "Status"],
            "Value": [
                result_data.get('vendor_name', ''),
                result_data.get('tier', ''),
                result_data.get('lane', ''),
                result_data.get('credit_days', ''),
                result_data.get('final_score', ''),
                result_data.get('grade', ''),
                result_data.get('status', '')
            ]
        })
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        # Breakdown sheet
        breakdown = result_data.get('breakdown', pd.DataFrame())
        breakdown.to_excel(writer, sheet_name="Score Breakdown", index=False)
        
        # Resilience sheet
        resilience = result_data.get('resilience_breakdown', pd.DataFrame())
        if not resilience.empty:
            resilience.to_excel(writer, sheet_name="Resilience Details", index=False)
    
    return "vendor_grading_report.xlsx"
