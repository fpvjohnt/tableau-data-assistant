# Tableau Data Assistant - Responsible AI Edition

> **A privacy-first, explainable AI tool for Tableau data validation and analysis**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Key Features

### ✅ Deterministic Data Validation
- Schema-based validation with Pandera
- Configurable null thresholds, uniqueness constraints
- Value range validation
- Duplicate detection
- **100% reproducible results**

### 🔒 Privacy-First Design
- Automatic PII detection (emails, phones, SSN, credit cards, etc.)
- Multiple masking strategies: partial, full, hash, remove
- Data minimization (≤100 rows to AI by default)
- Works offline for sensitive data

### 🧹 Intelligent Data Cleaning
- 8-step auto-cleaning pipeline
- Outlier detection using IQR/Z-score
- Type inference and conversion
- Tableau performance optimization

### 📊 Anomaly Detection
- IQR-based (deterministic)
- Z-score based (statistical)
- Isolation Forest (ML-optional)
- Ensemble with voting strategies

### 📝 Comprehensive Audit Logging
- PII-safe logging (auto-redacts sensitive data)
- JSONL format for easy querying
- Session tracking with summaries
- Configurable retention policies

### 📸 Dashboard UX Analysis
- AI-powered screenshot analysis
- 6 evaluation aspects (layout, accessibility, etc.)
- Actionable recommendations
- Works without AI (fallback mode)

### ⚡ SQL Optimization
- Generate Tableau-optimized SQL
- Database-specific templates (Postgres, MySQL, SQL Server, etc.)
- Query analysis and suggestions
- Index recommendations

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/fpvjohnt/tableau-data-assistant.git
cd tableau-data-assistant

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Basic Usage

```python
from utils import validate_for_tableau, DataCleaner, mask_pii_dataframe

# 1. Validate data
result, report = validate_for_tableau(
    df,
    required_columns=['customer_id', 'order_date'],
    unique_columns=['customer_id']
)

# 2. Clean data
cleaner = DataCleaner()
df_clean, cleaning_report = cleaner.auto_clean_df(df)

# 3. Mask PII
df_safe, pii_report = mask_pii_dataframe(df_clean, method='partial')

# 4. Export
df_safe.to_csv('data_cleaned.csv', index=False)
```

### Run Streamlit App

```bash
streamlit run scripts/tableau_chatbot.py
```

---

## 📖 Documentation

- **[RESPONSIBLE_AI.md](RESPONSIBLE_AI.md)** - Comprehensive responsible AI guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[tests/README.md](tests/README.md)** - Testing documentation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit UI                            │
└─────────────────┬───────────────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
┌─────▼────┐ ┌───▼────┐ ┌───▼────────┐
│Validation│ │Cleaning│ │  Privacy   │  ◄── Deterministic
└─────┬────┘ └───┬────┘ └───┬────────┘      (No AI)
      │          │          │
      └──────────┼──────────┘
                 │
         ┌───────▼────────┐
         │  Audit Logger  │  ◄────────── PII-Safe
         └───────┬────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
┌─────▼──────┐ ┌▼────────┐ ┌▼──────────────┐
│  Anomaly   │ │Screenshot│ │  AI Insights  │  ◄── Optional
│ Detection  │ │ Analysis │ │   (Claude)    │      (Cloud)
└────────────┘ └──────────┘ └───────────────┘
```

---

## 📦 What's Included

### Core Modules (utils/)
- **validation.py** (~500 lines) - Schema validation, data quality checks
- **cleaning.py** (~480 lines) - Auto-cleaning, outlier removal
- **privacy.py** (~390 lines) - PII detection, masking, data minimization
- **anomaly_detection.py** (~550 lines) - Multiple detection methods
- **logging_utils.py** (~510 lines) - PII-safe audit logging
- **screenshot_analysis.py** (~480 lines) - AI-powered UX analysis
- **sql_utils.py** (~470 lines) - SQL generation and optimization

### Configuration
- **config/settings.py** - Centralized settings with .env support

### Tests (60+ unit tests)
- **test_validation.py** - Validation module tests
- **test_privacy.py** - PII detection/masking tests
- **test_cleaning.py** - Data cleaning tests
- **test_anomaly_detection.py** - Anomaly detection tests

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# AI Behavior
AI_MODE=cloud                    # "cloud" or "offline"
MASK_PII=true                    # Auto-mask PII before AI
MAX_ROWS_FOR_AI=100              # Limit data sent to AI

# Validation
VALIDATION_ENABLED=true
NULL_THRESHOLD_PERCENT=20.0      # Max % nulls allowed
UNIQUENESS_THRESHOLD=95.0        # Min % unique for ID columns

# Logging
ENABLE_AUDIT_LOG=true
LOG_RETENTION_DAYS=30
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/test_validation.py -v

# With coverage
python -m pytest tests/ --cov=utils --cov-report=html
```

