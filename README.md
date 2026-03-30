# 🚚 Vendor Grading & Management System

A professional Streamlit-based vendor evaluation platform with preset templates, weighted scoring, and instant grading recommendations.

## 📦 Features

✅ **Preset Vendor Templates** — Pre-filled vendor profiles for quick entry  
✅ **Smart Scoring System** — 5-category evaluation with automated weighting  
✅ **Resilience Calculator** — 3-component sub-formula for RTC assessment  
✅ **Instant Grading** — Auto-calculated grades (A/B/C/D-F) with actions  
✅ **Professional UI** — Industrial design with color-coded results  
✅ **CSV Export** — Download evaluation results  
✅ **Monthly Evaluation Guide** — Reference table for seasonal assessments  

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 Files Included

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `config.py` | Presets, scoring weights, grade thresholds |
| `utils.py` | Calculation & export utilities |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## 🎯 How to Use

### Step 1: Load a Preset (Optional)
Select a vendor from the **"Load Vendor Preset"** dropdown in the sidebar to auto-fill basic information.

### Step 2: Enter Vendor Information
- **Vendor Name** — Unique identifier
- **Tier** — 1, 2, or 3 (select from list)
- **Primary Lane/Service** — Select from available routes
- **Cost Score** — 1–10 slider
- **Credit Days** — Enter number or "0 (Advance)"

### Step 3: Rate Performance Categories
Drag sliders for:
- **A. Accuracy** (30% weight) — On-time delivery, compliance
- **B. Crisis Response** (30% weight) — Problem-solving speed
- **D. Cost** (10% weight) — Pricing competitiveness
- **E. Credit Facility** (10% weight) — Payment flexibility

### Step 4: Assess Resilience Components
Rate the vendor on:
- **Priority Access** (40% of resilience) — Can we hold inventory?
- **Exception Success** (40% of resilience) — Do they waive exceptions?
- **Response Agility** (20% of resilience) — How quickly can they respond?

### Step 5: Calculate & Review
1. Click **"🎯 Calculate Final Grade"**
2. Review the results including:
   - Final score and grade (A/B/C/D-F)
   - Recommended action
   - Detailed score breakdown
   - Strength/weakness analysis
3. Download CSV if needed

## 📊 Scoring Formula

```
Total Score = (A × 0.30) + (B × 0.30) + (C × 0.20) + (D × 0.10) + (E × 0.10)

Where C (Resilience) = (PA × 0.4) + (ES × 0.4) + (RA × 0.2)
```

## 🏆 Grade Mapping

| Grade | Score | Status | Recommendation |
|:---:|:---:|---|---|
| **A** | 8.5–10.0 | Priority Partner ⭐ | Give first right of refusal |
| **B** | 7.0–8.4 | Standard Partner ✅ | Maintain current volumes |
| **C** | 5.0–6.9 | Backup Only ⚠️ | Use when A/B unavailable |
| **D/F** | <5.0 | Termination ❌ | Consider replacement |

## 🔧 Customization

### Add New Vendor Presets
Edit `config.py`:
```python
VENDOR_PRESETS = {
    "Your Vendor Name": {
        "tier": "Tier 1",
        "lane": "Your Lane",
        "cost_score": 8,
        "credit_days": 30
    }
}
```

### Add New Lanes
Edit `config.py`:
```python
LANE_OPTIONS = [
    "Your New Lane",
    # ... existing lanes
]
```

### Adjust Scoring Weights
Edit `config.py`:
```python
SCORING_WEIGHTS = {
    "Accuracy": 0.30,  # Modify as needed
    "Crisis Response": 0.30,
    # ... etc
}
```
*(Ensure all weights sum to 1.0)*

## 📤 Export Data

Click **"📥 Download CSV"** after calculating a grade to export:
- Vendor information
- Final score & grade
- Category breakdown
- Recommended action

## 🎨 UI/UX Highlights

- **Industrial Design** — Professional, not AI-generated
- **Color-Coded Results** — Green (A), Blue (B), Yellow (C), Red (D/F)
- **Responsive Layout** — Works on desktop and tablet
- **Session State** — Data persists during session
- **Expandable Sections** — Formula references collapse when not needed

## ⚙️ System Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- ~50MB disk space

## 🐛 Troubleshooting

**App won't start:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
streamlit run app.py
```

**Presets not showing:**
- Ensure `config.py` is in the same directory as `app.py`
- Restart the app: Stop and run `streamlit run app.py` again

**Export not working:**
- Check that you have write permissions in the app directory

## 📝 Notes

- All scores are on a 1–10 scale for consistency
- Scores below 5.0 trigger immediate termination recommendation
- Resilience score is calculated separately before being included in final score
- Each session is independent; refreshing the page resets all data

## 👤 Support

For issues or feature requests, check the app's sidebar for current configuration settings.

---

**Version:** 1.0 | **Last Updated:** March 2026
