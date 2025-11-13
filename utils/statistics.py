"""
Statistical analysis utilities
Provides advanced statistical tests and analysis for data exploration
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.stats import normaltest, shapiro, kstest, pearsonr, spearmanr

from config.settings import CORRELATION_THRESHOLD, NORMALITY_TEST_ALPHA
from utils.logger import get_logger

logger = get_logger(__name__)


class StatisticalAnalyzer:
    """Perform statistical analysis on datasets"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize statistical analyzer

        Args:
            df: DataFrame to analyze
        """
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    def test_normality(self, column: str) -> Dict:
        """
        Test if a column follows normal distribution

        Args:
            column: Column name to test

        Returns:
            Dictionary with test results
        """
        if column not in self.numeric_cols:
            return {'error': 'Column must be numeric'}

        data = self.df[column].dropna()
        if len(data) < 8:
            return {'error': 'Insufficient data for normality test (minimum 8 values)'}

        results = {
            'column': column,
            'sample_size': len(data),
            'tests': {}
        }

        # Shapiro-Wilk test (best for n < 5000)
        if len(data) < 5000:
            try:
                statistic, p_value = shapiro(data)
                results['tests']['shapiro_wilk'] = {
                    'statistic': float(statistic),
                    'p_value': float(p_value),
                    'is_normal': p_value > NORMALITY_TEST_ALPHA,
                    'interpretation': 'Normal distribution' if p_value > NORMALITY_TEST_ALPHA else 'Not normal distribution'
                }
            except Exception as e:
                logger.warning(f"Shapiro-Wilk test failed: {e}")

        # D'Agostino-Pearson test
        try:
            statistic, p_value = normaltest(data)
            results['tests']['dagostino_pearson'] = {
                'statistic': float(statistic),
                'p_value': float(p_value),
                'is_normal': p_value > NORMALITY_TEST_ALPHA,
                'interpretation': 'Normal distribution' if p_value > NORMALITY_TEST_ALPHA else 'Not normal distribution'
            }
        except Exception as e:
            logger.warning(f"D'Agostino-Pearson test failed: {e}")

        # Kolmogorov-Smirnov test
        try:
            # Normalize data for K-S test
            normalized = (data - data.mean()) / data.std()
            statistic, p_value = kstest(normalized, 'norm')
            results['tests']['kolmogorov_smirnov'] = {
                'statistic': float(statistic),
                'p_value': float(p_value),
                'is_normal': p_value > NORMALITY_TEST_ALPHA,
                'interpretation': 'Normal distribution' if p_value > NORMALITY_TEST_ALPHA else 'Not normal distribution'
            }
        except Exception as e:
            logger.warning(f"Kolmogorov-Smirnov test failed: {e}")

        # Overall conclusion
        normal_count = sum(
            1 for test in results['tests'].values()
            if test.get('is_normal', False)
        )
        total_tests = len(results['tests'])

        results['conclusion'] = {
            'likely_normal': normal_count >= (total_tests / 2),
            'consensus': f"{normal_count}/{total_tests} tests suggest normal distribution"
        }

        logger.debug(f"Normality test for {column}: {results['conclusion']['consensus']}")
        return results

    def calculate_correlations(self, method: str = 'pearson') -> Dict:
        """
        Calculate correlation matrix for numeric columns

        Args:
            method: Correlation method ('pearson', 'spearman', 'kendall')

        Returns:
            Dictionary with correlation results
        """
        if len(self.numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for correlation analysis'}

        # Calculate correlation matrix
        corr_matrix = self.df[self.numeric_cols].corr(method=method)

        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]

                if abs(corr_value) >= CORRELATION_THRESHOLD:
                    # Calculate p-value for significance
                    if method == 'pearson':
                        _, p_value = pearsonr(
                            self.df[col1].dropna(),
                            self.df[col2].dropna()
                        )
                    else:
                        _, p_value = spearmanr(
                            self.df[col1].dropna(),
                            self.df[col2].dropna()
                        )

                    strong_correlations.append({
                        'column1': col1,
                        'column2': col2,
                        'correlation': float(corr_value),
                        'p_value': float(p_value),
                        'strength': 'Strong positive' if corr_value >= CORRELATION_THRESHOLD else 'Strong negative',
                        'significant': p_value < 0.05
                    })

        results = {
            'method': method,
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'summary': f"Found {len(strong_correlations)} strong correlations (|r| >= {CORRELATION_THRESHOLD})"
        }

        logger.info(f"Correlation analysis ({method}): {len(strong_correlations)} strong correlations found")
        return results

    def detect_outliers_zscore(self, column: str, threshold: float = 3.0) -> Dict:
        """
        Detect outliers using z-score method

        Args:
            column: Column name
            threshold: Z-score threshold (default 3.0)

        Returns:
            Dictionary with outlier information
        """
        if column not in self.numeric_cols:
            return {'error': 'Column must be numeric'}

        data = self.df[column].dropna()
        if len(data) == 0:
            return {'error': 'No data to analyze'}

        # Calculate z-scores
        z_scores = np.abs(stats.zscore(data))
        outliers = z_scores > threshold

        outlier_indices = data[outliers].index.tolist()
        outlier_values = data[outliers].tolist()

        results = {
            'column': column,
            'method': 'z-score',
            'threshold': threshold,
            'total_values': len(data),
            'outlier_count': int(outliers.sum()),
            'outlier_percentage': round((outliers.sum() / len(data)) * 100, 2),
            'outlier_values': [float(v) for v in outlier_values[:20]],  # Limit to 20
            'statistics': {
                'mean': float(data.mean()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max())
            }
        }

        logger.debug(f"Z-score outlier detection for {column}: {results['outlier_count']} outliers")
        return results

    def perform_t_test(self, column: str, group_column: str) -> Dict:
        """
        Perform independent t-test between two groups

        Args:
            column: Numeric column to test
            group_column: Categorical column defining groups

        Returns:
            Dictionary with t-test results
        """
        if column not in self.numeric_cols:
            return {'error': 'Column must be numeric'}

        if group_column not in self.df.columns:
            return {'error': 'Group column not found'}

        groups = self.df[group_column].unique()
        if len(groups) != 2:
            return {'error': 'Group column must have exactly 2 unique values'}

        group1_data = self.df[self.df[group_column] == groups[0]][column].dropna()
        group2_data = self.df[self.df[group_column] == groups[1]][column].dropna()

        if len(group1_data) < 2 or len(group2_data) < 2:
            return {'error': 'Insufficient data in groups'}

        # Perform t-test
        t_statistic, p_value = stats.ttest_ind(group1_data, group2_data)

        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(group1_data) - 1) * group1_data.std() ** 2 +
             (len(group2_data) - 1) * group2_data.std() ** 2) /
            (len(group1_data) + len(group2_data) - 2)
        )
        cohens_d = (group1_data.mean() - group2_data.mean()) / pooled_std

        results = {
            'column': column,
            'group_column': group_column,
            'groups': {
                str(groups[0]): {
                    'n': len(group1_data),
                    'mean': float(group1_data.mean()),
                    'std': float(group1_data.std())
                },
                str(groups[1]): {
                    'n': len(group2_data),
                    'mean': float(group2_data.mean()),
                    'std': float(group2_data.std())
                }
            },
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'cohens_d': float(cohens_d),
            'effect_size': 'Small' if abs(cohens_d) < 0.5 else 'Medium' if abs(cohens_d) < 0.8 else 'Large',
            'interpretation': f"Groups are {'significantly' if p_value < 0.05 else 'not significantly'} different (p={p_value:.4f})"
        }

        logger.info(f"T-test {column} by {group_column}: p={p_value:.4f}, d={cohens_d:.2f}")
        return results

    def chi_square_test(self, col1: str, col2: str) -> Dict:
        """
        Perform chi-square test of independence

        Args:
            col1: First categorical column
            col2: Second categorical column

        Returns:
            Dictionary with chi-square results
        """
        if col1 not in self.df.columns or col2 not in self.df.columns:
            return {'error': 'Columns not found'}

        # Create contingency table
        contingency_table = pd.crosstab(self.df[col1], self.df[col2])

        # Perform chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        # Calculate Cramér's V (effect size)
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)
        cramers_v = np.sqrt(chi2 / (n * min_dim))

        results = {
            'column1': col1,
            'column2': col2,
            'chi2_statistic': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'cramers_v': float(cramers_v),
            'significant': p_value < 0.05,
            'effect_size': 'Small' if cramers_v < 0.3 else 'Medium' if cramers_v < 0.5 else 'Large',
            'interpretation': f"Variables are {'significantly' if p_value < 0.05 else 'not significantly'} associated (p={p_value:.4f})",
            'contingency_table': contingency_table.to_dict()
        }

        logger.info(f"Chi-square test {col1} vs {col2}: p={p_value:.4f}, V={cramers_v:.2f}")
        return results

    def comprehensive_analysis(self) -> Dict:
        """
        Perform comprehensive statistical analysis

        Returns:
            Dictionary with all analysis results
        """
        logger.info("Starting comprehensive statistical analysis...")

        analysis = {
            'summary': {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'numeric_columns': len(self.numeric_cols),
                'categorical_columns': len(self.categorical_cols),
                'datetime_columns': len(self.datetime_cols)
            },
            'normality_tests': {},
            'correlations': {},
            'outliers': {},
            'recommendations': []
        }

        # Test normality for all numeric columns
        for col in self.numeric_cols[:10]:  # Limit to first 10
            analysis['normality_tests'][col] = self.test_normality(col)

        # Calculate correlations
        if len(self.numeric_cols) >= 2:
            analysis['correlations']['pearson'] = self.calculate_correlations('pearson')
            analysis['correlations']['spearman'] = self.calculate_correlations('spearman')

        # Detect outliers
        for col in self.numeric_cols[:10]:  # Limit to first 10
            analysis['outliers'][col] = self.detect_outliers_zscore(col)

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        logger.info("Comprehensive statistical analysis completed")
        return analysis

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Normality recommendations
        non_normal_cols = [
            col for col, result in analysis['normality_tests'].items()
            if not result.get('conclusion', {}).get('likely_normal', True)
        ]
        if non_normal_cols:
            recommendations.append(
                f"📊 {len(non_normal_cols)} columns are not normally distributed - consider non-parametric tests or transformations"
            )

        # Correlation recommendations
        strong_corrs = analysis['correlations'].get('pearson', {}).get('strong_correlations', [])
        if strong_corrs:
            recommendations.append(
                f"🔗 Found {len(strong_corrs)} strong correlations - consider for multicollinearity or feature engineering"
            )

        # Outlier recommendations
        cols_with_outliers = [
            col for col, result in analysis['outliers'].items()
            if result.get('outlier_percentage', 0) > 5
        ]
        if cols_with_outliers:
            recommendations.append(
                f"⚠️ {len(cols_with_outliers)} columns have >5% outliers - investigate for data quality issues"
            )

        if not recommendations:
            recommendations.append("✅ Statistical profile looks good - data is ready for analysis")

        return recommendations


def perform_statistical_analysis(df: pd.DataFrame) -> Dict:
    """
    Convenience function for comprehensive statistical analysis

    Args:
        df: DataFrame to analyze

    Returns:
        Analysis results dictionary
    """
    analyzer = StatisticalAnalyzer(df)
    return analyzer.comprehensive_analysis()
