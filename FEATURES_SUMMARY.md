# Tableau Data Assistant - Complete Features Summary

## 🎯 Overview

The Tableau Data Assistant is now a **comprehensive, enterprise-grade data quality and analytics platform** with responsible AI capabilities, innovative trust scoring, automated data contract generation, and AI-powered storytelling coaching.

---

## 📦 Core Features (Complete)

### 1. **Data Validation** ✅
**Module:** `utils/validation.py` (500 lines)

**Capabilities:**
- Schema-based validation using Pandera
- Required column checks
- Data type validation
- Null threshold monitoring (configurable, default: 20%)
- Uniqueness constraints (default: 95%)
- Value range validation
- Duplicate detection
- Comprehensive ValidationResult reports

**Usage:**
```python
from utils import validate_for_tableau

result, report = validate_for_tableau(
    df,
    required_columns=['customer_id', 'order_date'],
    unique_columns=['customer_id'],
    value_ranges={'revenue': {'min': 0, 'max': 1000000}}
)
```

---

### 2. **Data Cleaning** ✅
**Module:** `utils/cleaning.py` (480 lines)

**8-Step Auto-Cleaning Pipeline:**
1. Standardize column names (Tableau-compatible)
2. Remove empty rows/columns
3. Remove duplicates
4. Intelligent type conversion (datetime, numeric)
5. Handle missing values (median/mode imputation)
6. Trim whitespace
7. Cap rows for Tableau performance (1M default)
8. Optimize data types for memory

**Additional Features:**
- IQR-based outlier detection
- Outlier removal with reporting
- Detailed CleaningReport

**Usage:**
```python
from utils import DataCleaner

cleaner = DataCleaner()
df_clean, report = cleaner.auto_clean_df(df)
```

---

### 3. **Privacy & PII Masking** ✅
**Module:** `utils/privacy.py` (390 lines)

**Features:**
- **Auto-detection** of 15+ PII types
  - Email, phone, SSN, credit cards, IP addresses
  - Account numbers, passwords, names, addresses
- **Multiple masking strategies:**
  - `partial`: Show first/last chars (e.g., "jo****@example.com")
  - `full`: Complete masking (e.g., "******************")
  - `hash`: SHA-256 anonymization
  - `remove`: Drop PII columns entirely
- **Data minimization:** Limit rows sent to AI (default: 100)
- **Sampling methods:** head, tail, random, stratified

**Usage:**
```python
from utils import mask_pii_dataframe

df_safe, pii_report = mask_pii_dataframe(df, method='partial')
```

---

### 4. **Anomaly Detection** ✅
**Module:** `utils/anomaly_detection.py` (550 lines)

**Detection Methods:**
- **IQRAnomalyDetector:** Deterministic IQR-based (no ML)
- **ZScoreAnomalyDetector:** Statistical Z-score method
- **IsolationForestDetector:** ML-based (requires scikit-learn)
- **AnomalyDetectorEnsemble:** Combines methods with voting
  - Voting strategies: majority, unanimous, any

**Usage:**
```python
from utils import detect_anomalies

report = detect_anomalies(df, method='iqr')  # or 'zscore', 'isolation_forest', 'ensemble'
```

---

### 5. **PII-Safe Audit Logging** ✅
**Module:** `utils/logging_utils.py` (510 lines)

**Features:**
- **PIISafeFormatter:** Auto-redacts sensitive data from logs
- **AuditLogger:** JSONL-based audit trail
  - Session tracking
  - Historical queries
  - Auto-cleanup (retention: 30 days default)
- **SessionLogger:** Tracks specific operations
  - Upload, validation, cleaning, PII masking
  - Anomaly detection, exports, AI queries

**Usage:**
```python
from utils import SessionLogger, generate_session_id

session = SessionLogger(generate_session_id())
session.log_upload('file.csv', 1024)
session.log_validation(result.to_dict(), duration_ms=123)
```

---

### 6. **Screenshot Analysis** ✅
**Module:** `utils/screenshot_analysis.py` (480 lines)

