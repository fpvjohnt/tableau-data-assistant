# Data Contract Copilot - Upstream Contract Auto-Generation

## 🎯 Overview

The **Data Contract Copilot** is an innovative feature that analyzes recurring data quality issues over time and automatically drafts formal **data contracts** to propose to upstream data providers. Instead of just reporting "this is broken," it generates complete, actionable contract documents that can be sent to upstream teams (ServiceNow, ETL pipelines, APIs, etc.).

### What Makes This Unusual?

Most data quality tools stop at **reporting problems**. The Data Contract Copilot goes further by:

1. **Analyzing historical patterns** of validation failures over time
2. **Generating formal contract proposals** with specific SLAs and requirements
3. **Creating JIRA ticket templates** with action items for upstream teams
4. **Using AI** (Claude) to generate natural language contract documents
5. **Proposing SLAs** based on observed data behavior
6. **Bridging consumers and producers** with concrete, actionable agreements

This shifts the conversation from reactive ("your data is broken") to proactive ("let's agree on these standards").

---

## 📊 How It Works

### Contract Generation Process

1. **Historical Analysis**: Analyzes validation results over N days to identify recurring issues
2. **Pattern Detection**: Groups similar failures (e.g., "customer_email missing 5-10% each week")
3. **Schema Inference**: Examines current data to infer types, constraints, and allowed values
4. **SLA Proposal**: Suggests quality thresholds based on observed behavior
5. **Contract Generation**: Creates formal Markdown/JSON contract documents
6. **JIRA Template**: Generates ticket template for upstream team engagement

### Data Contract Components

A complete data contract includes:

| Component | Description |
|-----------|-------------|
| **Field Specifications** | Data type, nullable, uniqueness, constraints |
| **Quality SLAs** | Uptime, freshness, completeness thresholds |
| **Allowed Values** | Enums, ranges, patterns |
| **Historical Issues** | What's been broken recently |
| **Governance** | Ownership, escalation path, review cycle |
| **Signature Section** | Producer/consumer sign-off |

---

## 🚀 Quick Start

### 1. Analyze Historical Issues

```python
from utils import DataContractAnalyzer, validate_for_tableau
import pandas as pd

# Collect validation results over time (simulated here)
historical_validation_results = []

for day in range(30):
    df = load_daily_data(day)  # Your data loading logic
    result, _ = validate_for_tableau(df)
    historical_validation_results.append({
        'timestamp': datetime.now() - timedelta(days=30-day),
        'result': result
    })

# Analyze patterns
analyzer = DataContractAnalyzer()
field_issues, recurring_issues, recommendations = analyzer.analyze_historical_issues(
    dataset_name='Sales Data',
    days=30,
    validation_results=historical_validation_results
)

# View recurring problems
print(f"Found {len(recurring_issues)} recurring issues:")
for issue in recurring_issues:
    print(f"  - {issue['field']}: {issue['issue_type']} ({issue['frequency']} occurrences)")
```

### 2. Generate Data Contract

```python
from utils import generate_data_contract

# Load current data
df = pd.read_csv('sales_data.csv')

# Generate contract
contract = generate_data_contract(
    df=df,
    dataset_name='Sales Data',
    upstream_system='ServiceNow CRM',
    historical_validation_results=historical_validation_results,
    days_history=30
)

# View contract
print(f"Contract: {contract.dataset_name}")
print(f"Upstream: {contract.upstream_system}")
print(f"Fields: {len(contract.fields)}")
print(f"Historical Issues: {len(contract.historical_issues)}")
```

### 3. Export Contract

```python
from utils import export_data_contract_proposal

# Export in multiple formats
paths = export_data_contract_proposal(contract, include_jira=True)

print(f"Markdown contract: {paths['markdown']}")
print(f"JSON contract: {paths['json']}")
print(f"JIRA ticket: {paths['jira']}")
```

---

## 📋 Contract Format Examples

### Markdown Contract (Human-Readable)

