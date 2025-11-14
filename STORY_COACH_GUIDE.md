# Dashboard Story Coach (Narrative Critic)

## 🎯 Overview

The **Dashboard Story Coach** is an AI-powered narrative critic that analyzes dashboard screenshots and provides storytelling guidance. Unlike typical design critiques that focus on colors and layouts, this feature evaluates whether your dashboard tells a **clear, compelling story** that drives action.

### What Makes This Unusual?

Most data visualization tools critique:
- ✓ Colors and fonts
- ✓ Chart types
- ✓ Layout density

The Story Coach critiques:
- 📖 **Narrative arc** (beginning, middle, end)
- 🎯 **Story clarity** (does it guide the viewer?)
- 💡 **Insight emphasis** (what should viewers remember?)
- 🚀 **Call to action** (what should viewers do next?)

**This shifts the conversation from "does it look good?" to "does it tell a story?"**

---

## 📖 Story Arc Framework

The Story Coach uses classic storytelling structure to evaluate dashboards:

| Act | Purpose | Dashboard Elements |
|-----|---------|-------------------|
| **Beginning (Context)** | Set the stage, establish why this matters | Title, date range, KPI overview, filters |
| **Middle (Insights)** | Present the analysis, reveal trends | Charts, comparisons, anomalies, trends |
| **End (Actions)** | Conclude with what to do next | Recommendations, alerts, action items |

A great dashboard guides viewers through all three acts naturally.

---

## 🚀 Quick Start

### 1. Analyze a Dashboard Screenshot

```python
from utils import analyze_dashboard_story

# Analyze storytelling
report = analyze_dashboard_story(
    screenshot_path='dashboard_screenshot.png',
    primary_metric='Incident Volume',
    dashboard_name='IT Operations Dashboard',
    context='Weekly ops review for leadership team'
)

# View overall score
print(f"Story Score: {report.overall_story_score:.0f}/100")

# Check story arc
print(f"Has Beginning: {report.story_arc.has_beginning}")
print(f"Has Middle: {report.story_arc.has_middle}")
print(f"Has End: {report.story_arc.has_end}")
```

### 2. Get Narrative Recommendations

```python
# Current vs Improved narrative
print("Current Story:")
print(report.current_narrative)
print("\nImproved Story:")
print(report.improved_narrative)

# High priority recommendations
high_priority = [r for r in report.layout_recommendations
                 if r.priority == 'high']

for rec in high_priority:
    print(f"\n✓ {rec.recommended_state}")
    print(f"  Impact: {rec.expected_impact}")
```

### 3. Export Report

```python
from utils import export_story_report

# Export in multiple formats
paths = export_story_report(report)

print(f"Markdown report: {paths['markdown']}")
print(f"Email draft: {paths['email']}")
print(f"JSON data: {paths['json']}")
```

---

## 🎨 Example: Before & After

### ❌ Before (Poor Storytelling)

**Dashboard Layout:**
```
┌─────────────────────────────────────┐
│ [30 different metrics scattered]   │
│ [No clear visual hierarchy]        │
│ [Filters buried at bottom]         │
│ [No titles or context]             │
│ [Charts in random order]           │
└─────────────────────────────────────┘
```

**Current Narrative:**
> "The dashboard shows various metrics. There are many numbers. Some charts display trends. Viewers must figure out what matters."

**Story Arc Scores:**
- Beginning: 20/100 (no context)
- Middle: 40/100 (insights unclear)
- End: 10/100 (no conclusion)
- Coherence: 25/100

---

### ✅ After (Strong Storytelling)

**Recommended Layout:**
```
┌─────────────────────────────────────┐
│ WHERE WE ARE NOW                    │
│ [3 key KPIs prominently displayed] │
│                                     │
│ WHAT CHANGED?                       │
│ [Time-series showing trend]        │
│ [Comparison to last month]         │
│                                     │
│ WHAT WE SHOULD DO NEXT              │
│ [Top 3 action items]               │
│ [Filters in left sidebar]          │
└─────────────────────────────────────┘
```

