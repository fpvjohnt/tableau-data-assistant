"""
Tableau Expert Knowledge Base
Deep domain knowledge of Tableau features, best practices, and troubleshooting
"""
from typing import Dict, List

# Comprehensive Tableau knowledge base
TABLEAU_EXPERT_PROMPT = """
You are a Tableau Expert Analyst with deep knowledge of:

## TABLEAU DESKTOP FEATURES
- Worksheet design and chart types
- Dashboard layout and containers
- Stories and navigation
- Parameters and filters
- Actions (filter, highlight, URL, parameter, set)
- Tooltips and formatting
- Map layers and spatial analysis

## CALCULATIONS & FORMULAS
- Calculated fields (basic, table, LOD)
- Level of Detail (LOD) expressions: FIXED, INCLUDE, EXCLUDE
- Table calculations and addressing/partitioning
- Quick table calculations
- Statistical functions
- Date calculations and date parts
- String manipulation and regex
- Logical functions (IF, CASE, IIF)
- Aggregate vs row-level calculations

## DATA CONNECTIONS
- Live connections vs Extracts
- Data source filters
- Join types and relationships
- Data blending
- Union and custom SQL
- Data interpreter
- Data source optimization

## PERFORMANCE OPTIMIZATION
- Extract optimization and strategies
- Reducing mark count
- Query optimization
- Dashboard performance recording
- Filter efficiency
- Context filters
- Index creation

## VISUAL BEST PRACTICES
- Chart type selection
- Color psychology and accessibility
- Pre-attentive attributes
- Visual hierarchy
- Dashboard layout patterns (golden ratio)
- Mobile design
- Tooltips and interactivity

## COMMON ERRORS & FIXES
- "Cannot mix aggregate and non-aggregate" → Use ATTR() or proper aggregation
- Null values in calculations → Use ZN() or IFNULL()
- Slow performance → Check mark count, use extracts, optimize calculations
- Incorrect totals → Check table calculation addressing
- Filter not working → Check filter order and context
- Map not recognizing locations → Check data role and geocoding
- Calculation error → Check data types and division by zero

## TABLEAU-SPECIFIC TERMINOLOGY
- Dimensions vs Measures
- Blue (discrete) vs Green (continuous)
- Pills and shelves
- Marks card
- Show Me panel
- Data pane
- Analytics pane

When analyzing Tableau screens:
1. Identify exact Tableau UI elements visible
2. Recognize calculation syntax and diagnose errors
3. Suggest Tableau-specific solutions (not generic advice)
4. Reference specific Tableau features by name
5. Consider Tableau best practices and design patterns
6. Explain WHY something is a problem in Tableau context
7. Provide step-by-step Tableau instructions

Use Tableau terminology correctly and be specific with feature names!
"""

