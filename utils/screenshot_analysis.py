"""
Screenshot analysis module for Tableau dashboards
Provides AI-powered UX/accessibility analysis of dashboard screenshots
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import base64
import os

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

from config.settings import (
    SCREENSHOT_MAX_SIZE_MB,
    SCREENSHOT_MIN_DIMENSION,
    SCREENSHOT_ANALYSIS_ASPECTS,
    ANTHROPIC_MODEL,
    MAX_TOKENS,
    API_TIMEOUT
)


@dataclass
class ScreenshotAnalysis:
    """Results from screenshot analysis"""
    overall_score: float = 0.0  # 0-100 scale
    aspect_scores: Dict[str, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    accessibility_issues: List[str] = field(default_factory=list)
    detailed_feedback: Dict[str, str] = field(default_factory=dict)
    image_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'overall_score': self.overall_score,
            'aspect_scores': self.aspect_scores,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'recommendations': self.recommendations,
            'accessibility_issues': self.accessibility_issues,
            'detailed_feedback': self.detailed_feedback,
            'image_metadata': self.image_metadata,
            'timestamp': self.timestamp.isoformat()
        }


class DashboardScreenshotAnalyzer:
    """
    Analyze Tableau dashboard screenshots for UX and accessibility
    Uses Claude AI vision capabilities when available
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize screenshot analyzer

        Args:
            api_key: Anthropic API key (if None, will use environment variable)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        # Check if Anthropic client is available
        try:
            import anthropic
            self.anthropic = anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
            self.ai_available = self.client is not None
        except ImportError:
            self.anthropic = None
            self.client = None
            self.ai_available = False

    def analyze_screenshot(
        self,
        image_path: str,
        custom_aspects: Optional[List[str]] = None
    ) -> ScreenshotAnalysis:
        """
        Analyze dashboard screenshot

        Args:
            image_path: Path to screenshot image
            custom_aspects: Optional custom analysis aspects

        Returns:
            ScreenshotAnalysis with results
        """
        analysis = ScreenshotAnalysis()

        # Validate image
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Screenshot not found: {image_path}")

        # Get image metadata
        analysis.image_metadata = self._get_image_metadata(image_path)

        # Validate image size and dimensions
        self._validate_image(image_path, analysis.image_metadata)

        # If AI is available, perform AI analysis
        if self.ai_available:
            analysis = self._ai_analysis(image_path, custom_aspects or SCREENSHOT_ANALYSIS_ASPECTS)
        else:
            # Fallback to basic analysis
            analysis = self._basic_analysis(image_path, analysis)

        return analysis

    def _get_image_metadata(self, image_path: Path) -> Dict[str, Any]:
        """Extract image metadata"""
        metadata = {
            'filename': image_path.name,
            'file_size_bytes': image_path.stat().st_size,
            'file_size_mb': round(image_path.stat().st_size / (1024 * 1024), 2)
        }

        # Get image dimensions if PIL available
        if PIL_AVAILABLE:
            try:
                with Image.open(image_path) as img:
                    metadata['width'] = img.width
                    metadata['height'] = img.height
                    metadata['format'] = img.format
                    metadata['mode'] = img.mode
            except Exception as e:
                metadata['error'] = str(e)

        return metadata

    def _validate_image(self, image_path: Path, metadata: Dict[str, Any]):
        """Validate image meets requirements"""
        # Check file size
        if metadata['file_size_mb'] > SCREENSHOT_MAX_SIZE_MB:
            raise ValueError(
                f"Image too large: {metadata['file_size_mb']}MB "
                f"(max: {SCREENSHOT_MAX_SIZE_MB}MB)"
            )

        # Check dimensions
        if PIL_AVAILABLE and 'width' in metadata:
            if (metadata['width'] < SCREENSHOT_MIN_DIMENSION or
                metadata['height'] < SCREENSHOT_MIN_DIMENSION):
                raise ValueError(
                    f"Image too small: {metadata['width']}x{metadata['height']} "
                    f"(min: {SCREENSHOT_MIN_DIMENSION}px)"
                )

    def _ai_analysis(
        self,
        image_path: Path,
        aspects: List[str]
    ) -> ScreenshotAnalysis:
        """
        Perform AI-powered analysis using Claude

        Args:
            image_path: Path to screenshot
            aspects: Analysis aspects to evaluate

        Returns:
            ScreenshotAnalysis with AI feedback
        """
        analysis = ScreenshotAnalysis()

        # Encode image to base64
        image_data = self._encode_image(image_path)

        # Determine media type
        extension = image_path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(extension, 'image/png')

        # Build analysis prompt
        prompt = self._build_analysis_prompt(aspects)

        try:
            # Call Claude API with vision
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Parse response
            response_text = response.content[0].text
            analysis = self._parse_ai_response(response_text, aspects)

        except Exception as e:
            # Fallback to basic analysis on error
            analysis.recommendations.append(
                f"AI analysis failed: {str(e)}. Using basic analysis."
            )
            analysis = self._basic_analysis(image_path, analysis)

        return analysis

    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64"""
        with open(image_path, 'rb') as image_file:
            return base64.standard_b64encode(image_file.read()).decode('utf-8')

    def _build_analysis_prompt(self, aspects: List[str]) -> str:
        """Build prompt for AI analysis"""
        aspects_str = "\n".join([f"- {aspect.replace('_', ' ').title()}" for aspect in aspects])

        prompt = f"""You are a Tableau dashboard UX expert. Analyze this dashboard screenshot for the following aspects:

