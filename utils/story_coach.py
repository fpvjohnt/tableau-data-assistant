"""
Dashboard Story Coach (Narrative Critic)
Analyzes dashboard screenshots and provides storytelling guidance

This module uses AI vision to critique the narrative arc of dashboards and
suggest improvements to help analysts tell compelling data stories.
"""

import os
import base64
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class StoryElement:
    """Represents a narrative element in the dashboard"""
    element_type: str  # "context", "insight", "action", "metric", "filter"
    location: str  # "top-left", "center", "bottom-right", etc.
    content_description: str
    effectiveness_score: float  # 0-100
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class StoryArc:
    """Represents the overall narrative structure"""
    has_beginning: bool  # Context/setup present
    has_middle: bool  # Insights/analysis present
    has_end: bool  # Conclusions/actions present

    beginning_score: float  # 0-100
    middle_score: float
    end_score: float
    overall_coherence: float  # 0-100

    beginning_elements: List[StoryElement] = field(default_factory=list)
    middle_elements: List[StoryElement] = field(default_factory=list)
    end_elements: List[StoryElement] = field(default_factory=list)

    narrative_flow_issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


@dataclass
class StoryRecommendation:
    """Specific recommendation for improving the story"""
    category: str  # "layout", "content", "emphasis", "sequence"
    priority: str  # "high", "medium", "low"
    current_state: str
    recommended_state: str
    rationale: str
    expected_impact: str


@dataclass
class NarrativeReport:
    """Complete story coaching report"""
    dashboard_name: str
    primary_metric: str
    analysis_timestamp: datetime

    # Story analysis
    story_arc: StoryArc
    story_elements: List[StoryElement]

    # Narrative text
    current_narrative: str  # What story it tells now
    improved_narrative: str  # Better version
    email_summary: str  # 1-2 paragraphs for email

    # Section recommendations
    suggested_section_titles: Dict[str, str]  # location -> title
    layout_recommendations: List[StoryRecommendation]
    content_recommendations: List[StoryRecommendation]

    # Scoring
    overall_story_score: float  # 0-100
    before_after_comparison: Dict[str, Any]

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'dashboard_name': self.dashboard_name,
            'primary_metric': self.primary_metric,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'story_arc': {
                'has_beginning': self.story_arc.has_beginning,
                'has_middle': self.story_arc.has_middle,
                'has_end': self.story_arc.has_end,
                'scores': {
                    'beginning': self.story_arc.beginning_score,
                    'middle': self.story_arc.middle_score,
                    'end': self.story_arc.end_score,
                    'coherence': self.story_arc.overall_coherence
                }
            },
            'narratives': {
                'current': self.current_narrative,
                'improved': self.improved_narrative,
                'email': self.email_summary
            },
            'suggested_sections': self.suggested_section_titles,
            'recommendations': {
                'layout': [
                    {
                        'priority': r.priority,
                        'current': r.current_state,
                        'recommended': r.recommended_state,
                        'rationale': r.rationale
                    }
                    for r in self.layout_recommendations
                ],
                'content': [
                    {
                        'priority': r.priority,
                        'current': r.current_state,
                        'recommended': r.recommended_state,
                        'rationale': r.rationale
                    }
                    for r in self.content_recommendations
                ]
            },
            'overall_story_score': self.overall_story_score,
            'before_after': self.before_after_comparison
        }


