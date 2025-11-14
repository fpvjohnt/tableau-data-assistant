"""
Example: Trust Heatmap Generation for Tableau
Demonstrates how to calculate and export trust scores
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
    detect_anomalies,
    calculate_trust_scores,
    export_trust_scores_for_tableau,
    TrustScoreStore,
    TrustHeatmapGenerator
)


def create_sample_sales_data():
    """Create sample sales dataset with varying quality"""
    np.random.seed(42)

    data = {
        # Perfect field - high trust
        'order_id': range(1, 1001),

        # Good field - minor issues
        'customer_id': [f'CUST{i:04d}' for i in range(1, 1001)],

        # Okay field - some nulls
        'customer_email': [
            f'user{i}@example.com' if i % 10 != 0 else None
            for i in range(1, 1001)
        ],

        # Poor field - lots of nulls
        'phone': [
            f'555-{i:04d}' if i % 3 != 0 else None
            for i in range(1, 1001)
        ],

        # Good numeric field
        'revenue': np.random.normal(1000, 200, 1000),

        # Field with anomalies
        'quantity': [
            int(np.random.normal(10, 3)) if i % 50 != 0 else 1000  # Outliers every 50 rows
            for i in range(1000)
        ],

        # Date field - fresh data
        'order_date': [
            datetime.now() - timedelta(days=np.random.randint(0, 7))
            for _ in range(1000)
        ],

        # Old date field - stale data
        'last_contact': [
            datetime.now() - timedelta(days=np.random.randint(60, 180))
            for _ in range(1000)
        ]
    }

    return pd.DataFrame(data)


def main():
    """Main example workflow"""
    print("=" * 60)
    print("Trust Heatmap Example for Tableau")
    print("=" * 60)

    # 1. Create sample data
    print("\n1. Creating sample sales data...")
    df = create_sample_sales_data()
    print(f"   Created dataset: {df.shape[0]} rows × {df.shape[1]} columns")

    # 2. Run validation
    print("\n2. Running data validation...")
    validation_result, _ = validate_for_tableau(
        df,
        required_columns=['order_id', 'customer_id', 'revenue'],
        unique_columns=['order_id']
    )
    print(f"   Validation: {'PASSED ✓' if validation_result.passed else 'FAILED ✗'}")
    print(f"   Checks: {validation_result.passed_checks} passed, {validation_result.failed_checks} failed")

    # 3. Detect anomalies
    print("\n3. Detecting anomalies...")
    anomaly_report = detect_anomalies(df, method='iqr')
    print(f"   Found {anomaly_report.total_anomalies} anomalies ({anomaly_report.anomaly_percentage:.1f}%)")
    if anomaly_report.anomalies_by_column:
        for col, count in list(anomaly_report.anomalies_by_column.items())[:3]:
            print(f"     - {col}: {count} anomalies")

    # 4. Calculate trust scores
    print("\n4. Calculating trust scores...")
    trust_report = calculate_trust_scores(
        df,
        validation_result=validation_result,
        anomaly_report=anomaly_report,
        date_column='order_date',
        dataset_name='Sample Sales Data'
    )
    print(f"   Overall Trust Score: {trust_report.overall_trust_score:.1f}/100")
    print(f"   Fields: {trust_report.metadata['total_fields']}")
    print(f"     - High trust (≥90): {trust_report.metadata['high_trust_fields']}")
    print(f"     - Medium trust (75-89): {trust_report.metadata['medium_trust_fields']}")
    print(f"     - Low trust (<75): {trust_report.metadata['low_trust_fields']}")

    # 5. Display field-level scores
    print("\n5. Field-Level Trust Scores:")
    print(f"   {'Field':<20} {'Score':<8} {'Grade':<6} {'Issues':<30}")
    print("   " + "-" * 70)

    for score in sorted(trust_report.field_scores, key=lambda x: x.trust_score, reverse=True):
        issues = score.warnings[0] if score.warnings else 'None'
        color_emoji = {
            '#10a37f': '🟢',
            '#f39c12': '🟡',
            '#e67e22': '🟠',
            '#e74c3c': '🔴'
        }.get(score.get_color(), '⚪')

        print(f"   {score.field_name:<20} {score.trust_score:<8.1f} {score.get_grade():<6} {color_emoji} {issues:<30}")

    # 6. Export for Tableau
    print("\n6. Exporting trust scores for Tableau...")
    csv_path = export_trust_scores_for_tableau(trust_report, save_to_db=True)
    print(f"   CSV exported to: {csv_path}")
    print(f"   Database updated: exports/trust_scores.db")

    # 7. Generate tooltips
    print("\n7. Sample Tableau Tooltip (for 'revenue' field):")
    generator = TrustHeatmapGenerator()
    revenue_score = [s for s in trust_report.field_scores if s.field_name == 'revenue'][0]
    tooltip = generator.generate_tooltip_text(revenue_score)
    print("\n" + "   " + tooltip.replace("\n", "\n   "))

    # 8. Show trust matrix
    print("\n8. Trust Matrix (for heatmap visualization):")
    matrix = generator.create_trust_matrix(trust_report)
    print(matrix.round(1))

    # 9. Check historical data
    print("\n9. Historical Trust Scores:")
    store = TrustScoreStore()
    latest = store.get_latest_scores('Sample Sales Data')
    print(f"   Found {len(latest)} historical records")

    # Summary
    print("\n" + "=" * 60)
    print("✓ Trust Heatmap Generated Successfully!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Open Tableau Desktop")
    print(f"2. Import CSV: {csv_path}")
    print("3. Create calculated field for color: ATTR([Color])")
    print("4. Add Trust_Score to tooltips")
    print("5. Use Color field to color-code your metrics")
    print("\nSee TRUST_HEATMAP_GUIDE.md for detailed instructions.")


if __name__ == '__main__':
    main()