**Improved Narrative:**
> "Incident volume decreased 15% this month (context). The drop correlates with our new monitoring system launched on May 1st (insight). We should expand monitoring to the remaining 3 teams to sustain this trend (action)."

**Story Arc Scores:**
- Beginning: 90/100 (clear context with KPIs)
- Middle: 85/100 (trend explanation)
- End: 80/100 (actionable recommendations)
- Coherence: 88/100

---

## 📊 Report Components

### StoryArc
Evaluates the three-act structure:

```python
story_arc = report.story_arc

# Check completeness
print(f"Beginning: {'✓' if story_arc.has_beginning else '✗'}")
print(f"Middle: {'✓' if story_arc.has_middle else '✗'}")
print(f"End: {'✓' if story_arc.has_end else '✗'}")

# View scores (0-100)
print(f"Beginning Score: {story_arc.beginning_score}")
print(f"Middle Score: {story_arc.middle_score}")
print(f"End Score: {story_arc.end_score}")
print(f"Overall Coherence: {story_arc.overall_coherence}")

# Issues and strengths
for issue in story_arc.narrative_flow_issues:
    print(f"  Issue: {issue}")

for strength in story_arc.strengths:
    print(f"  Strength: {strength}")
```

### StoryElement
Individual components analyzed:

```python
for element in report.story_elements:
    print(f"{element.element_type} ({element.location})")
    print(f"  Description: {element.content_description}")
    print(f"  Effectiveness: {element.effectiveness_score}/100")

    if element.issues:
        print(f"  Issues: {', '.join(element.issues)}")
    if element.suggestions:
        print(f"  Suggestions: {', '.join(element.suggestions)}")
```

### Recommendations
Actionable improvements:

```python
# Layout recommendations
for rec in report.layout_recommendations:
    if rec.priority == 'high':
        print(f"Priority: {rec.priority}")
        print(f"Current: {rec.current_state}")
        print(f"Recommended: {rec.recommended_state}")
        print(f"Rationale: {rec.rationale}")
        print(f"Expected Impact: {rec.expected_impact}")
```

### Suggested Section Titles

```python
# Get narrative section titles
titles = report.suggested_section_titles

print(f"Top Section: {titles.get('top')}")
print(f"Middle Section: {titles.get('middle')}")
print(f"Bottom Section: {titles.get('bottom')}")

# Example output:
# Top Section: "Current Performance Overview"
# Middle Section: "Key Trends & Insights"
# Bottom Section: "Recommended Actions"
```

---

## 💡 Use Cases

### Use Case 1: Executive Dashboard Review

**Scenario:** Weekly ops dashboard for C-suite. Needs to tell story in <30 seconds.

**Story Coach Analysis:**
```python
report = analyze_dashboard_story(
    screenshot_path='executive_ops.png',
    primary_metric='Overall System Health',
    dashboard_name='Executive Operations Dashboard',
    context='Weekly review for CEO and COO'
)
```

**Recommendations Provided:**
- ❌ **Current**: 15 metrics compete for attention
- ✅ **Recommended**: Show 3 KPIs at top with status indicators
- 📈 **Impact**: Reduces cognitive load by 80%, speeds decision-making

**Email Summary Generated:**
> "Your dashboard currently presents 15 metrics without clear prioritization, making it difficult to identify what requires immediate attention. By restructuring around a three-act narrative—starting with overall health status, diving into the top 3 issues, and concluding with recommended actions—executives will spend less time searching and more time acting."

---

### Use Case 2: Analyst Self-Review

**Scenario:** Data analyst wants feedback before presenting to stakeholders.

**Story Coach Analysis:**
```python
report = analyze_dashboard_story(
    screenshot_path='sales_analysis.png',
    primary_metric='Revenue Growth',
    dashboard_name='Q4 Sales Analysis'
)

# Generate before/after outline
from utils import DashboardStoryCoach
coach = DashboardStoryCoach()
outline = coach.generate_before_after_outline(report)
print(outline)
```

