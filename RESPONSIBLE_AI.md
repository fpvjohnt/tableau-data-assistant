# Responsible AI Implementation Guide

## Overview

The Tableau Data Assistant implements responsible AI principles to ensure ethical, transparent, and privacy-preserving data analysis. This document outlines the design philosophy, safeguards, and best practices implemented in this application.

---

## Core Principles

### 1. **AI as Explainer, Not Decision-Maker**

**Philosophy:** Deterministic validation comes first; AI provides explanations and insights.

- ✅ Schema validation uses **Pandera** for deterministic, reproducible data quality checks
- ✅ Anomaly detection defaults to **IQR and Z-score** (statistical, deterministic methods)
- ✅ AI (Claude) is used **only** for:
  - Explaining validation results in natural language
  - Providing actionable recommendations
  - Analyzing dashboard screenshots for UX insights
  - Answering user questions about data patterns

**Implementation:**
- `utils/validation.py`: Schema-based validation with clear pass/fail criteria
- `utils/anomaly_detection.py`: Multiple deterministic detectors (IQR, Z-score) with optional ML (Isolation Forest) as enhancement
- `utils/screenshot_analysis.py`: AI analyzes dashboard UX but users make final design decisions

---

### 2. **Privacy First**

**Philosophy:** Minimize data exposure to AI; mask PII automatically.

#### Data Minimization
- Only send **sample data** to AI (default: 100 rows max, configurable via `MAX_ROWS_FOR_AI`)
- Sample methods: head, tail, random, stratified
- Configurable via `.env`: `MAX_ROWS_FOR_AI=100`

#### PII Detection and Masking
- **Automatic PII detection** via:
  - Column name keywords (email, phone, SSN, etc.)
  - Content pattern matching (regex for emails, phones, credit cards, IP addresses)
- **Masking strategies**:
  - `partial`: Show first/last chars (default for AI queries)
  - `full`: Complete masking
  - `hash`: SHA-256 anonymization
  - `remove`: Drop PII columns entirely

**Implementation:**
- `utils/privacy.py`: `PIIDetector`, `PIIMasker`, `DataMinimizer`
- `config/settings.py`: `MASK_PII=true`, `PII_COLUMNS_KEYWORDS` list
- All AI queries automatically apply `DataMinimizer` before sending to Claude

#### Example
```python
from utils.privacy import mask_pii_dataframe

# Automatically detect and mask PII before AI analysis
df_masked, report = mask_pii_dataframe(df, method='partial')
```

---

### 3. **Transparency and Auditability**

**Philosophy:** Users should know exactly what operations were performed and why.

#### Comprehensive Logging
- **PII-Safe Logging**: Automatically redacts sensitive data from log files
- **Audit Trail**: JSONL-based audit log tracks all operations with timestamps
- **Session Tracking**: Every action tied to a unique session ID

**Logged Events:**
- File uploads (filename, size, not content)
- Data validation results (pass/fail counts, not actual data)
- Data cleaning operations (row/column counts, not values)
- PII masking actions (columns affected, not masked values)
- Anomaly detection (counts, not flagged records)
- AI queries (query type, row count, not data content)
- Exports (format, filename)

**Implementation:**
- `utils/logging_utils.py`: `AuditLogger`, `SessionLogger`, `PIISafeFormatter`
- `config/settings.py`: `ENABLE_AUDIT_LOG=true`, `LOG_RETENTION_DAYS=30`
- Logs stored in `logs/audit.jsonl` (JSONL format for easy parsing)

#### Example Audit Entry
```json
{
  "timestamp": "2025-01-15T10:30:45",
  "session_id": "a1b2c3d4e5f6g7h8",
  "action": "validate",
  "resource": "dataset",
  "details": {
    "passed": false,
    "total_checks": 25,
    "failed_checks": 3
  },
  "status": "success",
  "duration_ms": 1234.5
}
```

---

### 4. **Deterministic Validation**

**Philosophy:** Data quality checks must be consistent, reproducible, and explainable.

#### Schema-Based Validation (Pandera)
- **Required columns**: Ensure critical fields are present
- **Data types**: Validate expected types (int, float, datetime, string)
- **Null thresholds**: Flag columns with excessive missing values (default: >20%)
- **Uniqueness constraints**: Check ID columns meet uniqueness requirements (default: >95%)
- **Value ranges**: Validate numeric columns within expected bounds
- **Duplicate detection**: Identify and report duplicate rows

**Configuration:**
```env
VALIDATION_ENABLED=true
NULL_THRESHOLD_PERCENT=20.0
UNIQUENESS_THRESHOLD=95.0
VALIDATION_SAMPLE_SIZE=10000
```

**Implementation:**
- `utils/validation.py`: `DataValidator` class with deterministic checks
- Returns `ValidationResult` with detailed pass/fail information
- AI (Claude) **explains** validation results but doesn't change outcomes