# Specific analysis prompts for different scenarios
TABLEAU_ANALYSIS_PROMPTS = {
    "calculation_error": """
    CALCULATION ERROR ANALYSIS:

    1. Identify the exact error message visible
    2. Locate which calculation/field is causing it
    3. Explain WHY this error occurs in Tableau
    4. Provide the EXACT fix (formula correction)
    5. Explain aggregation rules if relevant
    6. Suggest alternative approaches if applicable

    Common fixes:
    - Wrap in ATTR() for dimension in aggregate context
    - Use FIXED LOD to set aggregation level
    - ZN() for null handling
    - Proper parentheses in complex calculations
    """,

    "performance_issue": """
    TABLEAU PERFORMANCE ANALYSIS:

    Check for:
    1. **Mark count**: Is it >10k marks? (look at bottom status bar)
    2. **Calculation complexity**: Nested LODs? Multiple table calcs?
    3. **Filter efficiency**: Are filters on dimensions or measures?
    4. **Data source**: Live connection on large dataset?
    5. **Dashboard elements**: Too many sheets in one dashboard?

    Suggest:
    - Extract if live connection is slow
    - Aggregate data at source if possible
    - Use context filters for dimensional filtering
    - Reduce mark count via filters or aggregation
    - Simplify LOD calculations
    - Consider data engine optimization
    """,

    "design_review": """
    TABLEAU DASHBOARD DESIGN REVIEW:

    Evaluate:
    1. **Layout**: Golden ratio? Clear hierarchy? Container structure?
    2. **Chart types**: Appropriate for data type and question?
    3. **Color**: Consistent palette? Accessibility? Legend placement?
    4. **Filters**: Well-organized? Apply to relevant sheets?
    5. **Interactivity**: Actions configured? Tooltips informative?
    6. **Typography**: Consistent fonts? Readable sizes (min 10pt)?
    7. **White space**: Good balance? Not cluttered?
    8. **Title/Labels**: Descriptive? Proper capitalization?

    Reference Tableau UI elements:
    - Container types (horizontal/vertical/floating)
    - Dashboard objects (text, image, web page, navigation)
    - Device layouts (Desktop/Tablet/Phone)
    """,

    "lod_calculation": """
    LEVEL OF DETAIL (LOD) ANALYSIS:

    When you see FIXED/INCLUDE/EXCLUDE:

    1. Identify the LOD type and structure
    2. Check if syntax is correct
    3. Verify aggregation is appropriate
    4. Explain what the LOD is computing
    5. Suggest optimizations if nested

    Common patterns:
    - FIXED: Independent of view filters
    - INCLUDE: Adds dimension to view level
    - EXCLUDE: Removes dimension from view level

    Troubleshoot:
    - "Cannot mix..." → Wrap LOD in AGG()
    - Null results → Check dimension existence
    - Wrong totals → Verify LOD scope
    """,

    "data_connection": """
    DATA CONNECTION ANALYSIS:

    Look for:
    1. Connection type: Live vs Extract (check data source icon)
    2. Join/Relationship issues: Check data pane for red exclamation marks
    3. Field types: Correct dimension/measure designation?
    4. Nulls: Unexpected null values in preview?
    5. Data interpreter issues: Dirty data?

    Diagnose:
    - Extract refresh times (bottom status bar)
    - Join type mismatches causing duplication
    - Relationship cardinality issues
    - Data type mismatches
    """,

    "map_visualization": """
    MAP VISUALIZATION ANALYSIS:

    Check:
    1. **Geographic role**: Are lat/long or location fields properly assigned?
    2. **Background map**: Which map layer is selected? (Streets, Light, Dark, etc.)
    3. **Mark type**: Symbol, Map, or Filled?
    4. **Size/Color**: Are they meaningful and scaled properly?
    5. **Unrecognized locations**: Any (unknown) values?

    Common fixes:
    - Assign geographic role: Right-click → Geographic Role
    - Edit locations for ambiguous names
    - Import custom geocoding
    - Check coordinate system projection
    - Adjust mark size for visibility
    """
}

# Error pattern recognition
ERROR_PATTERNS = {
    "cannot mix aggregate": {
        "cause": "Mixing aggregated and non-aggregated fields in same calculation",
        "solutions": [
            "Wrap dimension in ATTR() to make it aggregate",
            "Use FIXED LOD to set aggregation level",
            "Move calculation to row/column level instead of aggregate"
        ],
        "example": "SUM([Sales]) / [Quantity] → SUM([Sales]) / ATTR([Quantity])"
    },

    "null": {
        "cause": "Calculation encountering null values",
        "solutions": [
            "Use ZN() to convert nulls to zero",
            "Use IFNULL() to provide default value",
            "Filter out nulls before calculation",
            "Check source data for completeness"
        ],
        "example": "ZN(SUM([Sales])) or IFNULL([Field], 0)"
    },

    "division by zero": {
        "cause": "Denominator evaluating to zero",
        "solutions": [
            "Add IF statement to check for zero",
            "Use ZN() on denominator",
            "Filter out zero values"
        ],
        "example": "IF [Denominator] != 0 THEN [Num]/[Denom] ELSE 0 END"
    },

    "data types": {
        "cause": "Incompatible data types in calculation",
        "solutions": [
            "Use STR() to convert to string",
            "Use INT() or FLOAT() to convert to number",
            "Use DATE() or DATETIME() for dates",
            "Check field data types in data pane"
        ],
        "example": "STR([Number Field]) or INT([String Field])"
    },

    "table calculation": {
        "cause": "Incorrect addressing or partitioning",
        "solutions": [
            "Edit table calculation → Compute Using",
            "Check specific dimensions for addressing",
            "Verify nested table calculations",
            "Restart calculation order if nested"
        ],
        "example": "Right-click pill → Edit Table Calculation"
    }
}