**Output:**
```
============================================================
DASHBOARD STORY: BEFORE & AFTER
============================================================

📊 CURRENT STORY (Before)
------------------------------------------------------------
Narrative: The dashboard shows sales data across regions.
Multiple charts display various metrics. No clear conclusion.

Structure Score: 45/100
User Guidance: 30/100

Issues:
  ✗ No clear entry point for viewers
  ✗ Insights buried in middle of page
  ✗ Missing call to action

✨ IMPROVED STORY (After)
------------------------------------------------------------
Narrative: Q4 revenue exceeded targets by 12% driven by EMEA
growth. The surge came from 3 enterprise deals closing early.
We should replicate the EMEA playbook in APAC next quarter.

Structure Score: 88/100
User Guidance: 85/100

🎯 KEY CHANGES
1. Move regional comparison to top (context)
2. Add timeline highlighting key deal closures (insight)
3. Include action items section (conclusion)

📑 SUGGESTED SECTION TITLES
  TOP: "Q4 Performance Highlights"
  MIDDLE: "What Drove the Growth?"
  BOTTOM: "Next Quarter Game Plan"
```

---

### Use Case 3: Dashboard Redesign

**Scenario:** Ops team dashboard getting poor adoption. Users say "too confusing."

**Story Coach Analysis:**
```python
# Analyze current dashboard
current_report = analyze_dashboard_story(
    screenshot_path='ops_dashboard_v1.png',
    primary_metric='Mean Time to Resolution',
    dashboard_name='Operations Dashboard v1'
)

# Apply recommendations and analyze again
# (after implementing suggested changes)
improved_report = analyze_dashboard_story(
    screenshot_path='ops_dashboard_v2.png',
    primary_metric='Mean Time to Resolution',
    dashboard_name='Operations Dashboard v2'
)

# Compare improvement
print(f"Before: {current_report.overall_story_score:.0f}/100")
print(f"After: {improved_report.overall_story_score:.0f}/100")
print(f"Improvement: +{improved_report.overall_story_score - current_report.overall_story_score:.0f} points")
```

**Results:**
- Story Score: 35/100 → 82/100 (+47 points)
- User adoption: 25% → 78% (tracked via analytics)
- Time to first insight: 3.5 min → 45 sec

---

### Use Case 4: Template Library Creation

**Scenario:** Create reusable dashboard templates with strong narratives.

**Story Coach Analysis:**
```python
# Analyze multiple high-performing dashboards
templates = [
    'incident_dashboard.png',
    'sales_dashboard.png',
    'finance_dashboard.png'
]

best_practices = []

for template in templates:
    report = analyze_dashboard_story(
        screenshot_path=template,
        primary_metric='Various',
        dashboard_name=template
    )

    if report.overall_story_score >= 80:
        best_practices.extend(report.story_arc.strengths)

# Extract common patterns
print("Best Practices from High-Scoring Dashboards:")
for practice in set(best_practices):
    print(f"  - {practice}")
```

---

## 🔧 Advanced Usage

### 1. Custom Story Coaching Prompts

```python
from utils import DashboardStoryCoach
import anthropic

# Initialize with custom client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
coach = DashboardStoryCoach(client=client)

# Analyze with specific context
report = coach.analyze_story_structure(
    screenshot_path='dashboard.png',
    primary_metric='Customer Churn Rate',
    dashboard_name='Retention Dashboard',
    context="""
    This dashboard is for Customer Success team daily standup.
    Audience: CS reps and team lead.
    Goal: Identify at-risk accounts quickly.
    Time to review: <2 minutes.
    """
)
```

### 2. Batch Analysis

```python
import os
from utils import analyze_dashboard_story

# Analyze all dashboards in a directory
dashboard_dir = 'screenshots/'
reports = []

for filename in os.listdir(dashboard_dir):
    if filename.endswith('.png'):
        report = analyze_dashboard_story(
            screenshot_path=os.path.join(dashboard_dir, filename),
            primary_metric='Auto-detected',
            dashboard_name=filename.replace('.png', '')
        )
        reports.append(report)

# Rank by story score
sorted_reports = sorted(reports, key=lambda r: r.overall_story_score, reverse=True)

print("Dashboard Story Rankings:")
for i, report in enumerate(sorted_reports, 1):
    print(f"{i}. {report.dashboard_name}: {report.overall_story_score:.0f}/100")
```