```markdown
# Data Contract: Sales Data
**Provider**: ServiceNow CRM
**Consumer**: Tableau Analytics
**Effective Date**: 2025-01-13

## 1. Overview
This contract defines the data quality standards and SLAs for Sales Data...

## 2. Service Level Agreements (SLAs)
- **Uptime**: 99.9%
- **Freshness**: Data delivered within 24 hours
- **Completeness**: ≥95% of required fields populated

## 3. Field Specifications

### customer_id
- **Type**: STRING
- **Required**: Yes
- **Nullable**: No
- **Unique**: Yes
- **SLA Requirements**:
  - Must be unique across all records
  - Format: CUST followed by 4 digits (e.g., CUST0001)
- **Historical Issues**:
  - Duplicate values found on 2025-01-10

### customer_email
- **Type**: STRING
- **Required**: Yes
- **Nullable**: Yes
- **Max Null %**: 5.0%
- **SLA Requirements**:
  - Must contain @ symbol
  - Must follow email format (RFC 5322)
- **Historical Issues**:
  - High null rate (15-20%) observed over past 30 days
  - Invalid format detected on 2025-01-08

...
```

### JSON Contract (Machine-Readable)

```json
{
  "dataset_name": "Sales Data",
  "upstream_system": "ServiceNow CRM",
  "downstream_system": "Tableau Analytics",
  "effective_date": "2025-01-13T10:30:00",
  "sla_uptime": 99.9,
  "sla_freshness_hours": 24,
  "quality_requirements": {
    "completeness_threshold": 95.0,
    "uniqueness_threshold": 95.0,
    "max_null_percentage": 5.0
  },
  "fields": [
    {
      "field_name": "customer_id",
      "data_type": "STRING",
      "required": true,
      "nullable": false,
      "unique": true,
      "sla_requirements": [
        "Must be unique across all records",
        "Format: CUST followed by 4 digits"
      ],
      "observed_issues": [
        "Duplicate values found on 2025-01-10"
      ]
    }
  ],
  "historical_issues": [...]
}
```

### JIRA Ticket Template

```markdown
**Summary**: [DATA CONTRACT] Sales Data Quality Issues - Action Required

**Description**:
The downstream Tableau Analytics team has identified recurring data quality issues
with Sales Data from ServiceNow CRM over the past 30 days.

We've drafted a formal data contract proposal to establish quality standards and SLAs.

**Key Issues**:
- customer_email: High null rate (15-20%) - exceeds 5% threshold
- phone: Duplicate values detected (uniqueness: 85%, target: 95%)
- revenue: Outliers detected (10% of records)

**Proposed Actions**:
1. Review attached data contract proposal (see contract_Sales_Data.md)
2. Validate field specifications match upstream schema
3. Implement data quality checks at source
4. Agree on SLAs (99.9% uptime, 24h freshness)
5. Schedule bi-weekly review meetings

**Attachments**:
- contract_Sales_Data.md (formal contract)
- contract_Sales_Data.json (machine-readable spec)

**Priority**: High
**Labels**: data-quality, data-contract, servicenow, tableau
**Assignee**: [ServiceNow Team Lead]
```

---

## 🎨 Use Cases

### Use Case 1: CRM → Analytics Pipeline

**Scenario**: Your Tableau dashboards depend on ServiceNow CRM data, but customer_email is missing 20% of the time.

**Solution**:
1. Run historical analysis: `analyzer.analyze_historical_issues()`
2. Generate contract: `generate_data_contract(df, upstream_system='ServiceNow CRM')`
3. Export JIRA ticket: `export_data_contract_proposal(contract, include_jira=True)`
4. Send to ServiceNow team with formal proposal

**Result**: ServiceNow team agrees to enforce email validation at input time, reducing nulls to <5%.

---

### Use Case 2: API → Data Lake

**Scenario**: Third-party API provides transaction data, but timestamps are inconsistent (UTC vs. local time).

**Solution**:
1. Analyze timestamp validation failures over 30 days
2. Generate contract specifying: "All timestamps must be ISO 8601 UTC format"
3. Include examples in contract: `2025-01-13T10:30:00Z`
4. Propose SLA: 100% of timestamps must be parseable

**Result**: API provider updates documentation and fixes timestamp serialization.

---

### Use Case 3: Database ETL → Tableau

**Scenario**: Nightly ETL from Oracle to Tableau, but order_id has duplicates 3x per week.