class DashboardStoryCoach:
    """
    AI-powered dashboard storytelling coach

    Analyzes dashboard screenshots to evaluate narrative structure and
    provides recommendations for improving the storytelling.
    """

    def __init__(self, client: Optional[anthropic.Anthropic] = None):
        """
        Initialize story coach

        Args:
            client: Optional Claude API client. If not provided, will create from env
        """
        if client:
            self.client = client
        elif ANTHROPIC_AVAILABLE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
            else:
                self.client = None
        else:
            self.client = None

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Encode image to base64

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Determine media type from extension
        ext = Path(image_path).suffix.lower()
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_types.get(ext, 'image/png')

        return base64.standard_b64encode(image_data).decode('utf-8'), media_type

    def analyze_story_structure(
        self,
        screenshot_path: str,
        primary_metric: str,
        dashboard_name: str = "Dashboard",
        context: Optional[str] = None
    ) -> NarrativeReport:
        """
        Analyze dashboard storytelling structure

        Args:
            screenshot_path: Path to dashboard screenshot
            primary_metric: Main metric (e.g., "Incident Volume", "MTTR")
            dashboard_name: Name of the dashboard
            context: Optional context about the dashboard's purpose

        Returns:
            NarrativeReport with complete story analysis
        """
        if not self.client:
            # Fallback mode without AI
            return self._fallback_analysis(screenshot_path, primary_metric, dashboard_name)

        # Encode image
        image_data, media_type = self._encode_image(screenshot_path)

        # Construct storytelling critique prompt
        prompt = self._build_story_critique_prompt(primary_metric, dashboard_name, context)

        # Call Claude with vision
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Parse AI response
            ai_response = response.content[0].text
            report = self._parse_ai_response(ai_response, primary_metric, dashboard_name)

            return report

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return self._fallback_analysis(screenshot_path, primary_metric, dashboard_name)

    def _build_story_critique_prompt(
        self,
        primary_metric: str,
        dashboard_name: str,
        context: Optional[str]
    ) -> str:
        """Build prompt for AI story analysis"""

        context_section = f"\n\nContext: {context}" if context else ""

        return f"""You are a professional data storytelling coach. Analyze this dashboard screenshot and evaluate how well it tells a story.

Dashboard: {dashboard_name}
Primary Metric: {primary_metric}{context_section}

Analyze the dashboard using the classic story arc framework:
1. **Beginning (Context/Setup)**: Does it establish what we're looking at and why it matters?
2. **Middle (Insights/Analysis)**: Does it present clear insights or trends?
3. **End (Conclusions/Actions)**: Does it lead to conclusions or next steps?

Provide your analysis in the following JSON format:

{{
  "story_arc": {{
    "has_beginning": true/false,
    "has_middle": true/false,
    "has_end": true/false,
    "beginning_score": 0-100,
    "middle_score": 0-100,
    "end_score": 0-100,
    "overall_coherence": 0-100,
    "narrative_flow_issues": ["issue1", "issue2"],
    "strengths": ["strength1", "strength2"]
  }},
  "story_elements": [
    {{
      "element_type": "context|insight|action|metric|filter",
      "location": "top-left|center|bottom-right|etc",
      "content_description": "brief description",
      "effectiveness_score": 0-100,
      "issues": ["issue1"],
      "suggestions": ["suggestion1"]
    }}
  ],
  "current_narrative": "What story the dashboard tells now (2-3 sentences)",
  "improved_narrative": "Better version with clearer arc (2-3 sentences)",
  "email_summary": "1-2 paragraph summary suitable for email to stakeholders",
  "suggested_section_titles": {{
    "top": "Title for top section",
    "middle": "Title for middle section",
    "bottom": "Title for bottom section"
  }},
  "layout_recommendations": [
    {{
      "priority": "high|medium|low",
      "current_state": "Current layout issue",
      "recommended_state": "How to fix it",
      "rationale": "Why this matters",
      "expected_impact": "What this will improve"
    }}
  ],
  "content_recommendations": [
    {{
      "priority": "high|medium|low",
      "current_state": "Current content issue",
      "recommended_state": "How to fix it",
      "rationale": "Why this matters",
      "expected_impact": "What this will improve"
    }}
  ],
  "overall_story_score": 0-100,
  "before_after_comparison": {{
    "before": {{
      "structure": "Current structure description",
      "narrative_clarity": 0-100,
      "user_guidance": 0-100
    }},
    "after": {{
      "structure": "Recommended structure description",
      "narrative_clarity": 0-100,
      "user_guidance": 0-100
    }}
  }}
}}

Be specific and actionable. Focus on storytelling, not just design. Think like a narrative coach helping an analyst present their findings compellingly."""

    def _parse_ai_response(
        self,
        ai_response: str,
        primary_metric: str,
        dashboard_name: str
    ) -> NarrativeReport:
        """Parse AI response into NarrativeReport"""

        try:
            # Extract JSON from response (might be wrapped in markdown)
            json_str = ai_response
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].split("```")[0].strip()

            data = json.loads(json_str)

            # Build StoryArc
            arc_data = data.get('story_arc', {})
            story_arc = StoryArc(
                has_beginning=arc_data.get('has_beginning', False),
                has_middle=arc_data.get('has_middle', False),
                has_end=arc_data.get('has_end', False),
                beginning_score=arc_data.get('beginning_score', 0),
                middle_score=arc_data.get('middle_score', 0),
                end_score=arc_data.get('end_score', 0),
                overall_coherence=arc_data.get('overall_coherence', 0),
                narrative_flow_issues=arc_data.get('narrative_flow_issues', []),
                strengths=arc_data.get('strengths', [])
            )

            # Build StoryElements
            story_elements = []
            for elem in data.get('story_elements', []):
                story_elements.append(StoryElement(
                    element_type=elem.get('element_type', 'unknown'),
                    location=elem.get('location', 'unknown'),
                    content_description=elem.get('content_description', ''),
                    effectiveness_score=elem.get('effectiveness_score', 0),
                    issues=elem.get('issues', []),
                    suggestions=elem.get('suggestions', [])
                ))

            # Build recommendations
            layout_recs = []
            for rec in data.get('layout_recommendations', []):
                layout_recs.append(StoryRecommendation(
                    category='layout',
                    priority=rec.get('priority', 'medium'),
                    current_state=rec.get('current_state', ''),
                    recommended_state=rec.get('recommended_state', ''),
                    rationale=rec.get('rationale', ''),
                    expected_impact=rec.get('expected_impact', '')
                ))

            content_recs = []
            for rec in data.get('content_recommendations', []):
                content_recs.append(StoryRecommendation(
                    category='content',
                    priority=rec.get('priority', 'medium'),
                    current_state=rec.get('current_state', ''),
                    recommended_state=rec.get('recommended_state', ''),
                    rationale=rec.get('rationale', ''),
                    expected_impact=rec.get('expected_impact', '')
                ))

            # Create report
            report = NarrativeReport(
                dashboard_name=dashboard_name,
                primary_metric=primary_metric,
                analysis_timestamp=datetime.now(),
                story_arc=story_arc,
                story_elements=story_elements,
                current_narrative=data.get('current_narrative', ''),
                improved_narrative=data.get('improved_narrative', ''),
                email_summary=data.get('email_summary', ''),
                suggested_section_titles=data.get('suggested_section_titles', {}),
                layout_recommendations=layout_recs,
                content_recommendations=content_recs,
                overall_story_score=data.get('overall_story_score', 0),
                before_after_comparison=data.get('before_after_comparison', {}),
                metadata={
                    'ai_model': 'claude-3-5-sonnet-20241022',
                    'analysis_method': 'vision_api'
                }
            )

            return report

        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._fallback_analysis(None, primary_metric, dashboard_name)

    def _fallback_analysis(
        self,
        screenshot_path: Optional[str],
        primary_metric: str,
        dashboard_name: str
    ) -> NarrativeReport:
        """Fallback analysis without AI"""

        story_arc = StoryArc(
            has_beginning=False,
            has_middle=False,
            has_end=False,
            beginning_score=0,
            middle_score=0,
            end_score=0,
            overall_coherence=0,
            narrative_flow_issues=["AI analysis unavailable - manual review required"],
            strengths=[]
        )

        return NarrativeReport(
            dashboard_name=dashboard_name,
            primary_metric=primary_metric,
            analysis_timestamp=datetime.now(),
            story_arc=story_arc,
            story_elements=[],
            current_narrative="AI analysis unavailable. Please review manually.",
            improved_narrative="AI analysis unavailable. Please review manually.",
            email_summary="AI analysis unavailable. Please review manually.",
            suggested_section_titles={},
            layout_recommendations=[],
            content_recommendations=[],
            overall_story_score=0,
            before_after_comparison={},
            metadata={
                'analysis_method': 'fallback',
                'reason': 'AI unavailable'
            }
        )

    def generate_before_after_outline(self, report: NarrativeReport) -> str:
        """
        Generate a before/after story outline

        Args:
            report: NarrativeReport from analysis

        Returns:
            Formatted text showing before/after comparison
        """
        outline = []
        outline.append("=" * 60)
        outline.append("DASHBOARD STORY: BEFORE & AFTER")
        outline.append("=" * 60)
        outline.append("")

        # Before
        outline.append("ð CURRENT STORY (Before)")
        outline.append("-" * 60)
        outline.append(f"Narrative: {report.current_narrative}")
        outline.append("")
        outline.append(f"Structure Score: {report.before_after_comparison.get('before', {}).get('narrative_clarity', 0):.0f}/100")
        outline.append(f"User Guidance: {report.before_after_comparison.get('before', {}).get('user_guidance', 0):.0f}/100")
        outline.append("")

        if report.story_arc.narrative_flow_issues:
            outline.append("Issues:")
            for issue in report.story_arc.narrative_flow_issues:
                outline.append(f"  â {issue}")
        outline.append("")

        # After
        outline.append("â¨ IMPROVED STORY (After)")
        outline.append("-" * 60)
        outline.append(f"Narrative: {report.improved_narrative}")
        outline.append("")
        outline.append(f"Structure Score: {report.before_after_comparison.get('after', {}).get('narrative_clarity', 0):.0f}/100")
        outline.append(f"User Guidance: {report.before_after_comparison.get('after', {}).get('user_guidance', 0):.0f}/100")
        outline.append("")

        # Recommendations
        outline.append("ð¯ KEY CHANGES")
        outline.append("-" * 60)

        high_priority = [r for r in report.layout_recommendations + report.content_recommendations if r.priority == 'high']
        for i, rec in enumerate(high_priority[:5], 1):
            outline.append(f"{i}. {rec.recommended_state}")
            outline.append(f"   Impact: {rec.expected_impact}")
            outline.append("")

        # Suggested sections
        if report.suggested_section_titles:
            outline.append("ð SUGGESTED SECTION TITLES")
            outline.append("-" * 60)
            for location, title in report.suggested_section_titles.items():
                outline.append(f"  {location.upper()}: \"{title}\"")

        return "\n".join(outline)

    def export_report(
        self,
        report: NarrativeReport,
        output_dir: str = "exports/story_coach"
    ) -> Dict[str, str]:
        """
        Export story coaching report in multiple formats

        Args:
            report: NarrativeReport to export
            output_dir: Directory for exports

        Returns:
            Dictionary of format -> file path
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in report.dashboard_name)
        base_name = f"story_coach_{safe_name}_{timestamp}"

        paths = {}

        # 1. JSON export
        json_path = Path(output_dir) / f"{base_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
        paths['json'] = str(json_path)

        # 2. Markdown report
        md_path = Path(output_dir) / f"{base_name}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(report))
        paths['markdown'] = str(md_path)

        # 3. Email draft
        email_path = Path(output_dir) / f"{base_name}_email.txt"
        with open(email_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_email_draft(report))
        paths['email'] = str(email_path)

        return paths

    def _generate_markdown_report(self, report: NarrativeReport) -> str:
        """Generate comprehensive markdown report"""

        lines = []
        lines.append(f"# Dashboard Story Coaching Report")
        lines.append(f"**Dashboard**: {report.dashboard_name}")
        lines.append(f"**Primary Metric**: {report.primary_metric}")
        lines.append(f"**Analyzed**: {report.analysis_timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Overall Story Score**: {report.overall_story_score:.0f}/100")
        lines.append("")

        # Story Arc Analysis
        lines.append("## ð Story Arc Analysis")
        lines.append("")
        lines.append(f"- **Beginning (Context)**: {'â' if report.story_arc.has_beginning else 'â'} ({report.story_arc.beginning_score:.0f}/100)")
        lines.append(f"- **Middle (Insights)**: {'â' if report.story_arc.has_middle else 'â'} ({report.story_arc.middle_score:.0f}/100)")
        lines.append(f"- **End (Actions)**: {'â' if report.story_arc.has_end else 'â'} ({report.story_arc.end_score:.0f}/100)")
        lines.append(f"- **Overall Coherence**: {report.story_arc.overall_coherence:.0f}/100")
        lines.append("")

        # Current vs Improved Narrative
        lines.append("## ð Narrative Comparison")
        lines.append("")
        lines.append("### Current Story")
        lines.append(report.current_narrative)
        lines.append("")
        lines.append("### Improved Story")
        lines.append(report.improved_narrative)
        lines.append("")

        # Recommendations
        lines.append("## ð¯ Recommendations")
        lines.append("")

        high_priority = [r for r in report.layout_recommendations + report.content_recommendations if r.priority == 'high']
        if high_priority:
            lines.append("### High Priority")
            for rec in high_priority:
                lines.append(f"- **Current**: {rec.current_state}")
                lines.append(f"  **Recommended**: {rec.recommended_state}")
                lines.append(f"  **Rationale**: {rec.rationale}")
                lines.append(f"  **Impact**: {rec.expected_impact}")
                lines.append("")

        # Suggested Section Titles
        if report.suggested_section_titles:
            lines.append("## ð Suggested Section Titles")
            lines.append("")
            for location, title in report.suggested_section_titles.items():
                lines.append(f"- **{location.title()}**: \"{title}\"")
            lines.append("")

        # Email Summary
        lines.append("## ð§ Email-Ready Summary")
        lines.append("")
        lines.append(report.email_summary)

        return "\n".join(lines)

    def _generate_email_draft(self, report: NarrativeReport) -> str:
        """Generate email draft"""

        lines = []
        lines.append(f"Subject: Dashboard Story Review - {report.dashboard_name}")
        lines.append("")
        lines.append(f"Hi [Stakeholder],")
        lines.append("")
        lines.append(report.email_summary)
        lines.append("")
        lines.append("Key recommendations:")

        high_priority = [r for r in report.layout_recommendations + report.content_recommendations if r.priority == 'high']
        for i, rec in enumerate(high_priority[:3], 1):
            lines.append(f"{i}. {rec.recommended_state}")

        lines.append("")
        lines.append("Let me know if you'd like to discuss these suggestions.")
        lines.append("")
        lines.append("Best,")
        lines.append("[Your Name]")

        return "\n".join(lines)


def analyze_dashboard_story(
    screenshot_path: str,
    primary_metric: str,
    dashboard_name: str = "Dashboard",
    context: Optional[str] = None
) -> NarrativeReport:
    """
    Convenience function to analyze dashboard storytelling

    Args:
        screenshot_path: Path to dashboard screenshot
        primary_metric: Main metric being displayed
        dashboard_name: Name of dashboard
        context: Optional context about purpose

    Returns:
        NarrativeReport with complete analysis
    """
    coach = DashboardStoryCoach()
    return coach.analyze_story_structure(
        screenshot_path=screenshot_path,
        primary_metric=primary_metric,
        dashboard_name=dashboard_name,
        context=context
    )


def export_story_report(
    report: NarrativeReport,
    output_dir: str = "exports/story_coach"
) -> Dict[str, str]:
    """
    Export story coaching report

    Args:
        report: NarrativeReport to export
        output_dir: Output directory

    Returns:
        Dict of format -> path
    """
    coach = DashboardStoryCoach()
    return coach.export_report(report, output_dir)


if __name__ == "__main__":
    # Example usage
    print("Dashboard Story Coach Module")
    print("=" * 60)
    print("")
    print("This module analyzes dashboard screenshots to evaluate")
    print("storytelling effectiveness and provide narrative coaching.")
    print("")
    print("Key features:")
    print("  - Story arc analysis (beginning, middle, end)")
    print("  - Narrative clarity scoring")
    print("  - Layout and content recommendations")
    print("  - Before/after story comparison")
    print("  - Email-ready summaries")
    print("")
    print("See examples/story_coach_example.py for usage examples.")
