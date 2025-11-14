"""
Example: Dashboard Story Coach (Narrative Critic)
Demonstrates how to analyze dashboard storytelling and get narrative recommendations
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    analyze_dashboard_story,
    export_story_report,
    DashboardStoryCoach
)


def create_sample_dashboard_screenshot():
    """
    Create a sample dashboard screenshot for demonstration
    Note: In real usage, you'd provide an actual screenshot path
    """
    print("NOTE: This example demonstrates the API usage.")
    print("For actual analysis, provide a real dashboard screenshot (PNG/JPG).")
    print()

    # For demonstration, we'll use a placeholder path
    # In real usage, this would be a path to your dashboard screenshot
    return "sample_dashboard.png"


def demo_basic_analysis():
    """Demo 1: Basic story analysis"""
    print("=" * 70)
    print("DEMO 1: Basic Story Analysis")
    print("=" * 70)
    print()

    # Note: In real usage, provide actual screenshot path
    print("Example Usage:")
    print("-" * 70)
    print("""
from utils import analyze_dashboard_story

# Analyze a dashboard screenshot
report = analyze_dashboard_story(
    screenshot_path='my_dashboard.png',
    primary_metric='Incident Volume',
    dashboard_name='IT Operations Dashboard',
    context='Weekly ops review for leadership team'
)

# View results
print(f"Story Score: {report.overall_story_score:.0f}/100")
print(f"Has Beginning: {report.story_arc.has_beginning}")
print(f"Has Middle: {report.story_arc.has_middle}")
print(f"Has End: {report.story_arc.has_end}")
    """)
    print()

    # Simulated output
    print("Expected Output:")
    print("-" * 70)
    print("Story Score: 68/100")
    print("Has Beginning: True")
    print("Has Middle: True")
    print("Has End: False")
    print()
    print("✓ Dashboard provides context and insights")
    print("✗ Missing clear call to action or conclusion")
    print()


def demo_narrative_comparison():
    """Demo 2: Current vs Improved narrative"""
    print("=" * 70)
    print("DEMO 2: Narrative Comparison")
    print("=" * 70)
    print()

    print("Example: Comparing Current vs Improved Story")
    print("-" * 70)
    print()

    print("📊 CURRENT NARRATIVE:")
    print("-" * 70)
    print("""
The dashboard shows incident data for the past week. There are 42 incidents
displayed across various categories. Multiple charts show different metrics
and trends. Users can filter by team and priority.
""")
    print("Score: 45/100")
    print("Issues: No clear message, viewers must work to extract insights")
    print()

    print("✨ IMPROVED NARRATIVE:")
    print("-" * 70)
    print("""
Incident volume decreased 15% this week to 42 total incidents, the lowest
in 3 months. The drop is driven by P1/P2 incidents declining 40% after
deploying automated monitoring on Monday. To sustain this trend, we should
expand monitoring to the remaining 3 teams next week.
""")
    print("Score: 88/100")
    print("Strengths: Clear beginning (context), middle (insight), end (action)")
    print()


def demo_recommendations():
    """Demo 3: Layout and content recommendations"""
    print("=" * 70)
    print("DEMO 3: Actionable Recommendations")
    print("=" * 70)
    print()

    print("Example Recommendations from Story Coach:")
    print("-" * 70)
    print()

    recommendations = [
        {
            'priority': 'HIGH',
            'current': 'KPIs scattered across dashboard with no hierarchy',
            'recommended': 'Move top 3 KPIs to a dedicated section at the top',
            'rationale': 'Users need immediate context before diving into details',
            'impact': 'Reduces time to first insight by 60%'
        },
        {
            'priority': 'HIGH',
            'current': 'Time-series trend buried in middle of page',
            'recommended': 'Position trend chart prominently after KPIs',
            'rationale': 'Temporal context is key to understanding current state',
            'impact': 'Improves narrative flow and insight clarity'
        },
        {
            'priority': 'MEDIUM',
            'current': 'No clear conclusion or action items',
            'recommended': 'Add "Recommended Actions" section at bottom',
            'rationale': 'Dashboard should guide viewers to next steps',
            'impact': 'Increases action taken from dashboard by 3x'
        }
    ]

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['priority']}] {rec['recommended']}")
        print(f"   Current State: {rec['current']}")
        print(f"   Why: {rec['rationale']}")
        print(f"   Expected Impact: {rec['impact']}")
        print()


def demo_section_titles():
    """Demo 4: Suggested section titles"""
    print("=" * 70)
    print("DEMO 4: Narrative Section Titles")
    print("=" * 70)
    print()

    print("Transform generic titles into narrative guides:")
    print("-" * 70)
    print()

    transformations = [
        ("❌ BEFORE", "✅ AFTER"),
        ("-" * 30, "-" * 38),
        ("Overview", "Where We Are Now"),
        ("Charts", "What Changed This Week?"),
        ("Data Table", "Key Drivers Behind the Trend"),
        ("Filters", "What We Should Do Next"),
        ("More Metrics", "Deep Dive: Root Cause Analysis")
    ]

    for before, after in transformations:
        print(f"{before:32} → {after}")
    print()

    print("Why This Matters:")
    print("  - Narrative titles tell a story even before viewing the data")
    print("  - Guides viewers through logical flow")
    print("  - Reduces cognitive load and speeds comprehension")
    print()


def demo_before_after_outline():
    """Demo 5: Before/After story outline"""
    print("=" * 70)
    print("DEMO 5: Before & After Story Outline")
    print("=" * 70)
    print()

    outline = """
