# Trust Heatmap Overlay for Tableau

## 🎯 Overview

The **Trust Heatmap** is an innovative feature that generates field-level "trust scores" (0-100) for your data and exports them in a format that can be overlaid on Tableau dashboards. This allows you to visually communicate data quality directly within your visualizations.

### What Makes This Unusual?

Most data quality tools give you a simple **pass/fail** report. The Trust Heatmap goes further by:

1. **Quantifying trust** (0-100 score) for each field based on 4 dimensions
2. **Tracking changes over time** with SQLite persistence
3. **Integrating directly into Tableau** via CSV/database joins
4. **Generating visual overlays** that sit on top of dashboards
5. **Providing tooltip-ready explanations** for end users

---

## 📊 How It Works

### Trust Score Components

Each field receives a **weighted trust score** (0-100) based on:

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **Completeness** | 30% | % of non-null values |
| **Validity** | 30% | Passes validation checks (schema, types, ranges) |
| **Anomaly-Free** | 25% | % of values that aren't statistical outliers |
| **Freshness** | 15% | Recency of data (for date columns) |

**Total Trust Score = (Completeness × 0.30) + (Validity × 0.30) + (Anomaly-Free × 0.25) + (Freshness × 0.15)**

### Grading Scale

| Score | Grade | Color | Interpretation |
|-------|-------|-------|----------------|
| 95-100 | A+ | 🟢 Green | Excellent - Highly trustworthy |
| 90-94 | A | 🟢 Green | Very good - Trustworthy |
| 85-89 | B+ | 🟡 Yellow | Good - Minor concerns |
| 80-84 | B | 🟡 Yellow | Acceptable - Some issues |
| 75-79 | C+ | 🟠 Orange | Fair - Notable issues |
| 70-74 | C | 🟠 Orange | Marginal - Multiple issues |
| 60-69 | D | 🔴 Red | Poor - Significant problems |
| 0-59 | F | 🔴 Red | Failing - Major data quality issues |

---

## 🚀 Quick Start

### 1. Calculate Trust Scores

```python
from utils import calculate_trust_scores, validate_for_tableau, detect_anomalies
import pandas as pd

# Load your data
df = pd.read_csv('sales_data.csv')

# Run validation and anomaly detection (optional but recommended)
validation_result, _ = validate_for_tableau(df)
anomaly_report = detect_anomalies(df, method='iqr')

# Calculate trust scores
trust_report = calculate_trust_scores(
    df,
    validation_result=validation_result,
    anomaly_report=anomaly_report,
    date_column='order_date',  # Specify date column for freshness
    dataset_name='Sales Data'
)

# View overall trust
print(f"Overall Trust Score: {trust_report.overall_trust_score:.1f}/100")

# View field-level scores
for score in trust_report.field_scores:
    print(f"{score.field_name}: {score.trust_score:.1f} ({score.get_grade()})")
```

### 2. Export for Tableau

```python
from utils import export_trust_scores_for_tableau

# Export to CSV (saved to exports/ directory)
csv_path = export_trust_scores_for_tableau(trust_report, save_to_db=True)

print(f"Trust scores exported to: {csv_path}")
# Output: exports/trust_scores_Sales_Data.csv
```

### 3. Import into Tableau

#### Option A: CSV Data Source

1. In Tableau, go to **Data → New Data Source**
2. Select **Text file** and choose `exports/trust_scores_Sales_Data.csv`
3. The trust scores are now available as a separate data source

#### Option B: Join with Your Data

```sql
-- In Tableau Custom SQL
SELECT
    main.*,
    trust.Trust_Score,
    trust.Grade,
    trust.Color,
    trust.Warnings
FROM your_table main
LEFT JOIN trust_scores trust
    ON trust.Field_Name = 'your_field_name'
    AND trust.Dataset = 'Sales Data'
```

---

## 🎨 Visualization Examples

### Example 1: Trust Score Tooltips