#### Example
```python
from utils.validation import validate_for_tableau

result, report = validate_for_tableau(
    df,
    required_columns=['customer_id', 'order_date', 'revenue'],
    unique_columns=['customer_id'],
    value_ranges={'revenue': {'min': 0, 'max': 1000000}}
)

if not result.passed:
    print(f"Validation failed: {result.failed_checks} issues found")
    for error in result.errors:
        print(f"- {error['message']}")
```

---

### 5. **Offline Capability**

**Philosophy:** Critical functionality should work without AI/cloud connectivity.

#### Offline Mode Features
- ✅ Data validation (fully deterministic)
- ✅ Data cleaning (rule-based transformations)
- ✅ Anomaly detection (IQR, Z-score methods)
- ✅ PII masking (pattern-based detection)
- ✅ SQL generation and optimization
- ✅ Basic screenshot analysis (image metadata only)

#### Cloud-Enhanced Features (require API key)
- 🔒 AI-powered insights and recommendations
- 🔒 Natural language explanations of validation results
- 🔒 Advanced screenshot UX analysis with Claude Vision
- 🔒 Interactive chat for data questions

**Configuration:**
```env
AI_MODE=offline  # or "cloud"
ENABLE_ANOMALY_DETECTION=true
ENABLE_SCREENSHOT_ANALYSIS=true
```

**Implementation:**
- `config/settings.py`: `is_offline_mode()`, `is_ai_enabled()`
- All modules gracefully degrade when AI unavailable
- Clear user messaging when features require AI

---

## Module-by-Module Safeguards

### Validation (`utils/validation.py`)
- **Deterministic**: Uses statistical thresholds, not ML
- **Configurable**: All thresholds adjustable via `.env`
- **Transparent**: Returns detailed `ValidationResult` with all checks
- **No PII**: Validates schema, not individual values

### Cleaning (`utils/cleaning.py`)
- **Deterministic**: Rule-based transformations
- **Reversible**: Original data preserved, cleaned data returned separately
- **Auditable**: `CleaningReport` lists all operations performed
- **Configurable**: Aggressive mode optional, conservative by default

### Privacy (`utils/privacy.py`)
- **Auto-detection**: Finds PII via keywords and patterns
- **Multiple strategies**: Partial, full, hash, remove
- **Data minimization**: Limits rows sent to AI (default: 100)
- **Sampling**: Head, tail, random, stratified options

### Anomaly Detection (`utils/anomaly_detection.py`)
- **Defaults to deterministic**: IQR and Z-score (no ML required)
- **Optional ML**: Isolation Forest available when scikit-learn installed
- **Ensemble voting**: Combines multiple methods for robustness
- **Transparent**: Returns detailed `AnomalyReport` with scores and indices

### Logging (`utils/logging_utils.py`)
- **PII-safe**: `PIISafeFormatter` redacts sensitive data automatically
- **JSONL format**: Easy to parse, query, and analyze
- **Retention policy**: Auto-cleanup after configurable days (default: 30)
- **Session-based**: Groups operations for easy tracing

### Screenshot Analysis (`utils/screenshot_analysis.py`)
- **User consent**: Requires explicit screenshot upload
- **No automatic capture**: User provides images manually
- **UX focus**: Analyzes layout, accessibility, not data content
- **Fallback mode**: Works without AI (basic image metadata analysis)

### SQL Utilities (`utils/sql_utils.py`)
- **No data access**: Generates queries, doesn't execute them
- **Best practices**: Suggests optimizations based on patterns
- **Database-agnostic**: Supports multiple database types
- **User control**: Generated SQL reviewed before execution

---

## Configuration Reference

### Environment Variables (.env)

```env
# API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-...

# AI Behavior
AI_MODE=cloud                         # "cloud" or "offline"
ENABLE_ANOMALY_DETECTION=true
ENABLE_SCREENSHOT_ANALYSIS=true
MAX_ROWS_FOR_AI=100                   # Limit data sent to AI
MASK_PII=true                         # Auto-mask PII before AI

# Validation Thresholds
VALIDATION_ENABLED=true
NULL_THRESHOLD_PERCENT=20.0           # Max % nulls allowed
UNIQUENESS_THRESHOLD=95.0             # Min % unique for ID columns
VALIDATION_SAMPLE_SIZE=10000          # Rows to sample

# Anomaly Detection
ANOMALY_CONTAMINATION=0.05            # Expected % of anomalies
ANOMALY_N_ESTIMATORS=100              # Trees in Isolation Forest
ANOMALY_MAX_FEATURES=1.0              # Features per tree

# Screenshot Analysis
SCREENSHOT_MAX_SIZE_MB=10
SCREENSHOT_MIN_DIMENSION=400

# Logging
ENABLE_AUDIT_LOG=true
LOG_RETENTION_DAYS=30
```

---

## Best Practices for Users

### 1. **Review Before Accepting**
- Always review validation results before proceeding with data
- Check cleaning reports to understand what changed
- Verify PII masking caught all sensitive columns

### 2. **Start Conservative**
- Use default settings initially
- Enable aggressive cleaning only when needed
- Test with small datasets before full production runs