### 3. Integration with Trust Scores

```python
from utils import analyze_dashboard_story, calculate_trust_scores

# Analyze both storytelling and data quality
story_report = analyze_dashboard_story(
    screenshot_path='dashboard.png',
    primary_metric='Revenue',
    dashboard_name='Sales Dashboard'
)

trust_report = calculate_trust_scores(
    df=df,
    dataset_name='Sales Data'
)

# Combined recommendation
if story_report.overall_story_score < 70:
    print("⚠️ Storytelling needs improvement")
    print(f"Priority: {story_report.layout_recommendations[0].recommended_state}")

if trust_report.overall_trust_score < 80:
    print("⚠️ Data quality needs attention")
    for score in trust_report.field_scores:
        if score.trust_score < 70:
            print(f"  - {score.field_name}: {score.trust_score:.0f}/100")
```

### 4. Automated Weekly Reviews

```python
import schedule
from datetime import datetime

def weekly_dashboard_review():
    """Run story coaching on key dashboards weekly"""

    dashboards = {
        'exec_ops.png': 'System Health',
        'sales_pipeline.png': 'Pipeline Value',
        'customer_health.png': 'NPS Score'
    }

    for screenshot, metric in dashboards.items():
        report = analyze_dashboard_story(
            screenshot_path=screenshot,
            primary_metric=metric,
            dashboard_name=screenshot.replace('.png', '')
        )

        # Alert if score drops
        if report.overall_story_score < 70:
            send_alert(f"Dashboard {screenshot} story score: {report.overall_story_score:.0f}/100")
            export_story_report(report)

# Schedule weekly
schedule.every().monday.at("09:00").do(weekly_dashboard_review)
```

---

## 📖 Storytelling Best Practices

### 1. Start with Context (The Beginning)

**Bad:**
```
┌─────────────────┐
│ 42 incidents    │
│ 3.2 hrs MTTR    │
└─────────────────┘
```

**Good:**
```
┌─────────────────────────────────────┐
│ IT OPERATIONS - WEEK OF JAN 8-14    │
│ 42 incidents (-15% vs last week)    │
│ 3.2 hrs MTTR (target: 4 hrs) ✓      │
└─────────────────────────────────────┘
```

**Why:** Viewers need context to interpret numbers. Is 42 good or bad? The "good" version answers that immediately.

---

### 2. Guide the Eye (The Middle)

**Bad:** Scattered charts with no visual hierarchy

**Good:** Use size, position, and whitespace to guide viewers:
1. **Top third**: Most important insight (largest)
2. **Middle third**: Supporting details
3. **Bottom third**: Deep-dive or filters

---

### 3. End with Action (The End)

**Bad:** Dashboard ends with more data

**Good:** Dashboard concludes with:
- ✓ "Top 3 Action Items"
- ✓ "What to Watch Next Week"
- ✓ "Recommended Next Steps"

---

### 4. Use Narrative Section Titles

**Bad Titles:**
- "Chart 1"
- "Data Table"
- "More Metrics"

**Good Titles:**
- "Where We Stand Today"
- "What's Driving the Change?"
- "What We Should Do Next"

These titles tell a story even before viewers read the data.

---

## 🧪 Testing Story Quality

```python
import pytest
from utils import analyze_dashboard_story

def test_strong_narrative():
    """Test that well-designed dashboard scores high"""
    report = analyze_dashboard_story(
        screenshot_path='tests/fixtures/good_dashboard.png',
        primary_metric='Revenue',
        dashboard_name='Test Dashboard'
    )

    assert report.overall_story_score >= 70
    assert report.story_arc.has_beginning
    assert report.story_arc.has_middle
    assert report.story_arc.has_end

def test_weak_narrative():
    """Test that poorly designed dashboard gets recommendations"""
    report = analyze_dashboard_story(
        screenshot_path='tests/fixtures/poor_dashboard.png',
        primary_metric='Revenue',
        dashboard_name='Test Dashboard'
    )

    assert report.overall_story_score < 70
    assert len(report.layout_recommendations) > 0
    assert any(r.priority == 'high' for r in report.layout_recommendations)
```