**In Tableau:**
1. Drag any field to your viz
2. Edit Tooltip
3. Add Trust Score fields:

```
<Field Name>: <ATTR([Field Value])>

Trust Score: <AVG([Trust_Score])> / 100
Grade: <ATTR([Grade])>

⚠ Warnings: <ATTR([Warnings])>
✓ Reasons: <ATTR([Reasons])>
```

### Example 2: Color-Coded Metrics

Use the `Color` field from trust scores to color-code your dashboard elements:

1. Create calculated field:
```
// Trust Score Color
ATTR([Color])
```

2. Drag to **Color** shelf
3. Your metrics now show green (good), yellow (warning), or red (poor) automatically

### Example 3: Trust Heatmap Grid

Create a heatmap showing trust across all fields:

**Columns:** `Field_Name`
**Rows:** `Dataset`
**Color:** `Trust_Score` (diverging red-yellow-green palette)
**Label:** `Grade`
**Tooltip:** Full trust breakdown

### Example 4: Trust Trend Over Time

```python
from utils import TrustScoreStore

# Get historical scores
store = TrustScoreStore()
history = store.get_historical_scores(
    dataset_name='Sales Data',
    field_name='revenue',
    days=30
)

# Export for Tableau
history.to_csv('exports/trust_history.csv', index=False)
```

**In Tableau:**
- **X-axis:** `Timestamp`
- **Y-axis:** `Trust_Score`
- **Color:** `Field_Name`
- **Chart Type:** Line chart

---

## 📋 Output Format

### CSV Export Schema

| Column | Type | Description |
|--------|------|-------------|
| Dataset | String | Dataset name |
| Field_Name | String | Column/field name |
| Trust_Score | Float (0-100) | Overall trust score |
| Grade | String | Letter grade (A+, A, B+, etc.) |
| Color | String | Hex color code for viz |
| Completeness | Float (0-100) | Completeness sub-score |
| Validity | Float (0-100) | Validity sub-score |
| Anomaly_Free | Float (0-100) | Anomaly-free sub-score |
| Freshness | Float (0-100) | Freshness sub-score |
| Sample_Size | Integer | Number of rows analyzed |
| Last_Validated | Timestamp | When trust was calculated |
| Warnings | String | Semicolon-separated warnings |
| Reasons | String | Semicolon-separated strengths |

### Example CSV Output

```csv
Dataset,Field_Name,Trust_Score,Grade,Color,Completeness,Validity,Anomaly_Free,Freshness,Sample_Size,Last_Validated,Warnings,Reasons
Sales Data,order_id,98.5,A+,#10a37f,100.0,100.0,95.0,100.0,10000,2025-01-13T10:30:00,None,Excellent data completeness (≥95%); Passes all validation checks; No significant anomalies detected; Data is very fresh (≤1 day old)
Sales Data,customer_email,75.2,C+,#e67e22,85.0,70.0,100.0,100.0,10000,2025-01-13T10:30:00,Low completeness (85.0%),Good data completeness (≥80%); Minor validation warnings only
Sales Data,revenue,88.3,B+,#f39c12,98.0,95.0,75.0,100.0,10000,2025-01-13T10:30:00,High anomaly rate (25.0%),Excellent data completeness (≥95%); Passes all validation checks
```

---

## 💡 Advanced Usage

### 1. Custom Weights

```python
calculator = TrustScoreCalculator()

# Override default weights
calculator.WEIGHTS = {
    'completeness': 0.40,  # Prioritize completeness
    'validity': 0.30,
    'anomaly': 0.20,
    'freshness': 0.10
}

report = calculator.calculate_dataset_trust(df)
```

### 2. Historical Tracking