**Solution**:
1. Analyze historical uniqueness violations
2. Generate contract with requirement: "order_id must be unique (100%)"
3. Propose monitoring: Alert if duplicate rate >0.1%
4. Include historical evidence: "Duplicates detected on Jan 5, Jan 8, Jan 12"

**Result**: ETL team adds deduplication step and unique constraint check.

---

### Use Case 4: Manual Data Entry → BI

**Scenario**: Sales team manually enters data into Excel, leading to inconsistent date formats.

**Solution**:
1. Detect date parsing failures (e.g., "1/5/25" vs. "2025-01-05")
2. Generate contract specifying: "All dates in YYYY-MM-DD format"
3. Include allowed values: `{pattern: "\\d{4}-\\d{2}-\\d{2}"}`
4. Attach Excel template with data validation

**Result**: Sales team uses new template, reducing date errors by 95%.

---

## 💡 Advanced Usage

### 1. Custom SLA Thresholds

```python
from utils import DataContractAnalyzer

analyzer = DataContractAnalyzer()

# Override default thresholds
contract = analyzer.generate_contract_from_schema(
    df,
    dataset_name='Critical Sales Data',
    upstream_system='Salesforce',
    historical_analysis=historical_analysis
)

# Customize SLAs
contract.sla_uptime = 99.99  # Five nines for critical data
contract.sla_freshness_hours = 1  # Real-time requirement
contract.quality_requirements['completeness_threshold'] = 99.0  # Stricter
```

### 2. AI-Enhanced Contract Generation

```python
from utils import DataContractGenerator
import anthropic

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

generator = DataContractGenerator(client=client)

# Generate contract with AI-enhanced descriptions
contract_md = generator.generate_markdown(contract, use_ai=True)

# AI adds:
# - Natural language explanations of each field
# - Business context for requirements
# - Examples of valid/invalid values
```

### 3. Historical Trend Visualization

```python
import matplotlib.pyplot as plt

# Analyze 90-day history
field_issues, _, _ = analyzer.analyze_historical_issues(
    dataset_name='Sales Data',
    days=90,
    validation_results=validation_results_90d
)

# Plot null rate over time for customer_email
customer_email_issues = field_issues['customer_email']
plt.plot(customer_email_issues['timestamps'], customer_email_issues['null_rates'])
plt.title('customer_email Null Rate - Last 90 Days')
plt.xlabel('Date')
plt.ylabel('Null %')
plt.axhline(y=5.0, color='r', linestyle='--', label='SLA Threshold (5%)')
plt.legend()
plt.savefig('exports/customer_email_trend.png')
```

### 4. Multi-System Contracts

```python
# Generate contracts for multiple upstream systems
upstream_systems = [
    'ServiceNow CRM',
    'Salesforce Marketing',
    'Stripe Payments',
    'Google Analytics'
]

contracts = []
for system in upstream_systems:
    df = load_data_from(system)
    contract = generate_data_contract(
        df,
        dataset_name=f'{system} Data',
        upstream_system=system,
        historical_validation_results=get_history_for(system),
        days_history=30
    )
    contracts.append(contract)

# Export all
for contract in contracts:
    export_data_contract_proposal(contract, include_jira=True)
```

---

## 📊 Integration Patterns

### Pattern 1: Weekly Contract Review

**Automation**:
```python
import schedule

def weekly_contract_review():
    # Analyze last 7 days
    contract = generate_data_contract(df, days_history=7)

    # Only create JIRA if new issues detected
    if len(contract.historical_issues) > 0:
        export_data_contract_proposal(contract, include_jira=True)
        send_email_to_upstream_team(contract)

# Run every Monday at 9 AM
schedule.every().monday.at("09:00").do(weekly_contract_review)
```

### Pattern 2: Contract Versioning

**Track Contract Changes**:
```python
from utils import TrustScoreStore

store = TrustScoreStore()  # Reuse existing SQLite DB

# Save contract version
store.save_contract_version(
    dataset_name='Sales Data',
    version='2.1.0',
    contract_json=contract.to_dict(),
    changes='Added customer_email format requirement'
)

# Retrieve history
versions = store.get_contract_versions('Sales Data')
```

### Pattern 3: Upstream System Integration