# Best practices by category
BEST_PRACTICES = {
    "dashboard_layout": [
        "Use golden ratio: main content 62%, supporting 38%",
        "Maintain consistent padding (8-16px)",
        "Align elements to grid",
        "Use containers for responsive design",
        "Keep dashboard width ≤1280px for standard monitors",
        "Limit to 8-12 visualizations per dashboard",
        "Put most important viz in top-left (F-pattern reading)"
    ],

    "color_usage": [
        "Limit to 3-5 colors in palette",
        "Use color for meaning, not decoration",
        "Check color-blind accessibility (avoid red-green)",
        "Use sequential colors for continuous data",
        "Use diverging colors for +/- data",
        "Reserve bright colors for highlights",
        "Maintain consistent color meanings across dashboard"
    ],

    "chart_selection": [
        "Bar chart: comparing categories",
        "Line chart: trends over time",
        "Scatter plot: correlation between two measures",
        "Heatmap: magnitude across two dimensions",
        "Treemap: hierarchical part-to-whole",
        "Avoid pie charts for >5 categories",
        "Text table: precise values needed",
        "Bullet chart: actual vs target"
    ],

    "performance": [
        "Use extracts for >1M rows",
        "Filter data at source when possible",
        "Limit to <10k marks per viz",
        "Minimize LOD calculations",
        "Use context filters for large dimensions",
        "Aggregate before joining",
        "Hide unused fields in data source"
    ],

    "calculations": [
        "Name calculations descriptively",
        "Comment complex calculations",
        "Use parameters for dynamic values",
        "Avoid nested LODs when possible",
        "Test calculations with sample data first",
        "Use ATTR() to suppress aggregation warnings",
        "Prefer table calcs for running totals/ranks"
    ]
}


def get_tableau_expert_context(analysis_type: str = "general") -> str:
    """
    Get Tableau expert context for analysis

    Args:
        analysis_type: Type of analysis to perform

    Returns:
        Formatted expert prompt
    """
    base_prompt = TABLEAU_EXPERT_PROMPT

    if analysis_type in TABLEAU_ANALYSIS_PROMPTS:
        specific_prompt = TABLEAU_ANALYSIS_PROMPTS[analysis_type]
        return f"{base_prompt}\n\n## SPECIFIC FOCUS:\n{specific_prompt}"

    return base_prompt


def get_error_solution(error_text: str) -> Dict:
    """
    Get solution for common Tableau error

    Args:
        error_text: Error message text

    Returns:
        Dictionary with cause, solutions, and examples
    """
    error_text_lower = error_text.lower()

    for error_key, error_info in ERROR_PATTERNS.items():
        if error_key in error_text_lower:
            return error_info

    return {
        "cause": "Unknown error",
        "solutions": ["Check Tableau documentation", "Review calculation syntax"],
        "example": ""
    }


def get_best_practices(category: str) -> List[str]:
    """
    Get best practices for specific category

    Args:
        category: Category name

    Returns:
        List of best practice strings
    """
    return BEST_PRACTICES.get(category, [])
