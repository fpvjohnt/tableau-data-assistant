"""
Report generation utilities
Create PDF and HTML reports from analysis results
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO
import base64

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# HTML templates
from jinja2 import Template

from config.settings import EXPORTS_DIR, PDF_PAGE_SIZE
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generate analysis reports in multiple formats"""

    def __init__(self, exports_dir: Path = EXPORTS_DIR):
        """
        Initialize report generator

        Args:
            exports_dir: Directory for exported reports
        """
        self.exports_dir = exports_dir
        self.exports_dir.mkdir(exist_ok=True)
        logger.info(f"Report generator initialized: {exports_dir}")

    def generate_pdf_report(
        self,
        filename: str,
        title: str,
        data_summary: Dict,
        quality_score: Optional[Dict] = None,
        statistical_analysis: Optional[Dict] = None,
        anomalies: Optional[List] = None,
        visualizations: Optional[List] = None
    ) -> Path:
        """
        Generate PDF report

        Args:
            filename: Output filename
            title: Report title
            data_summary: Data summary dictionary
            quality_score: Quality score results
            statistical_analysis: Statistical analysis results
            anomalies: List of detected anomalies
            visualizations: Visualization suggestions

        Returns:
            Path to generated PDF
        """
        pdf_path = self.exports_dir / f"{filename}.pdf"
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4 if PDF_PAGE_SIZE == "A4" else letter,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Container for the 'Flowable' objects
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Data Summary Section
        elements.append(Paragraph("Data Summary", heading_style))
        summary_data = [
            ['Metric', 'Value'],
            ['File Size', f"{data_summary.get('file_size_mb', 'N/A')} MB"],
            ['Rows', f"{data_summary.get('rows', 0):,}"],
            ['Columns', f"{data_summary.get('columns', 0)}"],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))

        # Quality Score Section
        if quality_score:
            elements.append(Paragraph("Data Quality Assessment", heading_style))

            # Overall score
            overall_score = quality_score.get('overall_score', 0)
            grade = quality_score.get('grade', 'N/A')
            rating = quality_score.get('rating', 'N/A')

            score_text = f"<b>Overall Score:</b> {overall_score:.1f}/100 (Grade: {grade} - {rating})"
            elements.append(Paragraph(score_text, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))

            # Dimension scores
            dimension_scores = quality_score.get('dimension_scores', {})
            score_data = [['Dimension', 'Score']]
            for dimension, score in dimension_scores.items():
                score_data.append([dimension.capitalize(), f"{score:.1f}"])

            score_table = Table(score_data, colWidths=[3*inch, 2*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(score_table)
            elements.append(Spacer(1, 0.2*inch))

            # Recommendations
            recommendations = quality_score.get('recommendations', [])
            if recommendations:
                elements.append(Paragraph("<b>Recommendations:</b>", styles['Normal']))
                for rec in recommendations:
                    elements.append(Paragraph(f"• {rec}", styles['Normal']))

            elements.append(Spacer(1, 0.3*inch))

        # Anomalies Section
        if anomalies:
            elements.append(Paragraph("Detected Anomalies", heading_style))

            for anomaly in anomalies[:20]:  # Limit to 20
                severity = anomaly.get('severity', 'unknown')
                description = anomaly.get('description', 'No description')
                elements.append(Paragraph(f"<b>[{severity.upper()}]</b> {description}", styles['Normal']))

            elements.append(Spacer(1, 0.3*inch))

        # Visualizations Section
        if visualizations:
            elements.append(Paragraph("Recommended Visualizations", heading_style))

            for viz in visualizations[:10]:  # Limit to 10
                viz_type = viz.get('viz_type', 'Unknown')
                use_case = viz.get('use_case', '')
                description = viz.get('description', '')

                elements.append(Paragraph(f"<b>{viz_type}</b> - {use_case}", styles['Normal']))
                elements.append(Paragraph(description, styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))

        # Build PDF
        try:
            doc.build(elements)
            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise

    def generate_html_report(
        self,
        filename: str,
        title: str,
        data_summary: Dict,
        quality_score: Optional[Dict] = None,
        statistical_analysis: Optional[Dict] = None,
        anomalies: Optional[List] = None,
        visualizations: Optional[List] = None
    ) -> Path:
        """
        Generate HTML report

        Args:
            filename: Output filename
            title: Report title
            data_summary: Data summary dictionary
            quality_score: Quality score results
            statistical_analysis: Statistical analysis results
            anomalies: List of detected anomalies
            visualizations: Visualization suggestions

        Returns:
            Path to generated HTML
        """
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }

        .meta {
            color: #7f8c8d;
            margin-bottom: 30px;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .summary-card {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
        }

        .summary-card .label {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }

        .summary-card .value {
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
        }

        .quality-score {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            margin: 20px 0;
        }

        .quality-score .score {
            font-size: 4em;
            font-weight: bold;
        }

        .quality-score .grade {
            font-size: 2em;
        }

        .dimension-scores {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .dimension-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }

        .dimension-card .name {
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
        }

        .dimension-card .score {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }

        .anomaly {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }

        .anomaly.high {
            background-color: #fee;
            border-color: #e74c3c;
        }

        .anomaly.medium {
            background-color: #fef5e7;
            border-color: #f39c12;
        }

        .anomaly.low {
            background-color: #eef;
            border-color: #3498db;
        }

        .viz-card {
            background-color: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #2ecc71;
        }

        .viz-card .viz-type {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .viz-card .use-case {
            color: #7f8c8d;
            font-style: italic;
            margin-bottom: 10px;
        }

        .recommendation {
            background-color: #e8f8f5;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #2ecc71;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }

        tr:hover {
            background-color: #f5f5f5;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <p class="meta">Generated: {{ timestamp }}</p>

        <h2>Data Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <div class="label">File Size</div>
                <div class="value">{{ data_summary.get('file_size_mb', 'N/A') }} MB</div>
            </div>
            <div class="summary-card">
                <div class="label">Rows</div>
                <div class="value">{{ "{:,}".format(data_summary.get('rows', 0)) }}</div>
            </div>
            <div class="summary-card">
                <div class="label">Columns</div>
                <div class="value">{{ data_summary.get('columns', 0) }}</div>
            </div>
        </div>

        {% if quality_score %}
        <h2>Data Quality Assessment</h2>
        <div class="quality-score">
            <div class="score">{{ "%.1f"|format(quality_score.get('overall_score', 0)) }}</div>
            <div class="grade">Grade: {{ quality_score.get('grade', 'N/A') }} - {{ quality_score.get('rating', 'N/A') }}</div>
        </div>

        <h3>Dimension Scores</h3>
        <div class="dimension-scores">
            {% for dimension, score in quality_score.get('dimension_scores', {}).items() %}
            <div class="dimension-card">
                <div class="name">{{ dimension }}</div>
                <div class="score">{{ "%.1f"|format(score) }}</div>
            </div>
            {% endfor %}
        </div>

        {% if quality_score.get('recommendations') %}
        <h3>Recommendations</h3>
        {% for rec in quality_score.get('recommendations', []) %}
        <div class="recommendation">{{ rec }}</div>
        {% endfor %}
        {% endif %}
        {% endif %}

        {% if anomalies %}
        <h2>Detected Anomalies</h2>
        {% for anomaly in anomalies[:20] %}
        <div class="anomaly {{ anomaly.get('severity', 'low') }}">
            <strong>[{{ anomaly.get('severity', 'unknown').upper() }}]</strong> {{ anomaly.get('description', 'No description') }}
        </div>
        {% endfor %}
        {% endif %}

        {% if visualizations %}
        <h2>Recommended Visualizations</h2>
        {% for viz in visualizations[:10] %}
        <div class="viz-card">
            <div class="viz-type">{{ viz.get('viz_type', 'Unknown') }}</div>
            <div class="use-case">{{ viz.get('use_case', '') }}</div>
            <p>{{ viz.get('description', '') }}</p>
        </div>
        {% endfor %}
        {% endif %}
    </div>
</body>
</html>
"""

        template = Template(html_template)
        html_content = template.render(
            title=title,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data_summary=data_summary,
            quality_score=quality_score,
            statistical_analysis=statistical_analysis,
            anomalies=anomalies,
            visualizations=visualizations
        )

        html_path = self.exports_dir / f"{filename}.html"
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML report generated: {html_path}")
            return html_path
        except Exception as e:
            logger.error(f"Failed to generate HTML: {e}")
            raise

    def create_batch_download_zip(self, files: Dict[str, pd.DataFrame], zip_name: str) -> Path:
        """
        Create ZIP file with multiple cleaned datasets

        Args:
            files: Dictionary of filename -> DataFrame
            zip_name: Name for ZIP file

        Returns:
            Path to ZIP file
        """
        import zipfile

        zip_path = self.exports_dir / f"{zip_name}.zip"

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, df in files.items():
                    # Create CSV in memory
                    csv_buffer = BytesIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)

                    # Add to ZIP
                    zipf.writestr(f"cleaned_{filename}", csv_buffer.getvalue())

            logger.info(f"Batch ZIP created: {zip_path} ({len(files)} files)")
            return zip_path
        except Exception as e:
            logger.error(f"Failed to create batch ZIP: {e}")
            raise


# Global report generator instance
_report_generator = ReportGenerator()


def get_report_generator() -> ReportGenerator:
    """Get global report generator instance"""
    return _report_generator