```python
from utils import TrustScoreStore

store = TrustScoreStore()

# Save trust scores over time
for i in range(30):  # Daily for 30 days
    df = load_daily_data(i)
    report = calculate_trust_scores(df, dataset_name='Daily Sales')
    store.save_report(report)

# Analyze trends
history = store.get_historical_scores('Daily Sales', field_name='revenue')

# Find degrading fields
degrading = history.groupby('field_name')['trust_score'].apply(
    lambda x: x.iloc[0] - x.iloc[-1] > 10  # Dropped >10 points
)
```

### 3. Generate Tableau Tooltips

```python
from utils import TrustHeatmapGenerator

generator = TrustHeatmapGenerator()

for score in trust_report.field_scores:
    tooltip = generator.generate_tooltip_text(score)
    print(f"\n{score.field_name}:")
    print(tooltip)
```

Output:
```
revenue:
Trust Score: 88.3/100 (B+)

Component Scores:
  • Completeness: 98.0/100
  • Validity: 95.0/100
  • Anomaly-Free: 75.0/100
  • Freshness: 100.0/100

✓ Strengths:
  - Excellent data completeness (≥95%)
  - Passes all validation checks

⚠ Warnings:
  - High anomaly rate (25.0%)
```

### 4. Create Trust Matrix Heatmap

```python
generator = TrustHeatmapGenerator()
matrix = generator.create_trust_matrix(trust_report)

# Export for visualization
matrix.to_csv('exports/trust_matrix.csv')
```

---

## 🎯 Use Cases

### 1. Executive Dashboards

**Problem:** Executives don't know which metrics to trust
**Solution:** Add trust score badges/tooltips to every metric

```
Revenue: $1.2M (Trust: 95% ✓)
Customer Count: 1,534 (Trust: 68% ⚠)
```

### 2. Data Governance

**Problem:** Need to track data quality over time
**Solution:** Historical trust scores show quality trends

- Monitor which fields are degrading
- Alert when trust drops below threshold
- Track improvement after data fixes

### 3. Self-Service Analytics

**Problem:** Users don't know data limitations
**Solution:** Color-code fields by trust level

- Green fields: Safe to use
- Yellow fields: Use with caution
- Red fields: Known issues, verify before use

### 4. Data Catalog

**Problem:** No visibility into field reliability
**Solution:** Trust scores as metadata

```
Field: customer_email
Type: String
Trust: 75/100 (C+)
Issues: 15% missing values
Last Updated: 2 days ago
```

---

## 📊 Integration Patterns

### Pattern 1: Dashboard Overlay

1. Create trust score dashboard in Tableau
2. Publish to Tableau Server
3. Use URL actions to link from main dashboard
4. Users click "Data Trust" button → see quality overlay

### Pattern 2: Data Blending

1. Primary data source: Your business data
2. Secondary data source: Trust scores CSV
3. Blend on field name
4. Use trust scores in tooltips/colors

### Pattern 3: Calculated Field

```tableau
// Trust Score Badge
IF [Trust_Score] >= 90 THEN "✓ Trusted"
ELIF [Trust_Score] >= 75 THEN "⚠ Verify"
ELSE "✗ Review"
END
```

### Pattern 4: Parameter-Based Filtering

Create parameter: "Minimum Trust Level"
- Show only fields with trust ≥ selected level
- Filter out low-quality data automatically

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Trust Scoring
TRUST_FRESHNESS_THRESHOLD_DAYS=7  # Days before data is stale
TRUST_DB_PATH=exports/trust_scores.db  # SQLite database path
```

### Settings (config/settings.py)

```python
# Custom trust weights
TRUST_WEIGHTS = {
    'completeness': 0.30,
    'validity': 0.30,
    'anomaly': 0.25,
    'freshness': 0.15
}
```

---

## 🧪 Testing

```python
import pytest
from utils import calculate_trust_scores

def test_perfect_trust_score():
    # Perfect data
    df = pd.DataFrame({
        'id': range(100),
        'value': range(100)
    })

    report = calculate_trust_scores(df)

    for score in report.field_scores:
        assert score.trust_score >= 95.0
        assert score.get_grade() in ['A+', 'A']