**Features:**
- **AI-powered UX analysis** using Claude Vision
- **6 Evaluation Aspects:**
  1. Layout clarity
  2. Label readability
  3. Filter placement
  4. Visual clutter
  5. Accessibility
  6. Color usage
- Scores (0-100) + actionable recommendations
- **Fallback mode:** Works without AI (basic metadata)

**Usage:**
```python
from utils import analyze_dashboard_screenshot

analysis, report = analyze_dashboard_screenshot('dashboard.png')
```

---

### 7. **SQL Optimization** ✅
**Module:** `utils/sql_utils.py` (470 lines)

**Features:**
- **Generate Tableau-optimized SQL**
  - Supports: Postgres, MySQL, SQL Server, Redshift, Snowflake
- **SQLOptimizer:** Analyzes queries and suggests improvements
- **Templates:** Custom SQL, incremental extracts, live connections
- **Index recommendations** based on DataFrame analysis

**Usage:**
```python
from utils import optimize_sql_for_tableau

report, formatted = optimize_sql_for_tableau(query)
```

---

### 8. **Trust Heatmap** ✅ **NEW!**
**Module:** `utils/trust_scoring.py` (600 lines)

**Revolutionary Feature - Unique to This Tool!**

**What It Does:**
Generates field-level "trust scores" (0-100) based on 4 dimensions:
- **Completeness** (30%): % of non-null values
- **Validity** (30%): Passes validation checks
- **Anomaly-Free** (25%): % without statistical outliers
- **Freshness** (15%): Recency of data

**Outputs:**
1. **CSV for Tableau import** (join with your data)
2. **SQLite database** for historical tracking
3. **Visual color codes** (green/yellow/orange/red)
4. **Tooltip-ready text** with detailed explanations
5. **Letter grades** (A+, A, B+, B, C+, C, D, F)

**Why It's Unusual:**
- Most tools give pass/fail. This quantifies trust.
- Tracks quality over time (historical trends)
- Integrates directly into Tableau dashboards
- Provides visual overlays showing data confidence

**Usage:**
```python
from utils import calculate_trust_scores, export_trust_scores_for_tableau

# Calculate scores
trust_report = calculate_trust_scores(
    df,
    validation_result=validation_result,
    anomaly_report=anomaly_report,
    date_column='order_date',
    dataset_name='Sales Data'
)

# Export for Tableau
csv_path = export_trust_scores_for_tableau(trust_report, save_to_db=True)
# Output: exports/trust_scores_Sales_Data.csv
```

**Tableau Integration:**
```tableau
// In Tableau, create calculated field:
Trust Badge =
IF [Trust_Score] >= 90 THEN "✓ Trusted"
ELIF [Trust_Score] >= 75 THEN "⚠ Verify"
ELSE "✗ Review"
END
```

---

### 9. **Data Contract Copilot** ✅ **NEW!**
**Module:** `utils/data_contract.py` (800 lines)

**Revolutionary Feature - Proactive Data Quality Management!**

**What It Does:**
Instead of just reporting "your data is broken," this module analyzes recurring validation failures and automatically **drafts formal data contracts** to propose to upstream data providers (ServiceNow, ETL teams, APIs, etc.).

**Outputs:**
1. **Markdown Contract** - Complete formal agreement with SLAs
2. **JSON Contract** - Machine-readable specification
3. **JIRA Ticket Template** - Ready to send to upstream teams
4. **Historical Analysis** - Pattern detection over time
5. **Actionable Recommendations** - Specific fixes for upstream systems

**Key Components:**
- **Field Contracts**: Data type, nullable, constraints, allowed values, SLAs
- **Quality Requirements**: Completeness, uniqueness, freshness thresholds
- **Historical Issues**: What's been broken and when
- **Governance**: Ownership, escalation path, review cycle
- **SLA Proposals**: Based on observed data behavior

**Why It's Unusual:**
- Most tools stop at reporting problems
- This generates **actionable contract proposals**
- Bridges consumers (Tableau) and producers (upstream systems)
- Uses AI to generate natural language contracts
- Tracks issue patterns over time
- Proposes realistic SLAs based on historical data

