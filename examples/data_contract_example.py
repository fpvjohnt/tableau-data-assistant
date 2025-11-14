"""
Example: Data Contract Auto-Generation
Demonstrates how to analyze historical issues and generate formal data contracts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    validate_for_tableau,
    generate_data_contract,
    export_data_contract_proposal,
    DataContractAnalyzer,
    DataContractGenerator
)


def create_sample_data_with_issues(day_offset=0):
    """Create sample sales dataset with varying quality issues over time"""
    np.random.seed(42 + day_offset)

    # Simulate data quality degrading over time
    null_rate_multiplier = 1.0 + (day_offset / 30.0)  # Increases over 30 days

    data = {
        # Good field - no issues
        'order_id': [f'ORD{i:05d}' for i in range(1000, 1500)],

        # Field with increasing null rate (simulating upstream issue)
        'customer_email': [
            f'user{i}@example.com' if np.random.random() > (0.05 * null_rate_multiplier) else None
            for i in range(500)
        ],

        # Field with uniqueness issues
        'customer_id': [
            f'CUST{i:04d}' if i % 20 != 0 else f'CUST{(i-1):04d}'  # Duplicates every 20 rows
            for i in range(500)
        ],

        # Field with type issues
        'revenue': [
            float(np.random.normal(1000, 200)) if i % 15 != 0 else None  # Some nulls
            for i in range(500)
        ],

        # Date field for freshness
        'order_date': [
            datetime.now() - timedelta(days=np.random.randint(0, 2))
            for _ in range(500)
        ],

        # Field with invalid phone formats
        'phone': [
            f'555-{i:04d}' if i % 10 != 0 else f'{i}'  # Invalid format every 10 rows
            for i in range(500)
        ]
    }

    return pd.DataFrame(data)


def simulate_historical_validations(days=30):
    """Simulate validation results over N days"""
    print(f"\nSimulating {days} days of validation history...")

    historical_results = []

    for day in range(days):
        # Create data with issues
        df = create_sample_data_with_issues(day_offset=day)

        # Run validation
        result, _ = validate_for_tableau(
            df,
            required_columns=['order_id', 'customer_id', 'customer_email', 'revenue'],
            unique_columns=['order_id', 'customer_id']
        )

        historical_results.append({
            'timestamp': datetime.now() - timedelta(days=days-day),
            'result': result
        })

        if day % 7 == 0:
            print(f"  Day {day+1}/{days}: {'PASSED' if result.passed else 'FAILED'} "
                  f"({result.passed_checks} passed, {result.failed_checks} failed)")

    print(f"✓ Collected {len(historical_results)} validation results")
    return historical_results


def main():
    """Main example workflow"""
    print("=" * 60)
    print("Data Contract Copilot Example")
    print("=" * 60)

    # 1. Simulate historical validation data
    print("\n1. Collecting Historical Validation Data...")
    historical_results = simulate_historical_validations(days=30)

    # 2. Load current data
    print("\n2. Loading Current Dataset...")
    df_current = create_sample_data_with_issues(day_offset=30)
    print(f"   Dataset: {df_current.shape[0]} rows × {df_current.shape[1]} columns")

    # 3. Analyze historical issues
    print("\n3. Analyzing Historical Issues...")
    analyzer = DataContractAnalyzer()
    field_issues, recurring_issues, recommendations = analyzer.analyze_historical_issues(
        dataset_name='Sales Data',
        days=30,
        validation_results=historical_results
    )

    print(f"   Found {len(field_issues)} fields with issues")
    print(f"   Identified {len(recurring_issues)} recurring problems")
    print(f"   Generated {len(recommendations)} recommendations")

    # Display recurring issues
    print("\n4. Recurring Issues Detected:")
    if recurring_issues:
        for issue in recurring_issues[:5]:  # Show top 5
            print(f"   - {issue['field']}: {issue['issue_type']} "
                  f"(occurred {issue['frequency']} times over {issue['days_span']} days)")
    else:
        print("   No recurring issues detected")

    # Display recommendations
    print("\n5. Recommendations for Upstream Team:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. {rec}")

    # 6. Generate data contract
    print("\n6. Generating Data Contract...")
    contract = generate_data_contract(
        df=df_current,
        dataset_name='Sales Data',
        upstream_system='ServiceNow CRM',
        historical_validation_results=historical_results,
        days_history=30
    )

    print(f"   Contract Name: {contract.dataset_name}")
    print(f"   Upstream System: {contract.upstream_system}")
    print(f"   Downstream System: {contract.downstream_system}")
    print(f"   Fields Specified: {len(contract.fields)}")
    print(f"   Historical Issues Documented: {len(contract.historical_issues)}")
    print(f"   Proposed SLA Uptime: {contract.sla_uptime}%")
    print(f"   Proposed Freshness: {contract.sla_freshness_hours} hours")

    # 7. Display field contracts
    print("\n7. Field-Level Contract Specifications:")
    print(f"   {'Field':<20} {'Type':<10} {'Required':<10} {'Unique':<10} {'Issues':<30}")
    print("   " + "-" * 80)

    for field in contract.fields[:5]:  # Show first 5
        issues = field.observed_issues[0] if field.observed_issues else 'None'
        print(f"   {field.field_name:<20} {field.data_type:<10} "
              f"{'Yes' if field.required else 'No':<10} "
              f"{'Yes' if field.unique else 'No':<10} "
              f"{issues[:30]:<30}")

    if len(contract.fields) > 5:
        print(f"   ... and {len(contract.fields) - 5} more fields")

    # 8. Export contract
    print("\n8. Exporting Contract Proposal...")
    paths = export_data_contract_proposal(contract, include_jira=True)

    print(f"   Markdown Contract: {paths['markdown']}")
    print(f"   JSON Contract: {paths['json']}")
    print(f"   JIRA Ticket Template: {paths['jira']}")

    # 9. Show contract preview
    print("\n9. Contract Preview (First 20 Lines):")
    print("   " + "-" * 70)

    generator = DataContractGenerator()
    contract_md = generator.generate_markdown(contract)

    for i, line in enumerate(contract_md.split('\n')[:20], 1):
        print(f"   {line}")

    print("   ...")
    print(f"   [Full contract: {len(contract_md.split(chr(10)))} lines total]")

    # 10. Show JIRA ticket preview
    print("\n10. JIRA Ticket Preview:")
    print("   " + "-" * 70)

    jira_ticket = generator.generate_jira_ticket(contract)

    for i, line in enumerate(jira_ticket.split('\n')[:15], 1):
        print(f"   {line}")

    print("   ...")

    # Summary
    print("\n" + "=" * 60)
    print("✓ Data Contract Generated Successfully!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Review contract files in exports/contracts/")
    print(f"2. Open {paths['markdown']} to see full contract")
    print("3. Customize SLAs and requirements as needed")
    print("4. Send to upstream team (ServiceNow) for review")
    print("5. Create JIRA ticket using template in " + paths['jira'])
    print("6. Schedule negotiation meeting with upstream team")
    print("7. Once approved, use trust scores to monitor compliance")
    print("\nSee DATA_CONTRACT_GUIDE.md for detailed instructions.")

    # Bonus: Show quality requirements
    print("\n" + "=" * 60)
    print("Quality Requirements Summary:")
    print("=" * 60)
    for key, value in contract.quality_requirements.items():
        print(f"  - {key}: {value}")

    print("\n" + "=" * 60)
    print("Historical Issue Timeline:")
    print("=" * 60)
    for issue in contract.historical_issues[:5]:
        print(f"  [{issue['timestamp'].strftime('%Y-%m-%d')}] "
              f"{issue['field']}: {issue['issue_type']}")

    if len(contract.historical_issues) > 5:
        print(f"  ... and {len(contract.historical_issues) - 5} more issues")


if __name__ == '__main__':
    main()