{aspects_str}

For each aspect, provide:
1. A score from 0-100
2. Specific observations
3. Actionable recommendations

Also identify:
- Overall strengths of the dashboard
- Areas for improvement
- Accessibility issues (color contrast, font sizes, etc.)
- Best practices being followed or violated

Format your response as follows:

OVERALL_SCORE: [0-100]

ASPECT_SCORES:
layout_clarity: [0-100]
label_readability: [0-100]
filter_placement: [0-100]
visual_clutter: [0-100]
accessibility: [0-100]
color_usage: [0-100]

STRENGTHS:
- [Strength 1]
- [Strength 2]
...

WEAKNESSES:
- [Weakness 1]
- [Weakness 2]
...

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
...

ACCESSIBILITY_ISSUES:
- [Issue 1]
- [Issue 2]
...

DETAILED_FEEDBACK:
layout_clarity: [Detailed feedback about layout]
label_readability: [Detailed feedback about labels]
...
"""
        return prompt

    def _parse_ai_response(self, response_text: str, aspects: List[str]) -> ScreenshotAnalysis:
        """Parse AI response into ScreenshotAnalysis"""
        analysis = ScreenshotAnalysis()

        lines = response_text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Parse sections
            if line.startswith('OVERALL_SCORE:'):
                try:
                    score = float(line.split(':')[1].strip())
                    analysis.overall_score = score
                except:
                    pass

            elif line.startswith('ASPECT_SCORES:'):
                current_section = 'aspect_scores'

            elif line.startswith('STRENGTHS:'):
                current_section = 'strengths'

            elif line.startswith('WEAKNESSES:'):
                current_section = 'weaknesses'

            elif line.startswith('RECOMMENDATIONS:'):
                current_section = 'recommendations'

            elif line.startswith('ACCESSIBILITY_ISSUES:'):
                current_section = 'accessibility_issues'

            elif line.startswith('DETAILED_FEEDBACK:'):
                current_section = 'detailed_feedback'

            elif line.startswith('-'):
                # List item
                item = line[1:].strip()
                if current_section == 'strengths':
                    analysis.strengths.append(item)
                elif current_section == 'weaknesses':
                    analysis.weaknesses.append(item)
                elif current_section == 'recommendations':
                    analysis.recommendations.append(item)
                elif current_section == 'accessibility_issues':
                    analysis.accessibility_issues.append(item)

            elif ':' in line and current_section == 'aspect_scores':
                # Aspect score
                try:
                    aspect, score = line.split(':', 1)
                    aspect = aspect.strip()
                    score = float(score.strip())
                    analysis.aspect_scores[aspect] = score
                except:
                    pass

            elif ':' in line and current_section == 'detailed_feedback':
                # Detailed feedback
                try:
                    aspect, feedback = line.split(':', 1)
                    aspect = aspect.strip()
                    feedback = feedback.strip()
                    analysis.detailed_feedback[aspect] = feedback
                except:
                    pass

        return analysis

    def _basic_analysis(
        self,
        image_path: Path,
        analysis: ScreenshotAnalysis
    ) -> ScreenshotAnalysis:
        """
        Perform basic analysis without AI (fallback)

        Args:
            image_path: Path to screenshot
            analysis: Existing analysis to populate

        Returns:
            ScreenshotAnalysis with basic metrics
        """
        if not PIL_AVAILABLE:
            analysis.recommendations.append(
                "Install Pillow (pip install pillow) for enhanced image analysis"
            )
            return analysis

        try:
            with Image.open(image_path) as img:
                # Basic image analysis
                width, height = img.size
                aspect_ratio = width / height

                # Analyze dimensions
                if aspect_ratio > 2.0:
                    analysis.weaknesses.append("Very wide aspect ratio may cause display issues")
                elif aspect_ratio < 0.5:
                    analysis.weaknesses.append("Very tall aspect ratio may cause display issues")
                else:
                    analysis.strengths.append("Good aspect ratio for dashboard viewing")

                # Analyze size
                if width >= 1920 and height >= 1080:
                    analysis.strengths.append("High resolution suitable for detailed dashboards")
                elif width < 800 or height < 600:
                    analysis.weaknesses.append("Low resolution may affect readability")

                # Color mode analysis
                if img.mode == 'RGB':
                    analysis.strengths.append("RGB color mode suitable for web display")
                elif img.mode == 'RGBA':
                    analysis.strengths.append("RGBA mode supports transparency")

                # Set placeholder scores
                analysis.overall_score = 75.0
                for aspect in SCREENSHOT_ANALYSIS_ASPECTS:
                    analysis.aspect_scores[aspect] = 75.0

                analysis.recommendations.append(
                    "For detailed UX analysis, enable AI mode with Anthropic API key"
                )

        except Exception as e:
            analysis.recommendations.append(f"Image analysis error: {str(e)}")

        return analysis


def generate_analysis_report(analysis: ScreenshotAnalysis) -> str:
    """
    Generate human-readable analysis report

    Args:
        analysis: ScreenshotAnalysis to report

    Returns:
        Formatted string report
    """
    report_lines = [
        "### Dashboard Screenshot Analysis Report",
        "",
        f"**Overall Score:** {analysis.overall_score:.1f}/100",
        ""
    ]

    # Aspect scores
    if analysis.aspect_scores:
        report_lines.append("**Aspect Scores:**")
        for aspect, score in sorted(analysis.aspect_scores.items(), key=lambda x: x[1], reverse=True):
            aspect_name = aspect.replace('_', ' ').title()
            report_lines.append(f"  - {aspect_name}: {score:.1f}/100")
        report_lines.append("")

    # Strengths
    if analysis.strengths:
        report_lines.append("**Strengths:**")
        for strength in analysis.strengths:
            report_lines.append(f"   {strength}")
        report_lines.append("")

    # Weaknesses
    if analysis.weaknesses:
        report_lines.append("**Areas for Improvement:**")
        for weakness in analysis.weaknesses:
            report_lines.append(f"    {weakness}")
        report_lines.append("")

    # Accessibility
    if analysis.accessibility_issues:
        report_lines.append("**Accessibility Issues:**")
        for issue in analysis.accessibility_issues:
            report_lines.append(f"    {issue}")
        report_lines.append("")

    # Recommendations
    if analysis.recommendations:
        report_lines.append("**Recommendations:**")
        for i, rec in enumerate(analysis.recommendations, 1):
            report_lines.append(f"  {i}. {rec}")
        report_lines.append("")

    # Metadata
    if analysis.image_metadata:
        report_lines.append("**Image Information:**")
        if 'width' in analysis.image_metadata:
            report_lines.append(
                f"  - Resolution: {analysis.image_metadata['width']}x{analysis.image_metadata['height']}px"
            )
        report_lines.append(f"  - File Size: {analysis.image_metadata.get('file_size_mb', 0):.2f} MB")

    return "\n".join(report_lines)


# Convenience function
def analyze_dashboard_screenshot(
    image_path: str,
    api_key: Optional[str] = None
) -> Tuple[ScreenshotAnalysis, str]:
    """
    One-line function to analyze dashboard screenshot

    Args:
        image_path: Path to screenshot image
        api_key: Optional Anthropic API key

    Returns:
        Tuple of (ScreenshotAnalysis, formatted report)
    """
    analyzer = DashboardScreenshotAnalyzer(api_key=api_key)
    analysis = analyzer.analyze_screenshot(image_path)
    report = generate_analysis_report(analysis)

    return analysis, report
