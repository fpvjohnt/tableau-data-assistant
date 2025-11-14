"""
SQL utilities for Tableau data source optimization
Provides query generation, optimization hints, and best practices
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import re


@dataclass
class SQLOptimizationReport:
    """Report of SQL optimization suggestions"""
    original_query: str = ""
    optimized_query: str = ""
    suggestions: List[str] = field(default_factory=list)
    performance_tips: List[str] = field(default_factory=list)
    tableau_specific_tips: List[str] = field(default_factory=list)
    estimated_improvement: str = "Unknown"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'original_query': self.original_query,
            'optimized_query': self.optimized_query,
            'suggestions': self.suggestions,
            'performance_tips': self.performance_tips,
            'tableau_specific_tips': self.tableau_specific_tips,
            'estimated_improvement': self.estimated_improvement,
            'timestamp': self.timestamp.isoformat()
        }


class TableauSQLGenerator:
    """
    Generate SQL queries optimized for Tableau data sources
    Provides best practices for live connections and extracts
    """

    def __init__(self, database_type: str = 'generic'):
        """
        Initialize SQL generator

        Args:
            database_type: Type of database ('postgres', 'mysql', 'sqlserver', 'redshift', 'snowflake', 'generic')
        """
        self.database_type = database_type.lower()

    def generate_select_query(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order_by: Optional[List[str]] = None,
        aggregations: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate optimized SELECT query for Tableau

        Args:
            table_name: Table name
            columns: List of columns to select (None for all)
            filters: Dictionary of column: value filters
            limit: Row limit
            order_by: List of columns to order by
            aggregations: Dictionary of column: function ('SUM', 'AVG', etc.)

        Returns:
            SQL query string
        """
        # Build SELECT clause
        if aggregations:
            select_parts = []
            for col, func in aggregations.items():
                select_parts.append(f"{func}({col}) AS {col}_{func.lower()}")
            select_clause = ", ".join(select_parts)
        elif columns:
            select_clause = ", ".join(columns)
        else:
            select_clause = "*"

        query = f"SELECT {select_clause}\nFROM {table_name}"

        # Add WHERE clause
        if filters:
            where_parts = []
            for col, value in filters.items():
                if isinstance(value, str):
                    where_parts.append(f"{col} = '{value}'")
                elif isinstance(value, (int, float)):
                    where_parts.append(f"{col} = {value}")
                elif isinstance(value, list):
                    # IN clause
                    values_str = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                    where_parts.append(f"{col} IN ({values_str})")

            if where_parts:
                query += "\nWHERE " + " AND ".join(where_parts)

        # Add ORDER BY
        if order_by:
            query += "\nORDER BY " + ", ".join(order_by)

        # Add LIMIT
        if limit:
            if self.database_type in ['postgres', 'mysql', 'redshift', 'snowflake']:
                query += f"\nLIMIT {limit}"
            elif self.database_type == 'sqlserver':
                # SQL Server uses TOP
                query = query.replace("SELECT", f"SELECT TOP {limit}", 1)

        return query

    def generate_aggregation_query(
        self,
        table_name: str,
        group_by: List[str],
        metrics: Dict[str, str],
        filters: Optional[Dict[str, Any]] = None,
        having: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate aggregation query optimized for Tableau

        Args:
            table_name: Table name
            group_by: Columns to group by
            metrics: Dictionary of column: aggregation function
            filters: WHERE clause filters
            having: HAVING clause filters

        Returns:
            SQL query string
        """
        # Build SELECT with dimensions and metrics
        select_parts = group_by.copy()

        for col, func in metrics.items():
            select_parts.append(f"{func}({col}) AS {col}_{func.lower()}")

        select_clause = ", ".join(select_parts)
        query = f"SELECT {select_clause}\nFROM {table_name}"

        # WHERE clause
        if filters:
            where_parts = []
            for col, value in filters.items():
                if isinstance(value, str):
                    where_parts.append(f"{col} = '{value}'")
                elif isinstance(value, (int, float)):
                    where_parts.append(f"{col} = {value}")

            if where_parts:
                query += "\nWHERE " + " AND ".join(where_parts)

        # GROUP BY
        query += "\nGROUP BY " + ", ".join(group_by)

        # HAVING clause
        if having:
            having_parts = []
            for col, value in having.items():
                having_parts.append(f"{col} > {value}")

            if having_parts:
                query += "\nHAVING " + " AND ".join(having_parts)

        return query

    def generate_extract_query(
        self,
        table_name: str,
        date_column: Optional[str] = None,
        lookback_days: int = 365,
        incremental: bool = False
    ) -> str:
        """
        Generate query for Tableau extract creation

        Args:
            table_name: Table name
            date_column: Date column for filtering (if incremental)
            lookback_days: Days of historical data to include
            incremental: Whether to support incremental refresh

        Returns:
            SQL query string
        """
        query = f"SELECT *\nFROM {table_name}"

        if date_column and incremental:
            if self.database_type in ['postgres', 'mysql', 'redshift']:
                query += f"\nWHERE {date_column} >= CURRENT_DATE - INTERVAL '{lookback_days} days'"
            elif self.database_type == 'sqlserver':
                query += f"\nWHERE {date_column} >= DATEADD(day, -{lookback_days}, GETDATE())"
            elif self.database_type == 'snowflake':
                query += f"\nWHERE {date_column} >= DATEADD(day, -{lookback_days}, CURRENT_DATE())"

        return query


class SQLOptimizer:
    """
    Analyze and optimize SQL queries for Tableau performance
    """

    def __init__(self):
        """Initialize SQL optimizer"""
        pass

    def optimize_query(self, query: str) -> SQLOptimizationReport:
        """
        Analyze and optimize SQL query

        Args:
            query: SQL query to optimize

        Returns:
            SQLOptimizationReport with suggestions
        """
        report = SQLOptimizationReport()
        report.original_query = query

        query_upper = query.upper()
        optimized = query

        # Check for SELECT *
        if 'SELECT *' in query_upper:
            report.suggestions.append(
                "Replace SELECT * with explicit column names to reduce data transfer"
            )
            report.performance_tips.append(
                "Tableau performs better with fewer columns - select only what you need"
            )

        # Check for missing WHERE clause on large tables
        if 'WHERE' not in query_upper and 'LIMIT' not in query_upper:
            report.suggestions.append(
                "Consider adding WHERE clause or LIMIT to reduce result set size"
            )
            report.tableau_specific_tips.append(
                "Large result sets can slow down Tableau dashboards - filter data at the source"
            )

        # Check for DISTINCT
        if 'DISTINCT' in query_upper:
            report.performance_tips.append(
                "DISTINCT can be expensive - consider if it's necessary or if duplicates can be handled in Tableau"
            )

        # Check for complex subqueries
        subquery_count = query_upper.count('SELECT') - 1
        if subquery_count > 2:
            report.suggestions.append(
                f"Query contains {subquery_count} subqueries - consider simplifying or using CTEs"
            )

        # Check for missing indexes hints (for supported databases)
        if 'JOIN' in query_upper:
            report.performance_tips.append(
                "Ensure JOIN columns are indexed in the database for better performance"
            )
            report.tableau_specific_tips.append(
                "For live connections, optimize JOIN performance at the database level"
            )

        # Check for aggregations
        if any(agg in query_upper for agg in ['SUM(', 'COUNT(', 'AVG(', 'MAX(', 'MIN(']):
            report.tableau_specific_tips.append(
                "Consider letting Tableau handle aggregations for more flexible analysis"
            )

        # Check for ORDER BY
        if 'ORDER BY' in query_upper and 'LIMIT' not in query_upper:
            report.performance_tips.append(
                "ORDER BY without LIMIT can be expensive - let Tableau handle sorting when possible"
            )

        # Suggest materialized views for complex queries
        if subquery_count > 1 or 'JOIN' in query_upper:
            report.tableau_specific_tips.append(
                "For frequently used complex queries, consider creating a materialized view or Tableau extract"
            )

        # Generate optimized query (basic optimizations)
        optimized = self._apply_basic_optimizations(query)
        report.optimized_query = optimized

        # Estimate improvement
        if len(report.suggestions) == 0:
            report.estimated_improvement = "Query is already well-optimized"
        elif len(report.suggestions) <= 2:
            report.estimated_improvement = "10-30% potential improvement"
        else:
            report.estimated_improvement = "30-70% potential improvement"

        return report

    def _apply_basic_optimizations(self, query: str) -> str:
        """Apply basic automatic optimizations"""
        optimized = query

        # Add comment suggesting improvements
        if 'SELECT *' in query.upper():
            optimized = "-- TODO: Replace SELECT * with explicit columns\n" + optimized

        return optimized

    def suggest_indexes(self, df: pd.DataFrame) -> List[str]:
        """
        Suggest database indexes based on DataFrame analysis

        Args:
            df: DataFrame representing the data

        Returns:
            List of index suggestions
        """
        suggestions = []

        # Check for ID columns (likely primary keys)
        id_cols = [col for col in df.columns if 'id' in col.lower()]
        for col in id_cols:
            if df[col].nunique() / len(df) > 0.95:  # High cardinality
                suggestions.append(f"CREATE INDEX idx_{col} ON table_name({col});")

        # Check for date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns
        for col in date_cols:
            suggestions.append(
                f"CREATE INDEX idx_{col} ON table_name({col}); -- For date range filters"
            )

        # Check for foreign key candidates
        for col in df.select_dtypes(include=['int64']).columns:
            if col not in id_cols:
                cardinality_ratio = df[col].nunique() / len(df)
                if 0.01 < cardinality_ratio < 0.5:  # Potential foreign key
                    suggestions.append(
                        f"-- Consider indexing {col} if it's a foreign key\n"
                        f"CREATE INDEX idx_{col} ON table_name({col});"
                    )

        return suggestions


class TableauCustomSQLHelper:
    """
    Helper for writing Tableau custom SQL data sources
    Provides templates and best practices
    """

    @staticmethod
    def generate_initial_sql_template(table_name: str) -> str:
        """Generate Tableau custom SQL template"""
        return f"""-- Tableau Custom SQL Template
-- Replace placeholders with your actual table/column names

SELECT
    -- Dimensions
    dimension1,
    dimension2,
    date_column,

    -- Measures
    SUM(measure1) AS total_measure1,
    AVG(measure2) AS avg_measure2,
    COUNT(DISTINCT id_column) AS count_distinct_id

FROM {table_name}

-- Optional: Add filters to reduce data volume
WHERE date_column >= CURRENT_DATE - INTERVAL '90 days'

-- Optional: Group by dimensions if pre-aggregating
GROUP BY
    dimension1,
    dimension2,
    date_column

-- Best Practices:
-- 1. Select only needed columns
-- 2. Filter data at source when possible
-- 3. Use meaningful aliases for calculated fields
-- 4. Consider date ranges to limit data volume
-- 5. Index JOIN columns in database
"""

    @staticmethod
    def generate_incremental_extract_sql(
        table_name: str,
        date_column: str,
        id_column: str
    ) -> str:
        """Generate SQL for Tableau incremental extract"""
        return f"""-- Tableau Incremental Extract SQL
-- Supports incremental refresh based on date

SELECT *
FROM {table_name}
WHERE {date_column} >= DATEADD(day, -7, CURRENT_DATE)  -- Last 7 days
  OR {id_column} NOT IN (
    -- Exclude already extracted records if needed
    SELECT {id_column} FROM existing_extract_table
  )

-- Note: Adjust the lookback period based on your refresh frequency
-- For daily refreshes: -1 day
-- For weekly refreshes: -7 days
"""

    @staticmethod
    def generate_live_connection_sql(
        table_name: str,
        dimensions: List[str],
        measures: List[str]
    ) -> str:
        """Generate optimized SQL for Tableau live connection"""
        dim_str = ",\n    ".join(dimensions)
        measure_str = ",\n    ".join([f"SUM({m}) AS total_{m}" for m in measures])

        return f"""-- Tableau Live Connection SQL
-- Optimized for real-time dashboard queries

SELECT
    -- Dimensions
    {dim_str},

    -- Measures (pre-aggregated for performance)
    {measure_str}

FROM {table_name}

-- Use parameters for dynamic filtering
WHERE date_column BETWEEN :start_date AND :end_date

GROUP BY {', '.join(dimensions)}

-- Note:
-- - Keep result set small for live connections
-- - Let Tableau handle additional aggregations when possible
-- - Use database parameters for Tableau parameters
"""


def generate_sql_optimization_report(report: SQLOptimizationReport) -> str:
    """
    Generate human-readable SQL optimization report

    Args:
        report: SQLOptimizationReport to format

    Returns:
        Formatted string report
    """
    lines = [
        "### SQL Optimization Report",
        "",
        f"**Estimated Improvement:** {report.estimated_improvement}",
        ""
    ]

    if report.suggestions:
        lines.append("**Optimization Suggestions:**")
        for i, suggestion in enumerate(report.suggestions, 1):
            lines.append(f"  {i}. {suggestion}")
        lines.append("")

    if report.performance_tips:
        lines.append("**Performance Tips:**")
        for tip in report.performance_tips:
            lines.append(f"  {tip}")
        lines.append("")

    if report.tableau_specific_tips:
        lines.append("**Tableau-Specific Recommendations:**")
        for tip in report.tableau_specific_tips:
            lines.append(f"  {tip}")
        lines.append("")

    if report.optimized_query != report.original_query:
        lines.append("**Optimized Query:**")
        lines.append("```sql")
        lines.append(report.optimized_query)
        lines.append("```")

    return "\n".join(lines)


# Convenience functions
def optimize_sql_for_tableau(query: str) -> Tuple[SQLOptimizationReport, str]:
    """
    One-line function to optimize SQL query for Tableau

    Args:
        query: SQL query to optimize

    Returns:
        Tuple of (SQLOptimizationReport, formatted report)
    """
    optimizer = SQLOptimizer()
    report = optimizer.optimize_query(query)
    formatted_report = generate_sql_optimization_report(report)

    return report, formatted_report


def generate_tableau_sql(
    table_name: str,
    database_type: str = 'generic',
    **kwargs
) -> str:
    """
    Generate Tableau-optimized SQL query

    Args:
        table_name: Table name
        database_type: Database type
        **kwargs: Additional parameters (columns, filters, etc.)

    Returns:
        SQL query string
    """
    generator = TableauSQLGenerator(database_type=database_type)
    return generator.generate_select_query(table_name, **kwargs)