def test_low_trust_with_nulls():
    # Data with 50% nulls
    df = pd.DataFrame({
        'id': range(100),
        'value': [None if i % 2 == 0 else i for i in range(100)]
    })

    report = calculate_trust_scores(df)
    value_score = [s for s in report.field_scores if s.field_name == 'value'][0]

    assert value_score.completeness_score == 50.0
    assert 'Low completeness' in ' '.join(value_score.warnings)
```

---

## 📖 Best Practices

### 1. **Update Regularly**
Run trust scoring daily/weekly and track trends over time

### 2. **Set Thresholds**
Define minimum acceptable trust levels for different use cases:
- Critical metrics: ≥90 (A grade)
- Standard metrics: ≥75 (C+ grade)
- Exploratory data: ≥60 (D grade)

### 3. **Combine with Validation**
Always run validation + anomaly detection before trust scoring for accurate results

### 4. **Document Actions**
When trust drops, document:
- What happened (data source change, pipeline issue)
- What was fixed
- Expected timeline for improvement

### 5. **Automate Alerts**
```python
# Alert on low trust
for score in trust_report.field_scores:
    if score.trust_score < 75:
        send_alert(f"Field {score.field_name} has low trust: {score.trust_score:.1f}")
```

---

## 🚨 Troubleshooting

### Q: All fields show 100% trust
**A:** You may not be passing validation/anomaly results. Ensure you run:
```python
validation_result = validate_for_tableau(df)
anomaly_report = detect_anomalies(df)
# Then pass both to calculate_trust_scores()
```

### Q: Freshness score always 100
**A:** Specify the `date_column` parameter:
```python
calculate_trust_scores(df, date_column='order_date')
```

### Q: Can't find exported CSV
**A:** Check the `exports/` directory. Default path is `exports/trust_scores_{dataset_name}.csv`

### Q: Historical scores not saving
**A:** Ensure `save_to_db=True`:
```python
export_trust_scores_for_tableau(report, save_to_db=True)
```

---

## 🎁 Example Workflow

```python
# Complete end-to-end example
from utils import (
    validate_for_tableau,
    DataCleaner,
    detect_anomalies,
    calculate_trust_scores,
    export_trust_scores_for_tableau,
    TrustScoreStore
)
import pandas as pd

# 1. Load data
df = pd.read_csv('sales_data.csv')

# 2. Run validation
validation_result, _ = validate_for_tableau(
    df,
    required_columns=['order_id', 'customer_id', 'revenue'],
    unique_columns=['order_id']
)

# 3. Detect anomalies
anomaly_report = detect_anomalies(df, method='iqr')

# 4. Calculate trust scores
trust_report = calculate_trust_scores(
    df,
    validation_result=validation_result,
    anomaly_report=anomaly_report,
    date_column='order_date',
    dataset_name='Sales Data'
)

# 5. Export for Tableau
csv_path = export_trust_scores_for_tableau(trust_report, save_to_db=True)

# 6. View results
print(f"Overall Trust: {trust_report.overall_trust_score:.1f}/100")
print(f"\nField Scores:")
for score in trust_report.field_scores:
    print(f"  {score.field_name}: {score.trust_score:.1f} ({score.get_grade()}) {score.get_color()}")

# 7. Check historical trends
store = TrustScoreStore()
history = store.get_latest_scores('Sales Data')
print(f"\nHistorical records: {len(history)}")

print(f"\nTrust scores ready for Tableau: {csv_path}")
```

---

## 📚 Resources

- **Source Code**: `utils/trust_scoring.py`
- **Examples**: See `tests/test_trust_scoring.py` (coming soon)
- **API Reference**: See module docstrings

---

**🎉 You now have a visual trust layer for Tableau dashboards!**

This is a unique feature that bridges data quality and visual analytics - most teams won't have anything like this. Use it to build confidence in your data and make quality visible to stakeholders.