**Push to JIRA API**:
```python
from jira import JIRA

# Generate JIRA ticket
jira_text = generator.generate_jira_ticket(contract)

# Create via API
jira = JIRA(server='https://company.atlassian.net', basic_auth=('user', 'token'))
issue = jira.create_issue(
    project='DATA',
    summary=f'[DATA CONTRACT] {contract.dataset_name}',
    description=jira_text,
    issuetype={'name': 'Task'},
    labels=['data-quality', 'data-contract']
)

print(f"Created JIRA ticket: {issue.key}")
```

### Pattern 4: Contract Negotiation Workflow

**Stages**:
1. **Propose**: Generate contract, send to upstream team
2. **Review**: Upstream team reviews and suggests changes
3. **Negotiate**: Iterate on SLAs and requirements
4. **Approve**: Both teams sign off
5. **Monitor**: Track compliance via trust scores

**Implementation**:
```python
# Stage 1: Propose
contract = generate_data_contract(df, upstream_system='ServiceNow')
contract.status = 'PROPOSED'
export_data_contract_proposal(contract)

# Stage 2: Review (manual)
# Upstream team reviews and sends feedback

# Stage 3: Negotiate
contract.sla_uptime = 99.5  # Lowered from 99.9 after discussion
contract.quality_requirements['completeness_threshold'] = 90.0  # Relaxed
contract.status = 'NEGOTIATING'

# Stage 4: Approve
contract.status = 'APPROVED'
contract.effective_date = datetime.now()
contract.producer_signature = 'John Doe, ServiceNow Lead'
contract.consumer_signature = 'Jane Smith, Analytics Lead'

# Stage 5: Monitor
# Use trust scores to track compliance
trust_report = calculate_trust_scores(df)
if trust_report.overall_trust_score < 90.0:
    send_alert('Contract SLA violated!')
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Data Contract Settings
DATA_CONTRACT_ENABLED=true
DATA_CONTRACT_OUTPUT_DIR=exports/contracts
DATA_CONTRACT_MIN_HISTORY_DAYS=7
DATA_CONTRACT_DEFAULT_SLA_UPTIME=99.9
DATA_CONTRACT_DEFAULT_FRESHNESS_HOURS=24

# AI Enhancement (optional)
ANTHROPIC_API_KEY=sk-ant-api03-...
USE_AI_FOR_CONTRACTS=true  # Add natural language descriptions
```

### Settings (config/settings.py)

```python
# Default contract quality thresholds
CONTRACT_DEFAULT_QUALITY = {
    'completeness_threshold': 95.0,
    'uniqueness_threshold': 95.0,
    'max_null_percentage': 5.0,
    'max_anomaly_percentage': 10.0
}

# Contract metadata
CONTRACT_REVIEW_CYCLE_DAYS = 90  # Review every 3 months
CONTRACT_GOVERNANCE_OWNER = 'Data Governance Team'
CONTRACT_ESCALATION_EMAIL = 'data-escalation@company.com'
```

---

## 🧪 Testing

```python
import pytest
from utils import DataContractAnalyzer, generate_data_contract
import pandas as pd

def test_contract_generation():
    # Perfect data
    df = pd.DataFrame({
        'id': range(100),
        'email': [f'user{i}@example.com' for i in range(100)]
    })

    contract = generate_data_contract(
        df,
        dataset_name='Test Data',
        upstream_system='Test System',
        historical_validation_results=[],
        days_history=7
    )

    assert contract.dataset_name == 'Test Data'
    assert len(contract.fields) == 2
    assert contract.fields[0].field_name in ['id', 'email']

def test_historical_issue_detection():
    analyzer = DataContractAnalyzer()

    # Simulate recurring null issue
    validation_results = []
    for i in range(30):
        result = ValidationResult(
            passed=False,
            passed_checks=5,
            failed_checks=1,
            warnings=[],
            errors=[{'field': 'email', 'issue': 'high_null_rate', 'value': 15.0}]
        )
        validation_results.append({
            'timestamp': datetime.now() - timedelta(days=30-i),
            'result': result
        })

    field_issues, recurring, _ = analyzer.analyze_historical_issues(
        dataset_name='Test',
        days=30,
        validation_results=validation_results
    )

    assert 'email' in field_issues
    assert len(recurring) > 0
    assert recurring[0]['field'] == 'email'

def test_jira_ticket_generation():
    from utils import DataContractGenerator

    contract = DataContract(
        dataset_name='Sales Data',
        upstream_system='ServiceNow',
        fields=[],
        quality_requirements={},
        historical_issues=[{'field': 'email', 'issue': 'high_null_rate'}]
    )

    generator = DataContractGenerator()
    jira_text = generator.generate_jira_ticket(contract)

    assert 'DATA CONTRACT' in jira_text
    assert 'ServiceNow' in jira_text
    assert 'email' in jira_text
```

