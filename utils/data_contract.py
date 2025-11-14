"""
Data Contract Copilot
Auto-generates upstream data contracts based on recurring validation issues
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import json
import os

from config.settings import EXPORTS_DIR, is_ai_enabled


@dataclass
class FieldContract:
    """Contract specification for a single field"""
    field_name: str
    data_type: str
    required: bool = True
    nullable: bool = False
    max_null_percentage: float = 1.0  # Default: < 1% nulls
    unique: bool = False
    min_uniqueness_percentage: Optional[float] = None
    allowed_values: Optional[List[str]] = None
    value_pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    max_length: Optional[int] = None
    description: str = ""
    business_purpose: str = ""
    sla_requirements: List[str] = field(default_factory=list)
    observed_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'field_name': self.field_name,
            'data_type': self.data_type,
            'required': self.required,
            'nullable': self.nullable,
            'max_null_percentage': self.max_null_percentage,
            'unique': self.unique,
            'min_uniqueness_percentage': self.min_uniqueness_percentage,
            'allowed_values': self.allowed_values,
            'value_pattern': self.value_pattern,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'max_length': self.max_length,
            'description': self.description,
            'business_purpose': self.business_purpose,
            'sla_requirements': self.sla_requirements,
            'observed_issues': self.observed_issues
        }


@dataclass
class DataContract:
    """Complete data contract for a dataset"""
    dataset_name: str
    upstream_system: str
    downstream_system: str = "Tableau Analytics"
    fields: List[FieldContract] = field(default_factory=list)
    version: str = "1.0"
    effective_date: datetime = field(default_factory=datetime.now)
    owner_upstream: str = "Upstream Data Team"
    owner_downstream: str = "Analytics Team"
    update_frequency: str = "Daily"
    retention_period: str = "90 days"
    contact_upstream: str = ""
    contact_downstream: str = ""
    sla_uptime: float = 99.9
    sla_freshness_hours: int = 24
    quality_requirements: Dict[str, Any] = field(default_factory=dict)
    governance_policies: List[str] = field(default_factory=list)
    historical_issues: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'dataset_name': self.dataset_name,
            'upstream_system': self.upstream_system,
            'downstream_system': self.downstream_system,
            'fields': [f.to_dict() for f in self.fields],
            'version': self.version,
            'effective_date': self.effective_date.isoformat(),
            'owner_upstream': self.owner_upstream,
            'owner_downstream': self.owner_downstream,
            'update_frequency': self.update_frequency,
            'retention_period': self.retention_period,
            'contact_upstream': self.contact_upstream,
            'contact_downstream': self.contact_downstream,
            'sla_uptime': self.sla_uptime,
            'sla_freshness_hours': self.sla_freshness_hours,
            'quality_requirements': self.quality_requirements,
            'governance_policies': self.governance_policies,
            'historical_issues': self.historical_issues
        }


class DataContractAnalyzer:
    """Analyzes historical validation results to identify contract requirements"""

    def __init__(self, audit_logger=None):
        """
        Initialize contract analyzer

        Args:
            audit_logger: Optional AuditLogger instance for accessing historical data
        """
        self.audit_logger = audit_logger

    def analyze_historical_issues(
        self,
        dataset_name: str,
        days: int = 30,
        validation_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze historical validation issues to identify patterns

        Args:
            dataset_name: Name of dataset
            days: Number of days of history to analyze
            validation_results: Optional list of validation results (if not using audit logger)

        Returns:
            Dictionary with issue patterns and statistics
        """
        # If validation results provided, use those; otherwise get from audit log
        if validation_results is None and self.audit_logger:
            # Get historical validation logs
            validation_results = self._get_validation_history(dataset_name, days)

        if not validation_results:
            return {
                'total_runs': 0,
                'field_issues': {},
                'recurring_issues': [],
                'recommendations': []
            }

        # Aggregate issues by field
        field_issues = {}
        total_runs = len(validation_results)

        for result in validation_results:
            # Parse errors
            errors = result.get('errors', [])
            warnings = result.get('warnings', [])

            for error in errors:
                field = error.get('column') or error.get('field_name', 'unknown')
                issue_type = error.get('check', 'unknown')
                message = error.get('message', '')

                if field not in field_issues:
                    field_issues[field] = {
                        'error_count': 0,
                        'warning_count': 0,
                        'issue_types': {},
                        'messages': []
                    }

                field_issues[field]['error_count'] += 1
                field_issues[field]['issue_types'][issue_type] = field_issues[field]['issue_types'].get(issue_type, 0) + 1
                if message and message not in field_issues[field]['messages']:
                    field_issues[field]['messages'].append(message)

            for warning in warnings:
                field = warning.get('column') or warning.get('field_name', 'unknown')
                issue_type = warning.get('check', 'unknown')

                if field not in field_issues:
                    field_issues[field] = {
                        'error_count': 0,
                        'warning_count': 0,
                        'issue_types': {},
                        'messages': []
                    }

                field_issues[field]['warning_count'] += 1
                field_issues[field]['issue_types'][issue_type] = field_issues[field]['issue_types'].get(issue_type, 0) + 1

        # Identify recurring issues (present in >25% of runs)
        recurring_threshold = total_runs * 0.25
        recurring_issues = []

        for field, issues in field_issues.items():
            if issues['error_count'] >= recurring_threshold:
                recurring_issues.append({
                    'field': field,
                    'frequency': f"{(issues['error_count'] / total_runs) * 100:.1f}%",
                    'issue_types': issues['issue_types'],
                    'messages': issues['messages']
                })

        # Generate recommendations
        recommendations = self._generate_recommendations(field_issues, total_runs)

        return {
            'total_runs': total_runs,
            'field_issues': field_issues,
            'recurring_issues': recurring_issues,
            'recommendations': recommendations
        }

    def _get_validation_history(self, dataset_name: str, days: int) -> List[Dict[str, Any]]:
        """Get validation history from audit logger"""
        if not self.audit_logger:
            return []

        # Get logs from audit logger
        logs = self.audit_logger.get_logs(
            session_id=None,
            action='validate',
            start_time=datetime.now() - timedelta(days=days)
        )

        # Extract validation results
        results = []
        for log in logs:
            details = log.get('details', {})
            if details:
                results.append(details)

        return results

    def _generate_recommendations(
        self,
        field_issues: Dict[str, Any],
        total_runs: int
    ) -> List[str]:
        """Generate contract recommendations based on issues"""
        recommendations = []

        for field, issues in field_issues.items():
            # Null issues
            if 'null_threshold' in issues['issue_types']:
                frequency = (issues['issue_types']['null_threshold'] / total_runs) * 100
                if frequency > 25:
                    recommendations.append(
                        f"Field '{field}': Reduce null percentage (observed in {frequency:.0f}% of runs)"
                    )

            # Type issues
            if 'data_type' in issues['issue_types']:
                recommendations.append(
                    f"Field '{field}': Enforce consistent data type"
                )

            # Uniqueness issues
            if 'uniqueness' in issues['issue_types']:
                recommendations.append(
                    f"Field '{field}': Improve uniqueness for ID field"
                )

            # Range violations
            if 'value_range' in issues['issue_types']:
                recommendations.append(
                    f"Field '{field}': Ensure values stay within expected range"
                )

        return recommendations

    def generate_contract_from_schema(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        upstream_system: str,
        historical_analysis: Optional[Dict[str, Any]] = None
    ) -> DataContract:
        """
        Generate data contract from DataFrame schema and historical issues

        Args:
            df: DataFrame to analyze
            dataset_name: Name of dataset
            upstream_system: Name of upstream system
            historical_analysis: Optional historical issue analysis

        Returns:
            DataContract object
        """
        contract = DataContract(
            dataset_name=dataset_name,
            upstream_system=upstream_system
        )

        # Analyze each field
        for col in df.columns:
            field_contract = self._create_field_contract(df[col], col, historical_analysis)
            contract.fields.append(field_contract)

        # Set quality requirements
        contract.quality_requirements = {
            'overall_completeness': 95.0,
            'overall_validity': 95.0,
            'max_duplicate_percentage': 5.0,
            'freshness_sla_hours': 24
        }

        # Add governance policies
        contract.governance_policies = [
            "Data must be validated before downstream consumption",
            "Schema changes must be communicated 30 days in advance",
            "PII must be masked or encrypted",
            "Data quality issues must be resolved within 48 hours"
        ]

        # Add historical issues if provided
        if historical_analysis and historical_analysis.get('recurring_issues'):
            contract.historical_issues = historical_analysis['recurring_issues']

        return contract

    def _create_field_contract(
        self,
        series: pd.Series,
        field_name: str,
        historical_analysis: Optional[Dict[str, Any]]
    ) -> FieldContract:
        """Create field contract from series analysis"""
        # Determine data type
        dtype = str(series.dtype)
        if pd.api.types.is_integer_dtype(series):
            data_type = "integer"
        elif pd.api.types.is_float_dtype(series):
            data_type = "float"
        elif pd.api.types.is_datetime64_any_dtype(series):
            data_type = "datetime"
        elif pd.api.types.is_bool_dtype(series):
            data_type = "boolean"
        else:
            data_type = "string"

        # Calculate null percentage
        null_pct = (series.isnull().sum() / len(series)) * 100

        # Check uniqueness
        unique_pct = (series.nunique() / len(series)) * 100
        is_unique = unique_pct > 95

        # Get value constraints
        allowed_values = None
        value_pattern = None
        min_value = None
        max_value = None
        max_length = None

        if data_type == "string":
            # If low cardinality, list allowed values
            if unique_pct < 10:
                allowed_values = series.dropna().unique().tolist()[:20]  # Limit to 20
            max_length = int(series.astype(str).str.len().max()) if not series.isnull().all() else None

        elif data_type in ["integer", "float"]:
            if not series.isnull().all():
                min_value = float(series.min())
                max_value = float(series.max())

        # Get historical issues for this field
        observed_issues = []
        if historical_analysis and historical_analysis.get('field_issues', {}).get(field_name):
            field_issues = historical_analysis['field_issues'][field_name]
            for issue_type, count in field_issues.get('issue_types', {}).items():
                observed_issues.append(f"{issue_type}: occurred {count} times")

        # Create field contract
        field_contract = FieldContract(
            field_name=field_name,
            data_type=data_type,
            required=True,  # Assume required unless proven otherwise
            nullable=null_pct > 0,
            max_null_percentage=max(1.0, null_pct * 1.2) if null_pct > 0 else 1.0,  # 20% buffer
            unique=is_unique,
            min_uniqueness_percentage=95.0 if is_unique else None,
            allowed_values=allowed_values,
            min_value=min_value,
            max_value=max_value,
            max_length=max_length,
            observed_issues=observed_issues
        )

        # Add SLA requirements based on issues
        if observed_issues:
            field_contract.sla_requirements.append("Must resolve quality issues within 48 hours")
        if null_pct > 10:
            field_contract.sla_requirements.append(f"Reduce null percentage from {null_pct:.1f}% to <{field_contract.max_null_percentage:.1f}%")

        return field_contract