============================================================
DASHBOARD STORY: BEFORE & AFTER
============================================================

📊 CURRENT STORY (Before)
------------------------------------------------------------
Narrative: The dashboard displays various operational metrics
including incident counts, resolution times, and team workload.
Multiple visualizations show data from different perspectives.

Structure Score: 52/100
User Guidance: 38/100

Issues:
  ✗ No clear entry point for viewers
  ✗ Key insights buried among less important data
  ✗ Missing call to action or next steps
  ✗ Filters placed prominently but context missing

✨ IMPROVED STORY (After)
------------------------------------------------------------
Narrative: Operations improved significantly this week with
42 incidents (15% decrease) and 3.2hr average resolution time
(20% faster). Success driven by new automated monitoring
deployed Monday. Expand to 3 remaining teams to sustain gains.

Structure Score: 89/100
User Guidance: 87/100

🎯 KEY CHANGES
------------------------------------------------------------
1. Move incident count KPI to top with trend indicator
   Impact: Immediate context for all viewers

2. Add timeline highlighting monitoring deployment
   Impact: Connects cause (monitoring) to effect (reduction)

3. Include "Next Steps" section with team expansion plan
   Impact: Provides clear action path

4. Reorder layout: KPIs → Trend → Root Cause → Actions
   Impact: Creates logical narrative flow

5. Reduce total metrics from 15 to 8 most important
   Impact: Eliminates distraction, focuses attention

📑 SUGGESTED SECTION TITLES
------------------------------------------------------------
  TOP: "This Week's Performance Snapshot"
  MIDDLE: "What's Driving the Improvement?"
  BOTTOM: "Recommended Actions for Next Week"
"""

    print(outline)
    print()


def demo_email_generation():
    """Demo 6: Email-ready summary"""
    print("=" * 70)
    print("DEMO 6: Email-Ready Summary")
    print("=" * 70)
    print()

    print("Story Coach generates email drafts automatically:")
    print("-" * 70)
    print()

    email = """Subject: Dashboard Story Review - IT Operations Dashboard

Hi Team,

I've reviewed the IT Operations Dashboard and have recommendations to
improve its storytelling and impact.

Currently, the dashboard presents operational data across multiple
dimensions, but the key message—that incident volume decreased 15%
this week—gets lost in the details. Viewers must work to extract
this insight instead of seeing it immediately.

By restructuring around a clear narrative arc:
1. Lead with the headline: 42 incidents (15% decrease, 3-month low)
2. Show the driver: P1/P2 incidents down 40% after Monday's deployment
3. Conclude with action: Expand monitoring to 3 remaining teams

We can reduce time-to-insight by 60% and increase action-taking by 3x.

Key changes needed:
1. Move top KPIs to dedicated section at top
2. Position trend chart prominently after KPIs
3. Add "Recommended Actions" section at bottom

The attached report includes detailed recommendations and a before/after
story outline. Let me know if you'd like to discuss implementation.

Best,
[Your Name]

---
Generated by Dashboard Story Coach
"""

    print(email)
    print()


def demo_complete_workflow():
    """Demo 7: Complete end-to-end workflow"""
    print("=" * 70)
    print("DEMO 7: Complete Workflow")
    print("=" * 70)
    print()

    print("Full Story Coaching Workflow:")
    print("-" * 70)
    print()

    workflow_code = """
from utils import analyze_dashboard_story, export_story_report

# Step 1: Analyze dashboard screenshot
print("Analyzing dashboard storytelling...")
report = analyze_dashboard_story(
    screenshot_path='operations_dashboard.png',
    primary_metric='Mean Time to Resolution',
    dashboard_name='IT Operations Dashboard',
    context='Daily standup for ops team'
)

# Step 2: Review overall score
print(f"Story Score: {report.overall_story_score:.0f}/100")

if report.overall_story_score < 70:
    print("⚠️  Story needs improvement")
else:
    print("✓ Strong storytelling")

# Step 3: Check story arc completeness
print(f"\\nStory Arc:")
print(f"  Beginning: {report.story_arc.beginning_score:.0f}/100")
print(f"  Middle: {report.story_arc.middle_score:.0f}/100")
print(f"  End: {report.story_arc.end_score:.0f}/100")