---

## 📖 Best Practices

### 1. **Start with Recent History**
Don't analyze too far back initially. Start with 7-30 days to identify acute issues.

### 2. **Iterate on Contracts**
First draft is never final. Expect negotiation with upstream teams.

### 3. **Be Specific**
Instead of "email must be valid," specify: "Must match regex `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$`"

### 4. **Include Examples**
Show valid and invalid examples in contracts:
```
Valid: "john.doe@example.com"
Invalid: "john@", "example.com", null
```

### 5. **Document Historical Context**
Explain why requirements exist:
```
"customer_email must be non-null because:
- 20% null rate observed Jan 1-15, 2025
- Blocked dashboard launch due to missing contact data
- Business requirement: all customers must be contactable"
```

### 6. **Set Realistic SLAs**
Don't propose 100% uptime unless truly critical. Start conservative, tighten over time.

### 7. **Automate Monitoring**
Use trust scores to automatically detect contract violations:
```python
if trust_report.overall_trust_score < contract.quality_requirements['completeness_threshold']:
    create_jira_incident('Contract SLA violation')
```

### 8. **Review Regularly**
Schedule quarterly contract reviews to update requirements as business needs evolve.

---

## 🚨 Troubleshooting

### Q: No historical issues detected

**A:** Ensure validation results are being passed correctly:
```python
# Make sure results are from actual validation runs
validation_results = [
    {'timestamp': ..., 'result': validate_for_tableau(df)[0]}
]
```

### Q: Contract too strict/loose

**A:** Override default thresholds:
```python
contract.quality_requirements['completeness_threshold'] = 85.0  # More lenient
contract.sla_uptime = 99.99  # Stricter
```

### Q: JIRA ticket not created

**A:** Check output path:
```python
paths = export_data_contract_proposal(contract, include_jira=True)
print(f"JIRA template saved to: {paths['jira']}")
```

### Q: AI generation fails

**A:** Verify API key:
```python
import os
print(os.getenv('ANTHROPIC_API_KEY'))  # Should not be None
```

Or disable AI enhancement:
```python
generator.generate_markdown(contract, use_ai=False)
```

---

## 📚 API Reference

### Core Functions

#### `generate_data_contract()`
```python
def generate_data_contract(
    df: pd.DataFrame,
    dataset_name: str,
    upstream_system: str,
    historical_validation_results: List[Dict],
    days_history: int = 30
) -> DataContract
```

**Parameters**:
- `df`: Current dataset to analyze
- `dataset_name`: Name of dataset (e.g., "Sales Data")
- `upstream_system`: Source system name (e.g., "ServiceNow CRM")
- `historical_validation_results`: List of `{'timestamp': datetime, 'result': ValidationResult}`
- `days_history`: How many days of history to analyze

**Returns**: `DataContract` object with all specifications

---

#### `export_data_contract_proposal()`
```python
def export_data_contract_proposal(
    contract: DataContract,
    include_jira: bool = True
) -> Dict[str, str]
```

**Parameters**:
- `contract`: DataContract object to export
- `include_jira`: Whether to generate JIRA ticket template

**Returns**: Dictionary with paths to exported files:
```python
{
    'markdown': 'exports/contracts/contract_Sales_Data.md',
    'json': 'exports/contracts/contract_Sales_Data.json',
    'jira': 'exports/contracts/jira_ticket_Sales_Data.md'  # if include_jira=True
}
```

---

### Classes