class DataContractGenerator:
    """Generates human-readable data contract documents"""

    def __init__(self, use_ai: bool = True):
        """
        Initialize contract generator

        Args:
            use_ai: Whether to use AI for enhanced contract generation
        """
        self.use_ai = use_ai and is_ai_enabled()

    def generate_markdown(self, contract: DataContract) -> str:
        """Generate Markdown data contract document"""
        lines = [
            f"# Data Contract: {contract.dataset_name}",
            "",
            f"**Version:** {contract.version}",
            f"**Effective Date:** {contract.effective_date.strftime('%Y-%m-%d')}",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "---",
            "",
            "## Overview",
            "",
            f"This contract defines the data quality expectations and SLAs between **{contract.upstream_system}** (data producer) and **{contract.downstream_system}** (data consumer) for the `{contract.dataset_name}` dataset.",
            "",
            "## Ownership",
            "",
            f"- **Upstream Owner:** {contract.owner_upstream}",
            f"- **Downstream Owner:** {contract.owner_downstream}",
            f"- **Upstream Contact:** {contract.contact_upstream or 'TBD'}",
            f"- **Downstream Contact:** {contract.contact_downstream or 'TBD'}",
            "",
            "## Service Level Agreements (SLAs)",
            "",
            f"- **Update Frequency:** {contract.update_frequency}",
            f"- **Uptime:** {contract.sla_uptime}%",
            f"- **Freshness:** Data must be updated within {contract.sla_freshness_hours} hours",
            f"- **Retention:** {contract.retention_period}",
            "",
            "## Quality Requirements",
            ""
        ]

        # Add quality requirements
        for key, value in contract.quality_requirements.items():
            lines.append(f"- **{key.replace('_', ' ').title()}:** {value}%")

        lines.extend([
            "",
            "## Field Specifications",
            "",
            "| Field Name | Type | Required | Nullable | Constraints |",
            "|------------|------|----------|----------|-------------|"
        ])

        # Add field specifications
        for field in contract.fields:
            constraints = []
            if field.max_null_percentage:
                constraints.append(f"Nulls <{field.max_null_percentage:.1f}%")
            if field.unique:
                constraints.append("Unique ID")
            if field.allowed_values:
                constraints.append(f"Values: {', '.join(map(str, field.allowed_values[:5]))}")
            if field.min_value is not None and field.max_value is not None:
                constraints.append(f"Range: {field.min_value:.0f}-{field.max_value:.0f}")
            if field.max_length:
                constraints.append(f"Max length: {field.max_length}")

            constraint_str = '; '.join(constraints) if constraints else "None"

            lines.append(
                f"| {field.field_name} | {field.data_type} | {'Yes' if field.required else 'No'} | "
                f"{'Yes' if field.nullable else 'No'} | {constraint_str} |"
            )

        # Add detailed field descriptions
        lines.extend([
            "",
            "## Detailed Field Requirements",
            ""
        ])

        for field in contract.fields:
            lines.extend([
                f"### {field.field_name}",
                "",
                f"- **Type:** `{field.data_type}`",
                f"- **Required:** {'Yes' if field.required else 'No'}",
                f"- **Nullable:** {'Yes' if field.nullable else 'No'} (max {field.max_null_percentage:.1f}% nulls)",
                ""
            ])

            if field.description:
                lines.extend([
                    f"**Description:** {field.description}",
                    ""
                ])

            if field.allowed_values:
                lines.extend([
                    "**Allowed Values:**",
                    ""
                ])
                for val in field.allowed_values[:10]:
                    lines.append(f"- `{val}`")
                if len(field.allowed_values) > 10:
                    lines.append(f"- ... and {len(field.allowed_values) - 10} more")
                lines.append("")

            if field.min_value is not None or field.max_value is not None:
                lines.extend([
                    "**Value Range:**",
                    f"- Minimum: {field.min_value}",
                    f"- Maximum: {field.max_value}",
                    ""
                ])

            if field.sla_requirements:
                lines.extend([
                    "**SLA Requirements:**",
                    ""
                ])
                for sla in field.sla_requirements:
                    lines.append(f"- {sla}")
                lines.append("")

            if field.observed_issues:
                lines.extend([
                    "**  Historical Issues:**",
                    ""
                ])
                for issue in field.observed_issues:
                    lines.append(f"- {issue}")
                lines.append("")

        # Add governance policies
        if contract.governance_policies:
            lines.extend([
                "## Governance Policies",
                ""
            ])
            for policy in contract.governance_policies:
                lines.append(f"1. {policy}")
            lines.append("")

        # Add historical issues summary
        if contract.historical_issues:
            lines.extend([
                "## Recurring Quality Issues",
                "",
                f"Based on analysis of the last {len(contract.historical_issues)} validation runs:",
                ""
            ])
            for issue in contract.historical_issues:
                field = issue['field']
                frequency = issue['frequency']
                messages = issue.get('messages', [])

                lines.append(f"### Field: `{field}` (Failed {frequency} of runs)")
                lines.append("")
                for msg in messages[:3]:
                    lines.append(f"- {msg}")
                lines.append("")

        # Add acceptance criteria
        lines.extend([
            "## Acceptance Criteria",
            "",
            "This data contract is considered met when:",
            "",
            "1. All required fields are present in every data delivery",
            "2. Null percentages are within specified limits for all fields",
            "3. Data types match specifications",
            "4. Value constraints are respected (ranges, allowed values, patterns)",
            "5. Data freshness meets SLA requirements",
            "6. Overall data quality score e 95%",
            "",
            "## Monitoring & Reporting",
            "",
            "- **Validation Frequency:** Every data delivery",
            "- **Quality Dashboard:** [Link to Tableau dashboard]",
            "- **Alert Threshold:** Any SLA breach triggers immediate notification",
            "- **Monthly Review:** Joint review meeting to assess contract adherence",
            "",
            "## Change Management",
            "",
            "1. **Schema Changes:** 30 days advance notice required",
            "2. **New Fields:** Communicate via data governance committee",
            "3. **Deprecated Fields:** 90 days notice before removal",
            "4. **Breaking Changes:** Requires formal approval and migration plan",
            "",
            "## Escalation Path",
            "",
            "| Severity | Response Time | Escalation |",
            "|----------|---------------|------------|",
            "| Critical (Data unavailable) | 1 hour | VP Engineering |",
            "| High (SLA breach) | 4 hours | Engineering Manager |",
            "| Medium (Quality issues) | 24 hours | Data Team Lead |",
            "| Low (Minor warnings) | 48 hours | Direct team communication |",
            "",
            "## Signatures",
            "",
            f"**Upstream System ({contract.upstream_system}):**",
            "",
            "- Name: ___________________________",
            "- Title: ___________________________",
            "- Date: ___________________________",
            "",
            f"**Downstream System ({contract.downstream_system}):**",
            "",
            "- Name: ___________________________",
            "- Title: ___________________________",
            "- Date: ___________________________",
            "",
            "---",
            "",
            f"*Generated by Tableau Data Assistant on {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        ])

        return "\n".join(lines)

    def generate_jira_ticket(self, contract: DataContract) -> str:
        """Generate JIRA ticket template for data contract proposal"""
        # Create summary of top issues
        top_issues = []
        if contract.historical_issues:
            for issue in contract.historical_issues[:5]:  # Top 5
                field = issue['field']
                frequency = issue['frequency']
                top_issues.append(f"  {field}: Issues in {frequency} of runs")

        issue_summary = "\n".join(top_issues) if top_issues else "Initial contract proposal"

        ticket = f"""**Summary:** [DATA CONTRACT] {contract.dataset_name} - Quality SLA Agreement

**Description:**

We propose establishing a formal data contract for the `{contract.dataset_name}` dataset to ensure consistent data quality between {contract.upstream_system} and {contract.downstream_system}.

**Background:**

Historical analysis shows recurring quality issues:

{issue_summary}

**Proposed Contract:**

See attached data contract document for complete specifications.

**Key Requirements:**

- Update Frequency: {contract.update_frequency}
- Data Freshness: Within {contract.sla_freshness_hours} hours
- Overall Quality Target: e {contract.quality_requirements.get('overall_validity', 95)}%
- Field Count: {len(contract.fields)} fields with specifications

**Action Items:**

[] Review proposed data contract
[] Identify any constraints that cannot be met
[] Propose alternative SLAs if needed
[] Schedule contract review meeting
[] Implement monitoring for contract adherence
[] Set up automated alerts for SLA breaches

**Success Criteria:**

- All parties agree on field specifications
- SLAs are technically achievable
- Monitoring dashboard is implemented
- Contract is signed and effective

**Priority:** High
**Labels:** data-quality, data-contract, {contract.dataset_name.lower().replace(' ', '-')}
**Component:** Data Platform
**Affects Version:** Current
**Target Version:** Next release

**Attachments:**
- data_contract_{contract.dataset_name.replace(' ', '_')}.md

"""
        return ticket

    def export_contract(
        self,
        contract: DataContract,
        format: str = "markdown",
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export data contract to file

        Args:
            contract: DataContract to export
            format: Export format ('markdown', 'json', 'jira')
            output_path: Optional output path

        Returns:
            Path to exported file
        """
        if output_path is None:
            filename = f"data_contract_{contract.dataset_name.replace(' ', '_')}"
            if format == "markdown":
                output_path = EXPORTS_DIR / f"{filename}.md"
            elif format == "json":
                output_path = EXPORTS_DIR / f"{filename}.json"
            elif format == "jira":
                output_path = EXPORTS_DIR / f"{filename}_jira.txt"
            else:
                raise ValueError(f"Unknown format: {format}")

        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True)

        if format == "markdown":
            content = self.generate_markdown(contract)
        elif format == "json":
            content = json.dumps(contract.to_dict(), indent=2)
        elif format == "jira":
            content = self.generate_jira_ticket(contract)
        else:
            raise ValueError(f"Unknown format: {format}")

        output_path.write_text(content, encoding='utf-8')

        return output_path


# Convenience functions
def generate_data_contract(
    df: pd.DataFrame,
    dataset_name: str,
    upstream_system: str,
    historical_validation_results: Optional[List[Dict[str, Any]]] = None,
    days_history: int = 30
) -> DataContract:
    """
    One-line function to generate data contract

    Args:
        df: DataFrame to analyze
        dataset_name: Name of dataset
        upstream_system: Name of upstream system
        historical_validation_results: Optional validation history
        days_history: Days of history to analyze

    Returns:
        DataContract object
    """
    analyzer = DataContractAnalyzer()

    # Analyze historical issues
    historical_analysis = analyzer.analyze_historical_issues(
        dataset_name,
        days=days_history,
        validation_results=historical_validation_results
    )

    # Generate contract
    contract = analyzer.generate_contract_from_schema(
        df,
        dataset_name,
        upstream_system,
        historical_analysis
    )

    return contract


def export_data_contract_proposal(
    contract: DataContract,
    include_jira: bool = True
) -> Dict[str, Path]:
    """
    Export data contract in multiple formats

    Args:
        contract: DataContract to export
        include_jira: Whether to generate JIRA ticket template

    Returns:
        Dictionary mapping format to file path
    """
    generator = DataContractGenerator()

    exports = {
        'markdown': generator.export_contract(contract, format='markdown'),
        'json': generator.export_contract(contract, format='json')
    }

    if include_jira:
        exports['jira'] = generator.export_contract(contract, format='jira')

    return exports