**Usage:**
```python
from utils import generate_data_contract, export_data_contract_proposal

# Collect historical validation results
historical_results = []
for day in range(30):
    df = load_daily_data(day)
    result, _ = validate_for_tableau(df)
    historical_results.append({
        'timestamp': datetime.now() - timedelta(days=30-day),
        'result': result
    })

# Generate contract
contract = generate_data_contract(
    df=df_current,
    dataset_name='Sales Data',
    upstream_system='ServiceNow CRM',
    historical_validation_results=historical_results,
    days_history=30
)

# Export for upstream team
paths = export_data_contract_proposal(contract, include_jira=True)
# Output:
# - exports/contracts/contract_Sales_Data.md (formal contract)
# - exports/contracts/contract_Sales_Data.json (machine-readable)
# - exports/contracts/jira_ticket_Sales_Data.md (ticket template)
```

**Example Contract Output:**
```markdown
# Data Contract: Sales Data
**Provider**: ServiceNow CRM
**Consumer**: Tableau Analytics

## Service Level Agreements (SLAs)
- **Uptime**: 99.9%
- **Freshness**: Data delivered within 24 hours
- **Completeness**: ≥95% of required fields populated

## Field Specifications

### customer_email
- **Type**: STRING
- **Required**: Yes
- **Nullable**: Yes (max 5%)
- **SLA Requirements**:
  - Must contain @ symbol
  - Must follow email format (RFC 5322)
- **Historical Issues**:
  - High null rate (15-20%) observed over past 30 days
  - Invalid format detected on 2025-01-08
```

**Integration with Trust Scoring:**
```python
# Monitor contract compliance
trust_report = calculate_trust_scores(df)
if trust_report.overall_trust_score < contract.quality_requirements['completeness_threshold']:
    create_jira_incident('Contract SLA violation detected!')
```

---

### 10. **Dashboard Story Coach (Narrative Critic)** ✅ **NEW!**
**Module:** `utils/story_coach.py` (700 lines)

**Revolutionary Feature - AI-Powered Storytelling Coaching!**

**What It Does:**
Most tools critique dashboard **design** (colors, fonts, layouts). The Story Coach critiques **storytelling** (narrative arc, insight clarity, call to action). It analyzes screenshots using Claude's vision capabilities to evaluate whether your dashboard tells a clear, compelling story.

**Core Innovation:**
Uses the classic three-act story structure to evaluate dashboards:
1. **Beginning (Context)**: Does it establish what we're looking at and why?
2. **Middle (Insights)**: Does it present clear insights or trends?
3. **End (Actions)**: Does it lead to conclusions or next steps?

**Outputs:**
1. **Story Arc Analysis**: Scores for beginning, middle, end (0-100 each)
2. **Before/After Narratives**: Current story vs. improved version
3. **Email-Ready Summary**: 1-2 paragraphs for stakeholders
4. **Layout Recommendations**: Specific changes to improve flow
5. **Section Titles**: Narrative titles like "Where We Are Now", "What Changed?", "What We Should Do Next"
6. **Overall Story Score**: 0-100 storytelling effectiveness

**Why It's Unusual:**
- First tool to critique **narrative structure** not just visual design
- Uses AI vision to analyze dashboard screenshots
- Generates before/after story comparison
- Provides actionable storytelling recommendations
- Creates email drafts automatically
- Focuses on "does it guide the viewer?" not "does it look good?"

