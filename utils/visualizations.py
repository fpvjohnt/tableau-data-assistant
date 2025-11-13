"""
Interactive visualization utilities using Plotly
Create beautiful, interactive charts for data profiling
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
from plotly.subplots import make_subplots

from utils.logger import get_logger

logger = get_logger(__name__)


class DataVisualizer:
    """Create interactive visualizations for data profiling"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize visualizer

        Args:
            df: DataFrame to visualize
        """
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    def create_quality_gauge(self, quality_score: Dict) -> go.Figure:
        """
        Create gauge chart for overall quality score

        Args:
            quality_score: Quality score dictionary

        Returns:
            Plotly figure
        """
        overall_score = quality_score.get('overall_score', 0)
        grade = quality_score.get('grade', 'N/A')

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=overall_score,
            title={'text': f"Data Quality Score<br><span style='font-size:0.8em'>Grade: {grade}</span>"},
            delta={'reference': 80, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'size': 14}
        )

        return fig

    def create_dimension_scores_bar(self, quality_score: Dict) -> go.Figure:
        """
        Create bar chart for dimension scores

        Args:
            quality_score: Quality score dictionary

        Returns:
            Plotly figure
        """
        dimension_scores = quality_score.get('dimension_scores', {})

        dimensions = list(dimension_scores.keys())
        scores = list(dimension_scores.values())

        # Color code based on score
        colors_list = ['green' if s >= 80 else 'orange' if s >= 60 else 'red' for s in scores]

        fig = go.Figure(data=[
            go.Bar(
                x=[d.capitalize() for d in dimensions],
                y=scores,
                marker_color=colors_list,
                text=[f'{s:.1f}' for s in scores],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title="Quality Dimensions Breakdown",
            xaxis_title="Dimension",
            yaxis_title="Score",
            yaxis=dict(range=[0, 105]),
            height=400,
            showlegend=False,
            hovermode='x'
        )

        return fig

    def create_missing_values_heatmap(self) -> go.Figure:
        """
        Create heatmap showing missing values pattern

        Returns:
            Plotly figure
        """
        # Calculate missing values
        missing_data = self.df.isnull().astype(int)

        # Sample if too many rows
        if len(missing_data) > 1000:
            missing_data = missing_data.sample(n=1000, random_state=42).sort_index()

        fig = go.Figure(data=go.Heatmap(
            z=missing_data.T.values,
            x=missing_data.index,
            y=missing_data.columns,
            colorscale=[[0, '#2ecc71'], [1, '#e74c3c']],
            showscale=True,
            colorbar=dict(
                title="Missing",
                tickvals=[0, 1],
                ticktext=['Present', 'Missing']
            )
        ))

        fig.update_layout(
            title="Missing Values Pattern",
            xaxis_title="Row Index",
            yaxis_title="Columns",
            height=max(400, len(self.df.columns) * 20),
            xaxis={'side': 'bottom'}
        )

        return fig

    def create_correlation_heatmap(self, method: str = 'pearson') -> Optional[go.Figure]:
        """
        Create correlation heatmap for numeric columns

        Args:
            method: Correlation method

        Returns:
            Plotly figure or None
        """
        if len(self.numeric_cols) < 2:
            return None

        corr_matrix = self.df[self.numeric_cols].corr(method=method)

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))

        fig.update_layout(
            title=f"Correlation Matrix ({method.capitalize()})",
            height=max(500, len(self.numeric_cols) * 40),
            xaxis={'side': 'bottom'},
            yaxis={'autorange': 'reversed'}
        )

        return fig

    def create_distribution_plots(self, max_cols: int = 6) -> go.Figure:
        """
        Create distribution plots for numeric columns

        Args:
            max_cols: Maximum number of columns to plot

        Returns:
            Plotly figure
        """
        cols_to_plot = self.numeric_cols[:max_cols]
        n_cols = len(cols_to_plot)

        if n_cols == 0:
            return None

        # Create subplots
        rows = (n_cols + 2) // 3
        fig = make_subplots(
            rows=rows,
            cols=min(3, n_cols),
            subplot_titles=[f"{col}" for col in cols_to_plot]
        )

        for idx, col in enumerate(cols_to_plot):
            row = (idx // 3) + 1
            col_pos = (idx % 3) + 1

            data = self.df[col].dropna()

            fig.add_trace(
                go.Histogram(
                    x=data,
                    name=col,
                    nbinsx=30,
                    marker_color='#3498db',
                    showlegend=False
                ),
                row=row,
                col=col_pos
            )

        fig.update_layout(
            title_text="Distribution of Numeric Columns",
            height=300 * rows,
            showlegend=False
        )

        return fig

    def create_outlier_boxplots(self, max_cols: int = 6) -> Optional[go.Figure]:
        """
        Create box plots for outlier detection

        Args:
            max_cols: Maximum number of columns to plot

        Returns:
            Plotly figure or None
        """
        cols_to_plot = self.numeric_cols[:max_cols]

        if not cols_to_plot:
            return None

        fig = go.Figure()

        for col in cols_to_plot:
            fig.add_trace(go.Box(
                y=self.df[col].dropna(),
                name=col,
                boxmean='sd'
            ))

        fig.update_layout(
            title="Box Plots for Outlier Detection",
            yaxis_title="Value",
            height=500,
            showlegend=True
        )

        return fig

    def create_categorical_bar_charts(self, max_cols: int = 4) -> Optional[go.Figure]:
        """
        Create bar charts for categorical columns

        Args:
            max_cols: Maximum number of columns to plot

        Returns:
            Plotly figure or None
        """
        # Filter categorical columns with reasonable cardinality
        cols_to_plot = [
            col for col in self.categorical_cols[:max_cols]
            if self.df[col].nunique() <= 20
        ]

        if not cols_to_plot:
            return None

        n_cols = len(cols_to_plot)
        rows = (n_cols + 1) // 2

        fig = make_subplots(
            rows=rows,
            cols=2,
            subplot_titles=cols_to_plot,
            specs=[[{'type': 'bar'}] * 2] * rows
        )

        for idx, col in enumerate(cols_to_plot):
            row = (idx // 2) + 1
            col_pos = (idx % 2) + 1

            value_counts = self.df[col].value_counts().head(10)

            fig.add_trace(
                go.Bar(
                    x=value_counts.index.astype(str),
                    y=value_counts.values,
                    name=col,
                    marker_color='#2ecc71',
                    showlegend=False
                ),
                row=row,
                col=col_pos
            )

        fig.update_layout(
            title_text="Top Values in Categorical Columns",
            height=400 * rows,
            showlegend=False
        )

        return fig

    def create_time_series_plot(self, value_col: Optional[str] = None) -> Optional[go.Figure]:
        """
        Create time series plot if datetime column exists

        Args:
            value_col: Numeric column to plot (uses first if None)

        Returns:
            Plotly figure or None
        """
        if not self.datetime_cols or not self.numeric_cols:
            return None

        date_col = self.datetime_cols[0]
        if value_col is None:
            value_col = self.numeric_cols[0]

        # Sort by date
        plot_df = self.df[[date_col, value_col]].dropna().sort_values(date_col)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=plot_df[date_col],
            y=plot_df[value_col],
            mode='lines',
            name=value_col,
            line=dict(color='#3498db', width=2)
        ))

        fig.update_layout(
            title=f"Time Series: {value_col} over {date_col}",
            xaxis_title=date_col,
            yaxis_title=value_col,
            height=400,
            hovermode='x unified'
        )

        return fig

    def create_data_profile_dashboard(self, quality_score: Dict) -> Dict[str, go.Figure]:
        """
        Create comprehensive dashboard with all visualizations

        Args:
            quality_score: Quality score dictionary

        Returns:
            Dictionary of figure names to Plotly figures
        """
        dashboard = {}

        logger.info("Creating data profile visualizations...")

        # Quality gauge
        dashboard['quality_gauge'] = self.create_quality_gauge(quality_score)

        # Dimension scores
        dashboard['dimension_scores'] = self.create_dimension_scores_bar(quality_score)

        # Missing values heatmap (sample if large)
        if self.df.isnull().any().any():
            dashboard['missing_values'] = self.create_missing_values_heatmap()

        # Correlation heatmap
        corr_fig = self.create_correlation_heatmap()
        if corr_fig:
            dashboard['correlations'] = corr_fig

        # Distribution plots
        dist_fig = self.create_distribution_plots()
        if dist_fig:
            dashboard['distributions'] = dist_fig

        # Outlier box plots
        box_fig = self.create_outlier_boxplots()
        if box_fig:
            dashboard['boxplots'] = box_fig

        # Categorical bar charts
        cat_fig = self.create_categorical_bar_charts()
        if cat_fig:
            dashboard['categorical'] = cat_fig

        # Time series
        ts_fig = self.create_time_series_plot()
        if ts_fig:
            dashboard['timeseries'] = ts_fig

        logger.info(f"Created {len(dashboard)} visualizations")
        return dashboard


def create_visualizations(df: pd.DataFrame, quality_score: Dict) -> Dict[str, go.Figure]:
    """
    Convenience function to create all visualizations

    Args:
        df: DataFrame to visualize
        quality_score: Quality score dictionary

    Returns:
        Dictionary of visualizations
    """
    visualizer = DataVisualizer(df)
    return visualizer.create_data_profile_dashboard(quality_score)