#### `DataContractAnalyzer`
```python
class DataContractAnalyzer:
    def analyze_historical_issues(
        self,
        dataset_name: str,
        days: int,
        validation_results: List[Dict]
    ) -> Tuple[Dict, List[Dict], List[str]]
```

**Returns**:
- `field_issues`: Dict mapping field names to issue details
- `recurring_issues`: List of issues that occurred multiple times
- `recommendations`: List of suggested actions

---

#### `DataContractGenerator`
```python
class DataContractGenerator:
    def __init__(self, client: Optional[anthropic.Anthropic] = None):
        """
        Args:
            client: Optional Claude API client for AI-enhanced generation
        """

    def generate_markdown(self, contract: DataContract, use_ai: bool = False) -> str
    def generate_json(self, contract: DataContract) -> str
    def generate_jira_ticket(self, contract: DataContract) -> str
    def export_contract(self, contract: DataContract, format: str, output_path: str)
```

---

## 🎁 Example Workflow

```python
# Complete end-to-end example
from utils import (
    validate_for_tableau,
    generate_data_contract,
    export_data_contract_proposal,
    calculate_trust_scores
)
import pandas as pd
from datetime import datetime, timedelta

# 1. Collect historical validation results (30 days)
historical_results = []
for day in range(30):
    # Load data for each day
    df_daily = pd.read_csv(f'data/sales_2025-01-{day+1:02d}.csv')

    # Validate
    result, _ = validate_for_tableau(
        df_daily,
        required_columns=['order_id', 'customer_id', 'revenue'],
        unique_columns=['order_id']
    )

    historical_results.append({
        'timestamp': datetime.now() - timedelta(days=30-day),
        'result': result
    })

# 2. Load current data
df_current = pd.read_csv('data/sales_latest.csv')

# 3. Generate data contract
contract = generate_data_contract(
    df=df_current,
    dataset_name='Sales Data',
    upstream_system='ServiceNow CRM',
    historical_validation_results=historical_results,
    days_history=30
)

# 4. View contract summary
print(f"Contract: {contract.dataset_name}")
print(f"Upstream: {contract.upstream_system}")
print(f"Fields: {len(contract.fields)}")
print(f"Historical Issues: {len(contract.historical_issues)}")
print(f"Proposed SLA Uptime: {contract.sla_uptime}%")

# 5. Export in multiple formats
paths = export_data_contract_proposal(contract, include_jira=True)
print(f"\nContract exported to:")
print(f"  - Markdown: {paths['markdown']}")
print(f"  - JSON: {paths['json']}")
print(f"  - JIRA: {paths['jira']}")

# 6. Monitor compliance with trust scores
trust_report = calculate_trust_scores(
    df_current,
    dataset_name='Sales Data'
)

print(f"\nCurrent Trust Score: {trust_report.overall_trust_score:.1f}/100")

# 7. Alert if contract violated
if trust_report.overall_trust_score < contract.quality_requirements['completeness_threshold']:
    print("⚠️  WARNING: Contract SLA may be violated!")
    print(f"Trust score ({trust_report.overall_trust_score:.1f}) below threshold ({contract.quality_requirements['completeness_threshold']})")
```

---

## 🏆 Benefits

| Benefit | Description |
|---------|-------------|
| **Proactive** | Shifts from "your data is broken" to "let's agree on standards" |
| **Actionable** | Provides concrete requirements, not vague complaints |
| **Historical** | Uses real data to justify requirements |
| **Collaborative** | Creates basis for producer/consumer negotiation |
| **Automated** | Reduces manual contract writing from hours to minutes |
| **Versioned** | Tracks changes over time |
| **Enforceable** | Pairs with trust scores for automated monitoring |

---

## 📞 Support

- **Source Code**: `utils/data_contract.py`
- **Examples**: `examples/data_contract_example.py`
- **API Reference**: See module docstrings
- **Related Features**: Trust Scoring ([TRUST_HEATMAP_GUIDE.md](TRUST_HEATMAP_GUIDE.md))

---

**🎉 You now have an automated data contract negotiation system!**

This feature bridges the gap between data consumers (your Tableau dashboards) and data producers (upstream systems). Use it to formalize expectations, reduce firefighting, and build trust between teams.

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-01-13