---

## 🔒 Privacy & Security

### What We DON'T Send to AI
- ❌ Raw data values
- ❌ PII (auto-masked)
- ❌ Full datasets (limited to 100 rows)
- ❌ Actual validation failures

### What We DO Send (when enabled)
- ✅ Sampled, PII-masked summaries (≤100 rows)
- ✅ Column names and types
- ✅ Aggregate statistics
- ✅ Dashboard screenshots (user-uploaded only)

### Offline Mode
Set `AI_MODE=offline` in .env for sensitive data:
- ✅ Data validation (fully deterministic)
- ✅ Data cleaning
- ✅ PII masking
- ✅ Anomaly detection (IQR/Z-score)
- ✅ SQL optimization

---

## 📊 Example Workflow

```python
import pandas as pd
from utils import (
    validate_for_tableau,
    DataCleaner,
    mask_pii_dataframe,
    detect_anomalies,
    SessionLogger
)

# Initialize session logging
from utils.logging_utils import generate_session_id
session = SessionLogger(generate_session_id())

# 1. Load data
df = pd.read_csv('sales_data.csv')
session.log_upload('sales_data.csv', df.memory_usage(deep=True).sum())

# 2. Validate
result, report = validate_for_tableau(df)
session.log_validation(result.to_dict(), duration_ms=123.4)

if not result.passed:
    print(f"❌ {result.failed_checks} validation errors")
    for error in result.errors:
        print(f"  - {error['message']}")
else:
    print("✅ Validation passed!")

# 3. Clean
cleaner = DataCleaner()
df_clean, clean_report = cleaner.auto_clean_df(df)
session.log_cleaning(df.shape, df_clean.shape, duration_ms=456.7)

# 4. Mask PII
df_safe, pii_report = mask_pii_dataframe(df_clean, method='partial')
session.log_pii_masking(pii_report.masked_columns, sum(pii_report.total_values_masked.values()))

# 5. Detect anomalies
anomaly_report = detect_anomalies(df_safe, method='iqr')
session.log_anomaly_detection('iqr', anomaly_report.total_anomalies, anomaly_report.anomaly_percentage, duration_ms=789.0)

# 6. Export
df_safe.to_csv('sales_data_cleaned.csv', index=False)
session.log_export('csv', 'sales_data_cleaned.csv')

# 7. Get session summary
summary = session.get_session_summary()
print(f"Session completed: {summary['total_actions']} actions")
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **Anthropic Claude** - AI insights and explanations
- **Pandera** - Schema validation
- **scikit-learn** - ML-based anomaly detection
- **Streamlit** - Interactive UI framework

---

## 📞 Support

- **Issues**: https://github.com/fpvjohnt/tableau-data-assistant/issues
- **Documentation**: See [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md)

---

**Version**: 2.0.0
**Last Updated**: 2025-01-13
**Status**: ✅ Production Ready

---

## 🎯 Use Cases

### For Data Analysts
- Validate data before Tableau import
- Auto-clean messy datasets
- Detect quality issues early

### For Data Engineers
- Generate optimized SQL for Tableau
- Automate data quality checks
- Monitor data pipelines

### For Compliance Teams
- Mask PII automatically
- Audit all data operations
- Work offline with sensitive data

### For UX Designers
- Analyze dashboard screenshots
- Get accessibility recommendations
- Improve dashboard usability

---

**Ready to get started?** See [QUICK_START.md](QUICK_START.md) for a 5-minute guide!