# Step 4: View narratives
print(f"\\nCurrent: {report.current_narrative}")
print(f"\\nImproved: {report.improved_narrative}")

# Step 5: Get top recommendations
high_priority = [r for r in report.layout_recommendations
                 if r.priority == 'high']

print(f"\\nTop {len(high_priority)} Recommendations:")
for i, rec in enumerate(high_priority, 1):
    print(f"{i}. {rec.recommended_state}")
    print(f"   Impact: {rec.expected_impact}")

# Step 6: Export reports
paths = export_story_report(report)
print(f"\\nReports exported:")
print(f"  Markdown: {paths['markdown']}")
print(f"  Email: {paths['email']}")
print(f"  JSON: {paths['json']}")

# Step 7: Generate before/after outline
from utils import DashboardStoryCoach
coach = DashboardStoryCoach()
outline = coach.generate_before_after_outline(report)
print(outline)
"""

    print(workflow_code)
    print()


def demo_integration_with_trust_scores():
    """Demo 8: Combining story coaching with trust scores"""
    print("=" * 70)
    print("DEMO 8: Integration with Trust Scores")
    print("=" * 70)
    print()

    print("Combine storytelling analysis with data quality:")
    print("-" * 70)
    print()

    integration_code = """
from utils import (
    analyze_dashboard_story,
    calculate_trust_scores
)

# Analyze storytelling
story_report = analyze_dashboard_story(
    screenshot_path='sales_dashboard.png',
    primary_metric='Revenue',
    dashboard_name='Sales Dashboard'
)

# Analyze data quality
trust_report = calculate_trust_scores(
    df=sales_df,
    dataset_name='Sales Data'
)

# Combined health check
print("Dashboard Health Report")
print("=" * 40)
print(f"Story Quality: {story_report.overall_story_score:.0f}/100")
print(f"Data Quality: {trust_report.overall_trust_score:.0f}/100")
print()

# Recommendations based on both
if story_report.overall_story_score < 70:
    print("📖 STORYTELLING NEEDS WORK:")
    for rec in story_report.layout_recommendations[:3]:
        if rec.priority == 'high':
            print(f"  - {rec.recommended_state}")

if trust_report.overall_trust_score < 80:
    print("\\n📊 DATA QUALITY NEEDS ATTENTION:")
    for score in trust_report.field_scores:
        if score.trust_score < 70:
            print(f"  - {score.field_name}: {score.trust_score:.0f}/100")

# Overall recommendation
overall_score = (story_report.overall_story_score +
                 trust_report.overall_trust_score) / 2

if overall_score >= 85:
    print(f"\\n✓ Dashboard is production-ready ({overall_score:.0f}/100)")
elif overall_score >= 70:
    print(f"\\n⚠️  Dashboard needs minor improvements ({overall_score:.0f}/100)")
else:
    print(f"\\n✗ Dashboard needs significant work ({overall_score:.0f}/100)")
"""

    print(integration_code)
    print()


def main():
    """Run all demos"""
    print()
    print("=" * 70)
    print("DASHBOARD STORY COACH - EXAMPLES")
    print("=" * 70)
    print()
    print("This script demonstrates the Dashboard Story Coach feature,")
    print("an AI-powered narrative critic that analyzes dashboard")
    print("screenshots and provides storytelling guidance.")
    print()
    input("Press Enter to continue...")
    print()

    # Run demos
    demo_basic_analysis()
    input("Press Enter for next demo...")
    print()

    demo_narrative_comparison()
    input("Press Enter for next demo...")
    print()

    demo_recommendations()
    input("Press Enter for next demo...")
    print()

    demo_section_titles()
    input("Press Enter for next demo...")
    print()

    demo_before_after_outline()
    input("Press Enter for next demo...")
    print()

    demo_email_generation()
    input("Press Enter for next demo...")
    print()

    demo_complete_workflow()
    input("Press Enter for next demo...")
    print()

    demo_integration_with_trust_scores()
    print()

    # Summary
    print("=" * 70)
    print("✓ EXAMPLES COMPLETE")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  1. Story Coach evaluates narrative arc (beginning, middle, end)")
    print("  2. Provides before/after story comparison")
    print("  3. Generates actionable layout and content recommendations")
    print("  4. Suggests narrative section titles")
    print("  5. Creates email-ready summaries")
    print("  6. Integrates with trust scores for complete dashboard health")
    print()
    print("To use with real dashboards:")
    print("  1. Take a screenshot of your dashboard")
    print("  2. Run: analyze_dashboard_story('your_screenshot.png', ...)")
    print("  3. Review recommendations")
    print("  4. Export reports: export_story_report(report)")
    print()
    print("See STORY_COACH_GUIDE.md for detailed documentation.")
    print()


if __name__ == '__main__':
    main()