---

## 📧 Email-Ready Summaries

The Story Coach generates email drafts automatically:

```python
from utils import export_story_report

report = analyze_dashboard_story(
    screenshot_path='dashboard.png',
    primary_metric='Churn Rate',
    dashboard_name='Retention Dashboard'
)

paths = export_story_report(report)

# Read email draft
with open(paths['email'], 'r') as f:
    email = f.read()
    print(email)
```

**Example Email Output:**
```
Subject: Dashboard Story Review - Retention Dashboard

Hi [Stakeholder],

Your Retention Dashboard currently presents churn data across multiple
dimensions but lacks a clear narrative flow. Viewers must work to extract
the key insight: churn increased 8% in Q4, primarily among SMB customers.
By restructuring the dashboard to lead with this headline, then showing
the SMB breakdown, and concluding with retention initiatives, you'll
enable faster decision-making and clearer accountability.

Key recommendations:
1. Move the churn trend to the top with clear indicator (8% increase)
2. Add a comparison showing SMB vs Enterprise churn side-by-side
3. Include a "Retention Initiatives" section with progress tracking

Let me know if you'd like to discuss these suggestions.

Best,
[Your Name]
```

---

## 🎯 Scoring Rubric

### Overall Story Score (0-100)

| Score | Interpretation | Action |
|-------|---------------|--------|
| 90-100 | Excellent storytelling | Share as template |
| 75-89 | Good, minor improvements | Implement 1-2 suggestions |
| 60-74 | Acceptable, needs work | Prioritize high-impact changes |
| 40-59 | Poor, major issues | Significant redesign needed |
| 0-39 | Very poor | Start from scratch with narrative framework |

### Story Arc Component Scores

Each component (beginning, middle, end) is scored 0-100:

- **90-100**: Exceptional - clear, compelling, memorable
- **75-89**: Strong - effective with minor improvements possible
- **60-74**: Adequate - gets the job done but lacks impact
- **40-59**: Weak - confusing or missing key elements
- **0-39**: Very weak - largely absent or ineffective

---

## 🚨 Troubleshooting

### Q: Story Coach returns low scores but I think the dashboard is good

**A:** The Story Coach evaluates **narrative clarity**, not visual design. A beautiful dashboard can score low if it doesn't guide viewers through a clear story. Review the specific recommendations:

```python
# Check what's missing
if not report.story_arc.has_end:
    print("Missing: Conclusion or call to action")
    print("Add: Action items section or 'Next Steps' panel")
```

---

### Q: Can I use this without Claude API?

**A:** The Story Coach requires Claude's vision capabilities for screenshot analysis. However, you can:
1. Use it in offline mode with pre-generated reports
2. Manually apply the story arc framework
3. Use the export templates for structure

---

### Q: How do I improve my story score?

**A:** Focus on the three-act structure:

1. **Add Context (Beginning)**
   - Clear dashboard title with timeframe
   - KPI overview showing status (good/bad)
   - Filters prominently displayed

2. **Clarify Insights (Middle)**
   - Highlight key trends with annotations
   - Use visual hierarchy (biggest chart = most important)
   - Compare to baselines or targets

3. **Drive Action (End)**
   - Add recommendations section
   - Include "what to watch" indicators
   - Provide clear next steps

---

### Q: Can I customize the narrative framework?

**A:** Yes, modify the prompt in `story_coach.py`:

```python
def _build_story_critique_prompt(self, primary_metric, dashboard_name, context):
    # Add your custom framework
    return f"""
    Analyze using the SCQA framework:
    - Situation: What's the context?
    - Complication: What's the problem?
    - Question: What should we ask?
    - Answer: What's the recommendation?
    ...
    """
```

---

## 📚 API Reference

### Core Functions