**Usage:**
```python
from utils import analyze_dashboard_story, export_story_report

# Analyze dashboard storytelling
report = analyze_dashboard_story(
    screenshot_path='operations_dashboard.png',
    primary_metric='Mean Time to Resolution',
    dashboard_name='IT Operations Dashboard',
    context='Daily standup for ops team'
)

# View story analysis
print(f"Story Score: {report.overall_story_score:.0f}/100")
print(f"Beginning: {report.story_arc.beginning_score:.0f}/100")
print(f"Middle: {report.story_arc.middle_score:.0f}/100")
print(f"End: {report.story_arc.end_score:.0f}/100")

# View narratives
print(f"\nCurrent: {report.current_narrative}")
print(f"\nImproved: {report.improved_narrative}")

# Get recommendations
for rec in report.layout_recommendations:
    if rec.priority == 'high':
        print(f"✓ {rec.recommended_state}")
        print(f"  Impact: {rec.expected_impact}")

# Export reports
paths = export_story_report(report)
# Output:
# - exports/story_coach/report.md (full analysis)
# - exports/story_coach/email_draft.txt (ready to send)
# - exports/story_coach/report.json (structured data)
```

**Example Analysis:**

**Current Story (Score: 45/100):**
> "The dashboard shows incident data for the past week. There are 42 incidents displayed across various categories. Multiple charts show different metrics and trends."

**Issues:**
- No clear message or headline
- Viewers must work to extract insights
- Missing call to action

**Improved Story (Score: 88/100):**
> "Incident volume decreased 15% this week to 42 total incidents, the lowest in 3 months. The drop is driven by P1/P2 incidents declining 40% after deploying automated monitoring on Monday. To sustain this trend, we should expand monitoring to the remaining 3 teams next week."

**Key Changes:**
1. Lead with the headline: "42 incidents (15% decrease)"
2. Explain the driver: "P1/P2 down 40% after Monday's deployment"
3. Conclude with action: "Expand to 3 remaining teams"

**Suggested Section Titles:**
- Top: "This Week's Performance Snapshot"
- Middle: "What's Driving the Improvement?"
- Bottom: "Recommended Actions for Next Week"

**Integration with Other Features:**
```python
# Combine storytelling + data quality
story_report = analyze_dashboard_story(screenshot_path='dashboard.png', ...)
trust_report = calculate_trust_scores(df, ...)

# Combined health check
print(f"Story Quality: {story_report.overall_story_score:.0f}/100")
print(f"Data Quality: {trust_report.overall_trust_score:.0f}/100")

overall = (story_report.overall_story_score + trust_report.overall_trust_score) / 2
if overall >= 85:
    print(f"✓ Dashboard is production-ready ({overall:.0f}/100)")
```

**Use Cases:**
1. **Executive Dashboard Review**: Ensure dashboards tell story in <30 seconds
2. **Analyst Self-Review**: Get feedback before presenting to stakeholders
3. **Dashboard Redesign**: Improve low-adoption dashboards
4. **Template Library**: Extract best practices from high-scoring dashboards

---

## 📊 Statistics

### Code Metrics
| Category | Count |
|----------|-------|
| **Total Modules** | 11 (validation, cleaning, privacy, anomaly, logging, screenshot, SQL, trust, contract, story coach, config) |
| **Total Code** | ~6,000 lines |
| **Test Coverage** | 60+ unit tests |
| **Documentation** | ~6,000+ lines |
| **Functions** | 90+ |
| **Classes** | 30+ |
| **Configuration Options** | 30+ env variables |

### Module Breakdown
| Module | Lines | Key Features |
|--------|-------|--------------|
| validation.py | 500 | Schema validation, quality checks |
| cleaning.py | 480 | Auto-clean, outlier removal |
| privacy.py | 390 | PII detection, masking, minimization |
| anomaly_detection.py | 550 | IQR, Z-score, Isolation Forest, ensemble |
| logging_utils.py | 510 | PII-safe logging, audit trails |
| screenshot_analysis.py | 480 | AI UX analysis, accessibility |
| sql_utils.py | 470 | SQL generation, optimization |
| **trust_scoring.py** | **600** | **Trust heatmap** |
| **data_contract.py** | **800** | **Contract auto-generation** |
| **story_coach.py** | **700** | **Narrative coaching (NEW!)** |
| settings.py | 500 | Configuration management |
| **Total** | **5,980** | |

---

## 🎨 Unique Innovations

### 1. **Trust Heatmap Overlay** 🆕
- **First-of-its-kind** field-level trust visualization
- Quantifies data quality (0-100) instead of pass/fail
- Historical tracking with SQLite persistence
- Tableau-ready CSV exports with color codes
- Tooltip text generation for end-user transparency