### 3. **Audit Regularly**
- Review audit logs (`logs/audit.jsonl`) periodically
- Check session summaries for unusual patterns
- Verify PII masking is working as expected

### 4. **Offline Mode for Sensitive Data**
- Set `AI_MODE=offline` when working with highly sensitive data
- Use deterministic methods (IQR, Z-score) instead of ML
- Avoid screenshot analysis if dashboards contain sensitive info

### 5. **Understand Limitations**
- PII detection is pattern-based, may miss edge cases
- Anomaly detection suggests outliers, doesn't explain causation
- Screenshot analysis provides UX guidance, not design decisions

---

## Privacy Guarantees

### What We DON'T Send to AI
- ❌ Raw data values (only sampled, masked summaries)
- ❌ PII (automatically detected and masked)
- ❌ Full datasets (limited to `MAX_ROWS_FOR_AI`)
- ❌ Validation failures with actual violating values
- ❌ Cleaning operations with before/after data

### What We DO Send to AI (when enabled)
- ✅ Sampled, PII-masked data summaries (≤100 rows)
- ✅ Column names and data types
- ✅ Aggregate statistics (counts, averages, no individuals)
- ✅ Validation report summaries (counts, not values)
- ✅ Dashboard screenshots (user-uploaded, requires consent)

### Data Retention
- **AI queries**: Not stored by this application (subject to Anthropic's policies)
- **Audit logs**: Retained locally for `LOG_RETENTION_DAYS` (default: 30 days)
- **Session data**: Cleared after `SESSION_TIMEOUT` (default: 24 hours)
- **Uploaded files**: Processed in-memory, not persisted to disk

---

## Compliance Considerations

### GDPR / CCPA
- **Right to erasure**: Audit logs can be deleted via cleanup functions
- **Data minimization**: Only minimal data sent to AI
- **Transparency**: Full audit trail of all operations
- **Consent**: Screenshot analysis requires explicit user upload

### HIPAA / Healthcare
- **Recommendation**: Use `AI_MODE=offline` for PHI
- **PII masking**: Auto-detects medical record numbers, patient IDs
- **Audit logs**: Track all access and operations

### Financial Services
- **PII detection**: Covers credit cards, account numbers, SSN
- **Deterministic validation**: Meet regulatory requirements for data quality
- **Audit trail**: Demonstrates due diligence

---

## Testing Responsible AI Features

### Test PII Masking
```python
import pandas as pd
from utils.privacy import mask_pii_dataframe

# Create test data with PII
df = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
    'revenue': [100, 200, 150]
})

# Mask PII
df_masked, report = mask_pii_dataframe(df, method='partial')

print(f"Detected PII columns: {report.detected_columns}")
# Output: ['email']

print(df_masked['email'].tolist())
# Output: ['jo************om', 'ja************om', 'bo************om']
```

### Test Data Minimization
```python
from utils.privacy import DataMinimizer

minimizer = DataMinimizer(max_rows=10)
df_mini, metadata = minimizer.minimize_for_ai(large_df)

print(f"Original: {metadata['original_shape']}, Minimized: {metadata['minimized_shape']}")
# Output: Original: (10000, 20), Minimized: (10, 20)
```

### Test Deterministic Validation
```python
from utils.validation import DataValidator

validator = DataValidator()
result = validator.validate_df(df)

assert result.total_checks > 0
assert result.passed in [True, False]  # Deterministic outcome
```

---

## Incident Response

### If PII Leaked to Logs
1. Stop the application immediately
2. Delete affected log files (`logs/*.log`, `logs/audit.jsonl`)
3. Review `PIISafeFormatter` configuration
4. Report incident per your organization's policy

### If Validation Produces Unexpected Results
1. Check configuration in `.env`
2. Review `ValidationResult.to_dict()` for details
3. Verify sample data matches expectations
4. Contact support with validation report (no actual data)

### If AI Provides Inaccurate Advice
1. Remember: AI explains, doesn't decide
2. Trust deterministic validation results over AI explanations
3. File issue on GitHub with anonymized example

---

## Support and Feedback

- **Documentation**: https://github.com/fpvjohnt/tableau-data-assistant
- **Issues**: https://github.com/fpvjohnt/tableau-data-assistant/issues
- **Questions**: Open a discussion on GitHub

---

## Version History

### v2.0.0 (Current)
- ✅ Responsible AI implementation
- ✅ Deterministic validation with Pandera
- ✅ Privacy-first PII masking
- ✅ Data minimization for AI queries
- ✅ PII-safe audit logging
- ✅ Offline mode support
- ✅ Multiple anomaly detection methods

### v1.0.0 (Legacy)
- Basic chatbot functionality
- Screenshot analysis
- Tableau workbook parsing

---

## License

This software is provided under the MIT License. See LICENSE file for details.

**Disclaimer**: This tool provides data quality suggestions and insights. Users are responsible for:
- Verifying all validation results
- Ensuring compliance with applicable regulations
- Protecting sensitive data
- Reviewing AI-generated recommendations before acting

**The software is provided "AS IS", without warranty of any kind.**