#### `analyze_dashboard_story()`
```python
def analyze_dashboard_story(
    screenshot_path: str,
    primary_metric: str,
    dashboard_name: str = "Dashboard",
    context: Optional[str] = None
) -> NarrativeReport
```

**Parameters:**
- `screenshot_path`: Path to dashboard image (PNG, JPG, etc.)
- `primary_metric`: Main metric displayed (e.g., "Revenue", "MTTR")
- `dashboard_name`: Dashboard name for reporting
- `context`: Optional context about audience/purpose

**Returns:** `NarrativeReport` with complete story analysis

---

#### `export_story_report()`
```python
def export_story_report(
    report: NarrativeReport,
    output_dir: str = "exports/story_coach"
) -> Dict[str, str]
```

**Parameters:**
- `report`: NarrativeReport to export
- `output_dir`: Export directory

**Returns:** Dict mapping format to file path:
```python
{
    'markdown': 'exports/story_coach/report.md',
    'email': 'exports/story_coach/email_draft.txt',
    'json': 'exports/story_coach/report.json'
}
```

---

### Classes

#### `DashboardStoryCoach`
Main class for story analysis:

```python
coach = DashboardStoryCoach(client=anthropic_client)

report = coach.analyze_story_structure(
    screenshot_path='dashboard.png',
    primary_metric='Revenue',
    dashboard_name='Sales Dashboard',
    context='Weekly exec review'
)

outline = coach.generate_before_after_outline(report)
paths = coach.export_report(report)
```

---

## 🎁 Complete Example

```python
from utils import analyze_dashboard_story, export_story_report

# 1. Analyze dashboard
report = analyze_dashboard_story(
    screenshot_path='operations_dashboard.png',
    primary_metric='Mean Time to Resolution',
    dashboard_name='IT Operations Dashboard',
    context='Daily standup for ops team'
)

# 2. Print summary
print(f"Dashboard: {report.dashboard_name}")
print(f"Story Score: {report.overall_story_score:.0f}/100")
print()

print("Story Arc:")
print(f"  Beginning: {report.story_arc.beginning_score:.0f}/100")
print(f"  Middle: {report.story_arc.middle_score:.0f}/100")
print(f"  End: {report.story_arc.end_score:.0f}/100")
print()

# 3. Show narratives
print("Current Narrative:")
print(f"  {report.current_narrative}")
print()
print("Improved Narrative:")
print(f"  {report.improved_narrative}")
print()

# 4. Top recommendations
print("Top 3 Recommendations:")
high_priority = [r for r in report.layout_recommendations + report.content_recommendations
                 if r.priority == 'high']
for i, rec in enumerate(high_priority[:3], 1):
    print(f"{i}. {rec.recommended_state}")
    print(f"   Impact: {rec.expected_impact}")
    print()

# 5. Suggested section titles
print("Suggested Section Titles:")
for location, title in report.suggested_section_titles.items():
    print(f"  {location}: \"{title}\"")
print()

# 6. Export reports
paths = export_story_report(report)
print(f"Reports exported:")
print(f"  Markdown: {paths['markdown']}")
print(f"  Email: {paths['email']}")
print(f"  JSON: {paths['json']}")
```

---

## 🏆 Benefits

| Benefit | Description |
|---------|-------------|
| **Faster Decision-Making** | Clear narratives reduce time to insight |
| **Higher Adoption** | Users engage with dashboards that tell stories |
| **Better Presentations** | Email-ready summaries for stakeholders |
| **Consistent Quality** | Automated review ensures narrative standards |
| **Reduced Training** | Self-service dashboards when story is clear |
| **Actionable Feedback** | Specific, prioritized recommendations |

---

## 📞 Support

- **Module**: `utils/story_coach.py`
- **Examples**: `examples/story_coach_example.py`
- **Related Features**: Screenshot Analysis ([screenshot_analysis.py](utils/screenshot_analysis.py))

---

**🎉 You now have an AI storytelling coach for your dashboards!**

This feature helps bridge the gap between data analysis and data communication. Use it to ensure every dashboard tells a clear, compelling story that drives action.

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-01-14