### 2. **Data Contract Auto-Generation** 🆕
- **Industry-first** automated contract drafting
- Analyzes recurring validation failures over time
- Generates formal SLAs and requirements for upstream systems
- Creates JIRA-ready ticket templates
- Shifts from reactive ("broken") to proactive ("let's agree")
- Bridges data consumers and producers with concrete agreements

### 3. **Dashboard Story Coach** 🆕
- **First tool** to critique narrative structure, not just visual design
- Evaluates story arc: beginning (context), middle (insights), end (actions)
- Uses Claude vision API for screenshot analysis
- Generates before/after story comparison
- Creates email-ready summaries automatically
- Focuses on "does it guide the viewer?" over "does it look good?"

### 4. **AI as Explainer, Not Decider**
- Deterministic validation comes first
- AI provides natural language explanations
- All critical decisions are reproducible

### 4. **Privacy-First Architecture**
- Auto-detects and masks PII before AI processing
- Data minimization (≤100 rows to AI)
- PII-safe logging (auto-redaction)

### 5. **Offline Capability**
- Works without internet for sensitive data
- Set `AI_MODE=offline` in .env
- All core features work deterministically

### 6. **Comprehensive Audit Trail**
- JSONL format for easy querying
- Session-based tracking
- Historical analysis and cleanup

---

## 🚀 Use Cases

### Executive Dashboards
**Problem:** Stakeholders don't know which metrics to trust
**Solution:** Add trust score badges to every metric
```
Revenue: $1.2M (Trust: 95% ✓)
Customer Count: 1,534 (Trust: 68% ⚠)
```

### Data Governance
**Problem:** Need to track quality over time
**Solution:** Historical trust scores show trends
- Monitor degrading fields
- Alert when trust drops
- Track improvement after fixes

### Self-Service Analytics
**Problem:** Users don't know data limitations
**Solution:** Color-code fields by trust level
- Green: Safe to use
- Yellow: Use with caution
- Red: Known issues

### Compliance (GDPR, HIPAA)
**Problem:** Need to demonstrate data protection
**Solution:**
- Auto PII masking
- Complete audit trail
- Offline mode for PHI

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md) | Comprehensive responsible AI guide |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical implementation details |
| [TRUST_HEATMAP_GUIDE.md](TRUST_HEATMAP_GUIDE.md) | Trust scoring feature guide |
| [DATA_CONTRACT_GUIDE.md](DATA_CONTRACT_GUIDE.md) | Data contract auto-generation guide |
| [STORY_COACH_GUIDE.md](STORY_COACH_GUIDE.md) | Dashboard storytelling coaching guide |
| [README_RESPONSIBLE_AI.md](README_RESPONSIBLE_AI.md) | Project overview |
| [tests/README.md](tests/README.md) | Testing documentation |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/test_validation.py -v
python -m pytest tests/test_privacy.py -v
python -m pytest tests/test_cleaning.py -v
python -m pytest tests/test_anomaly_detection.py -v

# With coverage
python -m pytest tests/ --cov=utils --cov-report=html
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# API
ANTHROPIC_API_KEY=sk-ant-api03-...

# AI Behavior
AI_MODE=cloud                         # "cloud" or "offline"
MASK_PII=true
MAX_ROWS_FOR_AI=100

# Validation
VALIDATION_ENABLED=true
NULL_THRESHOLD_PERCENT=20.0
UNIQUENESS_THRESHOLD=95.0

# Anomaly Detection
ANOMALY_CONTAMINATION=0.05
ANOMALY_N_ESTIMATORS=100

# Screenshot Analysis
SCREENSHOT_MAX_SIZE_MB=10
SCREENSHOT_MIN_DIMENSION=400

# Logging
ENABLE_AUDIT_LOG=true
LOG_RETENTION_DAYS=30

# Trust Scoring
TRUST_FRESHNESS_THRESHOLD_DAYS=7
```

---

## 🎯 Example Workflow

```python
# Complete end-to-end workflow with trust scoring
from utils import *
import pandas as pd

# 1. Load data
df = pd.read_csv('sales_data.csv')

# 2. Validate
validation_result, _ = validate_for_tableau(df)

# 3. Clean
cleaner = DataCleaner()
df_clean, clean_report = cleaner.auto_clean_df(df)

# 4. Mask PII
df_safe, pii_report = mask_pii_dataframe(df_clean, method='partial')

# 5. Detect anomalies
anomaly_report = detect_anomalies(df_safe, method='iqr')

# 6. Calculate trust scores
trust_report = calculate_trust_scores(
    df_safe,
    validation_result=validation_result,
    anomaly_report=anomaly_report,
    date_column='order_date',
    dataset_name='Sales Data'
)

# 7. Export for Tableau
csv_path = export_trust_scores_for_tableau(trust_report, save_to_db=True)

# 8. View results
print(f"Overall Trust: {trust_report.overall_trust_score:.1f}/100")
for score in trust_report.field_scores:
    print(f"{score.field_name}: {score.trust_score:.1f} ({score.get_grade()})")

# 9. Export cleaned data
df_safe.to_csv('sales_data_cleaned.csv', index=False)
```

---

## 🏆 Competitive Advantages

| Feature | This Tool | Typical Tools |
|---------|-----------|---------------|
| **Trust Scoring** | ✅ 0-100 scores with grades | ❌ Pass/fail only |
| **Data Contract Generation** | ✅ Auto-draft contracts for upstream | ❌ Not available |
| **Story Coaching** | ✅ AI narrative critique with arc analysis | ❌ Not available |
| **Historical Tracking** | ✅ SQLite database + trends | ❌ One-time reports |
| **Tableau Integration** | ✅ Direct CSV import, join-ready | ❌ Manual copy-paste |
| **Visual Trust Layer** | ✅ Heatmaps, color codes, tooltips | ❌ Separate reports |
| **PII Auto-Masking** | ✅ Pattern + keyword detection | ⚠️ Manual configuration |
| **Offline Mode** | ✅ Full functionality w/o AI | ❌ Cloud-only |
| **Audit Logging** | ✅ PII-safe, JSONL format | ⚠️ Basic logs |
| **Multi-Method Anomaly** | ✅ IQR, Z-score, ML, ensemble | ⚠️ Single method |
| **Screenshot UX Analysis** | ✅ AI-powered accessibility review | ❌ Not available |
| **SQL Optimization** | ✅ Database-specific templates | ⚠️ Generic advice |
| **JIRA Integration** | ✅ Auto-generate ticket templates | ⚠️ Manual tickets |
| **Email Generation** | ✅ Auto-draft summaries for stakeholders | ⚠️ Manual writing |

---

## 📞 Support

- **GitHub**: https://github.com/fpvjohnt/tableau-data-assistant
- **Issues**: https://github.com/fpvjohnt/tableau-data-assistant/issues
- **Documentation**: See RESPONSIBLE_AI.md

---

## 🎉 Summary

You now have:
- ✅ **11 production-ready modules** (~6,000 lines)
- ✅ **Enterprise-grade data quality** validation and cleaning
- ✅ **Privacy-first AI** with PII masking and data minimization
- ✅ **Trust scoring heatmap** (unique innovation!)
- ✅ **Data contract auto-generation** (industry-first!)
- ✅ **Dashboard story coaching** (narrative critic!)
- ✅ **Comprehensive audit logging**
- ✅ **60+ unit tests**
- ✅ **6,000+ lines of documentation**
- ✅ **Tableau-ready exports**
- ✅ **JIRA integration** for upstream collaboration
- ✅ **Email generation** for stakeholder communication

**This is not just a data assistant - it's a complete data quality platform with responsible AI, proactive data governance, and AI-powered storytelling coaching built in!**

---

**Version**: 2.3.0 (Story Coach Edition)
**Status**: ✅ Production Ready
**Last Updated**: 2025-01-14
