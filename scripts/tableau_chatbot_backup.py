import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import zipfile
import tempfile
import pandas as pd
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Tableau Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-style black and white interface
st.markdown("""
<style>
    /* Main app styling - black background */
    .stApp {
        background-color: #212121;
    }

    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #212121;
        max-width: 1400px;
        margin: 0 auto;
    }

    /* Sidebar styling - dark gray */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2f2f2f;
    }

    [data-testid="stSidebar"] * {
        color: #ECECEC !important;
    }

    /* Title styling */
    h1 {
        color: #ECECEC;
        font-size: 2rem !important;
        font-weight: 600 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }

    /* Subtitle */
    .main .block-container > div:nth-child(1) > div:nth-child(2) {
        text-align: center;
        color: #B4B4B4;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Subheaders */
    h2, h3 {
        color: #ECECEC !important;
        font-weight: 600 !important;
    }

    /* Paragraph text */
    p {
        color: #ECECEC;
    }

    /* Cards and expanders */
    .streamlit-expanderHeader {
        background-color: #2f2f2f;
        border-radius: 8px !important;
        border: 1px solid #3f3f3f;
        font-weight: 500;
        color: #ECECEC !important;
    }

    /* Buttons - minimal style */
    .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: background-color 0.2s;
    }

    .stButton > button:hover {
        background-color: #0d8f6d;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #2f2f2f;
        color: white;
        border: 1px solid #3f3f3f;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }

    .stDownloadButton > button:hover {
        background-color: #3f3f3f;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        background-color: #2f2f2f;
    }

    [data-testid="stChatMessageContainer"] > div {
        background-color: #2f2f2f;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid #3f3f3f;
        padding: 0.75rem;
        transition: border-color 0.2s;
        background-color: #2f2f2f;
        color: #ECECEC;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #10a37f;
        outline: none;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #2f2f2f;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #3f3f3f;
    }

    [data-testid="stFileUploader"] * {
        color: #ECECEC !important;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 6px;
        border: 1px solid #3f3f3f;
        background-color: #2f2f2f;
    }

    /* Success message */
    .stSuccess {
        background-color: #1a3a2e;
        color: #7ee3c3;
        border-left: 3px solid #10a37f;
    }

    /* Warning message */
    .stWarning {
        background-color: #3a311a;
        color: #f5d77e;
        border-left: 3px solid #f59e0b;
    }

    /* Error message */
    .stError {
        background-color: #3a1a1a;
        color: #f87171;
        border-left: 3px solid #ef4444;
    }

    /* Info message */
    .stInfo {
        background-color: #1a2a3a;
        color: #7ec3e3;
        border-left: 3px solid #3b82f6;
    }

    /* Dataframe styling */
    .dataframe {
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #3f3f3f;
        background-color: #2f2f2f;
    }

    .dataframe th {
        background-color: #1a1a1a !important;
        color: #ECECEC !important;
    }

    .dataframe td {
        background-color: #2f2f2f !important;
        color: #ECECEC !important;
    }

    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background-color: #3f3f3f;
    }

    /* JSON viewer */
    .streamlit-expanderContent pre {
        background-color: #1a1a1a;
        border-radius: 6px;
        padding: 1rem;
        border: 1px solid #3f3f3f;
        color: #ECECEC;
    }

    .streamlit-expanderContent code {
        color: #ECECEC;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #10a37f !important;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        border: 1px solid #565869;
        color: #ECECEC;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2a2b32;
    }

    /* Chat input */
    .stChatInputContainer {
        border-top: 1px solid #3f3f3f;
        padding-top: 1rem;
        background-color: #212121;
    }

    /* Chat input field */
    [data-testid="stChatInput"] > div > div > input {
        background-color: #2f2f2f;
        border: 1px solid #3f3f3f;
        color: #ECECEC;
    }

    [data-testid="stChatInput"] > div > div > input:focus {
        border-color: #10a37f;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #2f2f2f;
        border: 1px solid #3f3f3f;
        color: #ECECEC;
    }

    /* Labels */
    label {
        color: #ECECEC !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = []
if "cleaned_dataframes" not in st.session_state:
    st.session_state.cleaned_dataframes = {}
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []
if "sql_queries" not in st.session_state:
    st.session_state.sql_queries = []

def get_anthropic_client():
    """Initialize Anthropic client with API key"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found. Please add it to your .env file.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

def parse_twb_file(file_content):
    """Parse Tableau .twb (XML) file and extract key information"""
    try:
        root = ET.fromstring(file_content)

        info = {
            "worksheets": [],
            "dashboards": [],
            "data_sources": [],
            "calculations": []
        }

        # Extract worksheets
        for worksheet in root.findall(".//worksheet"):
            name = worksheet.get("name", "Unnamed")
            info["worksheets"].append(name)

        # Extract dashboards
        for dashboard in root.findall(".//dashboard"):
            name = dashboard.get("name", "Unnamed")
            info["dashboards"].append(name)

        # Extract data sources
        for datasource in root.findall(".//datasource"):
            name = datasource.get("name", "Unnamed")
            if name not in ["Parameters", "Sample - Superstore"]:
                info["data_sources"].append(name)

        # Extract calculated fields
        for column in root.findall(".//column[@caption][@formula]"):
            calc_name = column.get("caption", "Unnamed")
            calc_formula = column.get("formula", "")
            info["calculations"].append({
                "name": calc_name,
                "formula": calc_formula
            })

        return info, ET.tostring(root, encoding='unicode')
    except Exception as e:
        return None, str(e)

def parse_twbx_file(uploaded_file):
    """Parse Tableau .twbx (ZIP) file and extract .twb content"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.twbx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            # Find .twb file in the archive
            twb_files = [f for f in zip_ref.namelist() if f.endswith('.twb')]
            if twb_files:
                twb_content = zip_ref.read(twb_files[0]).decode('utf-8')
                return parse_twb_file(twb_content)

        return None, "No .twb file found in .twbx archive"
    except Exception as e:
        return None, str(e)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def analyze_csv_excel(uploaded_file):
    """Analyze CSV or Excel file and provide summary"""
    try:
        # For large files, read in chunks for better memory management
        file_size_mb = uploaded_file.size / (1024 * 1024)

        if uploaded_file.name.endswith('.csv'):
            # For very large CSV files, use chunked reading
            if file_size_mb > 200:
                # Read first 100k rows for analysis
                df = pd.read_csv(uploaded_file, nrows=100000)
                st.warning(f"⚠️ Large file detected ({file_size_mb:.1f} MB). Analyzing first 100,000 rows.")
            else:
                df = pd.read_csv(uploaded_file)
        else:
            # For Excel files
            if file_size_mb > 200:
                df = pd.read_excel(uploaded_file, nrows=100000)
                st.warning(f"⚠️ Large file detected ({file_size_mb:.1f} MB). Analyzing first 100,000 rows.")
            else:
                df = pd.read_excel(uploaded_file)

        info = {
            "file_size_mb": round(file_size_mb, 2),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
            "sample_data": df.head(5).to_dict(),
            "missing_values": {str(k): int(v) for k, v in df.isnull().sum().to_dict().items()},
            "numeric_summary": {str(k): {str(k2): float(v2) for k2, v2 in v.items()}
                               for k, v in df.describe().to_dict().items()}
                               if len(df.select_dtypes(include=['number']).columns) > 0 else None
        }

        return info, df
    except Exception as e:
        return None, str(e)

def clean_data_for_tableau(df, filename):
    """Clean and prepare data for Tableau with best practices"""
    df_clean = df.copy()
    cleaning_report = []

    # 1. Handle column names - make them Tableau-friendly
    original_cols = df_clean.columns.tolist()
    df_clean.columns = df_clean.columns.str.strip()
    df_clean.columns = df_clean.columns.str.replace(r'[^\w\s]', '_', regex=True)
    df_clean.columns = df_clean.columns.str.replace(r'\s+', '_', regex=True)
    if list(df_clean.columns) != original_cols:
        cleaning_report.append("✅ Cleaned column names (removed special characters, replaced spaces)")

    # 2. Remove completely empty rows and columns
    initial_rows = len(df_clean)
    df_clean = df_clean.dropna(how='all')
    if len(df_clean) < initial_rows:
        cleaning_report.append(f"✅ Removed {initial_rows - len(df_clean)} completely empty rows")

    initial_cols = len(df_clean.columns)
    df_clean = df_clean.dropna(axis=1, how='all')
    if len(df_clean.columns) < initial_cols:
        cleaning_report.append(f"✅ Removed {initial_cols - len(df_clean.columns)} completely empty columns")

    # 3. Handle duplicate rows
    duplicates = df_clean.duplicated().sum()
    if duplicates > 0:
        df_clean = df_clean.drop_duplicates()
        cleaning_report.append(f"✅ Removed {duplicates} duplicate rows")

    # 4. Convert data types appropriately for Tableau
    for col in df_clean.columns:
        # Try to convert to datetime if it looks like a date
        if df_clean[col].dtype == 'object':
            try:
                # Check if at least 70% of non-null values can be parsed as dates
                sample = df_clean[col].dropna().head(100)
                if len(sample) > 0:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    if parsed.notna().sum() / len(sample) > 0.7:
                        df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                        cleaning_report.append(f"✅ Converted '{col}' to datetime")
            except:
                pass

        # Try to convert to numeric if it looks like a number
        if df_clean[col].dtype == 'object':
            try:
                # Remove common currency symbols and commas
                temp = df_clean[col].astype(str).str.replace(r'[$,€£¥]', '', regex=True).str.strip()
                numeric_vals = pd.to_numeric(temp, errors='coerce')
                if numeric_vals.notna().sum() / len(df_clean) > 0.7:
                    df_clean[col] = numeric_vals
                    cleaning_report.append(f"✅ Converted '{col}' to numeric")
            except:
                pass

    # 5. Handle missing values - add indicator columns for significant missingness
    for col in df_clean.columns:
        missing_pct = df_clean[col].isnull().sum() / len(df_clean) * 100
        if missing_pct > 10 and missing_pct < 100:
            indicator_col = f"{col}_is_missing"
            df_clean[indicator_col] = df_clean[col].isnull().astype(int)
            cleaning_report.append(f"✅ Added missing indicator for '{col}' ({missing_pct:.1f}% missing)")

    # 6. Trim whitespace from string columns
    string_cols = df_clean.select_dtypes(include=['object']).columns
    for col in string_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    if len(string_cols) > 0:
        cleaning_report.append(f"✅ Trimmed whitespace from {len(string_cols)} text columns")

    # 7. Cap very large datasets for Tableau performance
    if len(df_clean) > 1000000:
        df_clean = df_clean.head(1000000)
        cleaning_report.append("⚠️ Dataset capped at 1,000,000 rows for Tableau performance")

    # Generate summary
    summary = {
        "original_rows": initial_rows,
        "cleaned_rows": len(df_clean),
        "original_columns": initial_cols,
        "cleaned_columns": len(df_clean.columns),
        "cleaning_actions": len(cleaning_report),
        "report": cleaning_report
    }

    return df_clean, summary

def detect_anomalies(df):
    """Detect anomalies and unusual patterns in the data"""
    anomalies = []

    # Analyze numeric columns for outliers
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].notna().sum() > 0:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            # Detect outliers using IQR method
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)][col]
            if len(outliers) > 0:
                outlier_pct = (len(outliers) / len(df)) * 100
                if outlier_pct > 1:  # Only report if >1% are outliers
                    anomalies.append({
                        "type": "outliers",
                        "column": col,
                        "count": len(outliers),
                        "percentage": round(outlier_pct, 2),
                        "severity": "high" if outlier_pct > 5 else "medium",
                        "description": f"Found {len(outliers)} outliers ({outlier_pct:.1f}%) in '{col}'"
                    })

            # Check for negative values in potentially positive-only columns
            if any(keyword in col.lower() for keyword in ['price', 'cost', 'amount', 'quantity', 'age', 'count']):
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    anomalies.append({
                        "type": "negative_values",
                        "column": col,
                        "count": negative_count,
                        "severity": "high",
                        "description": f"Found {negative_count} negative values in '{col}' (expected positive)"
                    })

    # Check for duplicate records
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        dup_pct = (duplicates / len(df)) * 100
        if dup_pct > 5:
            anomalies.append({
                "type": "duplicates",
                "count": duplicates,
                "percentage": round(dup_pct, 2),
                "severity": "medium",
                "description": f"Found {duplicates} duplicate rows ({dup_pct:.1f}% of data)"
            })

    # Check for suspicious missing patterns
    for col in df.columns:
        missing_pct = (df[col].isnull().sum() / len(df)) * 100
        if missing_pct > 50:
            anomalies.append({
                "type": "high_missing",
                "column": col,
                "percentage": round(missing_pct, 2),
                "severity": "high" if missing_pct > 80 else "medium",
                "description": f"Column '{col}' has {missing_pct:.1f}% missing values"
            })

    # Check for date columns with future dates or very old dates
    date_cols = df.select_dtypes(include=['datetime64']).columns
    for col in date_cols:
        if df[col].notna().sum() > 0:
            max_date = df[col].max()
            min_date = df[col].min()
            current_year = pd.Timestamp.now().year

            if max_date.year > current_year + 1:
                anomalies.append({
                    "type": "future_dates",
                    "column": col,
                    "severity": "medium",
                    "description": f"Column '{col}' contains future dates (max: {max_date.date()})"
                })

            if min_date.year < 1900:
                anomalies.append({
                    "type": "old_dates",
                    "column": col,
                    "severity": "low",
                    "description": f"Column '{col}' contains very old dates (min: {min_date.date()})"
                })

    # Check for constant columns
    for col in df.columns:
        if df[col].nunique() == 1:
            anomalies.append({
                "type": "constant_column",
                "column": col,
                "severity": "low",
                "description": f"Column '{col}' has only one unique value (constant)"
            })

    return anomalies

def suggest_visualizations(df):
    """Suggest Tableau visualization templates based on data structure"""
    suggestions = []

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    # Time series analysis
    if len(date_cols) > 0 and len(numeric_cols) > 0:
        suggestions.append({
            "viz_type": "Line Chart / Area Chart",
            "priority": "high",
            "use_case": "Time Series Trend Analysis",
            "recommended_fields": {
                "x_axis": date_cols[0],
                "y_axis": numeric_cols[0],
                "color": categorical_cols[0] if categorical_cols else None
            },
            "description": f"Track trends over time using {date_cols[0]} and {numeric_cols[0]}",
            "tableau_tips": "Use continuous date on Columns, measure on Rows. Add trend lines for forecasting."
        })

    # Category comparison
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        # Check cardinality
        cardinality = df[categorical_cols[0]].nunique()

        if cardinality <= 10:
            suggestions.append({
                "viz_type": "Bar Chart (Horizontal)",
                "priority": "high",
                "use_case": "Category Comparison",
                "recommended_fields": {
                    "rows": categorical_cols[0],
                    "columns": numeric_cols[0]
                },
                "description": f"Compare {numeric_cols[0]} across {categorical_cols[0]} categories",
                "tableau_tips": "Sort bars by value for better readability. Use color to highlight key categories."
            })
        elif cardinality <= 50:
            suggestions.append({
                "viz_type": "Tree Map",
                "priority": "medium",
                "use_case": "Hierarchical Part-to-Whole",
                "recommended_fields": {
                    "size": numeric_cols[0],
                    "color": categorical_cols[0]
                },
                "description": f"Show proportions of {categorical_cols[0]} by {numeric_cols[0]}",
                "tableau_tips": "Great for showing hierarchy and relative sizes. Works well with 10-50 categories."
            })

    # Geographical analysis
    geo_keywords = ['country', 'state', 'city', 'region', 'zip', 'postal', 'latitude', 'longitude', 'lat', 'lon', 'lng']
    geo_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in geo_keywords)]

    if geo_cols and len(numeric_cols) > 0:
        suggestions.append({
            "viz_type": "Map (Symbol Map or Filled Map)",
            "priority": "high",
            "use_case": "Geographical Distribution",
            "recommended_fields": {
                "location": geo_cols[0],
                "size": numeric_cols[0],
                "color": numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
            },
            "description": f"Visualize {numeric_cols[0]} across geographical regions",
            "tableau_tips": "Use filled maps for regions/states, symbol maps for precise locations. Enable map layers."
        })

    # Distribution analysis
    if len(numeric_cols) >= 1:
        suggestions.append({
            "viz_type": "Histogram",
            "priority": "medium",
            "use_case": "Distribution Analysis",
            "recommended_fields": {
                "bins": numeric_cols[0],
                "count": "Number of Records"
            },
            "description": f"Analyze the distribution of {numeric_cols[0]}",
            "tableau_tips": "Convert measure to dimension and create bins. Shows frequency distribution."
        })

    # Correlation / Scatter
    if len(numeric_cols) >= 2:
        suggestions.append({
            "viz_type": "Scatter Plot",
            "priority": "high",
            "use_case": "Correlation Analysis",
            "recommended_fields": {
                "x_axis": numeric_cols[0],
                "y_axis": numeric_cols[1],
                "color": categorical_cols[0] if categorical_cols else None,
                "size": numeric_cols[2] if len(numeric_cols) > 2 else None
            },
            "description": f"Explore relationship between {numeric_cols[0]} and {numeric_cols[1]}",
            "tableau_tips": "Add trend lines to see correlation. Use color and size for multi-dimensional analysis."
        })

    # Heatmap for multi-categorical
    if len(categorical_cols) >= 2 and len(numeric_cols) >= 1:
        cat1_cardinality = df[categorical_cols[0]].nunique()
        cat2_cardinality = df[categorical_cols[1]].nunique()

        if cat1_cardinality <= 20 and cat2_cardinality <= 20:
            suggestions.append({
                "viz_type": "Heat Map",
                "priority": "high",
                "use_case": "Multi-Dimensional Comparison",
                "recommended_fields": {
                    "rows": categorical_cols[0],
                    "columns": categorical_cols[1],
                    "color": numeric_cols[0]
                },
                "description": f"Compare {numeric_cols[0]} across {categorical_cols[0]} and {categorical_cols[1]}",
                "tableau_tips": "Use color intensity to show magnitude. Perfect for pattern recognition."
            })

    # KPI / Single value
    if len(numeric_cols) > 0:
        suggestions.append({
            "viz_type": "KPI / Big Number",
            "priority": "low",
            "use_case": "Dashboard Header / Key Metric",
            "recommended_fields": {
                "metric": numeric_cols[0]
            },
            "description": f"Display {numeric_cols[0]} as a key performance indicator",
            "tableau_tips": "Use SUM/AVG aggregation. Add sparklines or comparison to previous period."
        })

    # Pie chart (only if low cardinality)
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        cardinality = df[categorical_cols[0]].nunique()
        if cardinality <= 5:
            suggestions.append({
                "viz_type": "Pie Chart",
                "priority": "low",
                "use_case": "Simple Part-to-Whole (Use Sparingly)",
                "recommended_fields": {
                    "angle": numeric_cols[0],
                    "color": categorical_cols[0]
                },
                "description": f"Show composition of {categorical_cols[0]}",
                "tableau_tips": "⚠️ Use only for 2-5 categories. Bar charts are usually better. Add % labels."
            })

    return suggestions

def create_analysis_prompt(file_type, file_info, user_question=None):
    """Create a prompt for Claude based on file type and content"""
    if file_type in ["twb", "twbx"]:
        prompt = f"""I have a Tableau workbook with the following structure:

**Worksheets:** {', '.join(file_info['worksheets']) if file_info['worksheets'] else 'None'}
**Dashboards:** {', '.join(file_info['dashboards']) if file_info['dashboards'] else 'None'}
**Data Sources:** {', '.join(file_info['data_sources']) if file_info['data_sources'] else 'None'}

**Calculated Fields:**
"""
        for calc in file_info.get('calculations', [])[:10]:  # Limit to first 10
            prompt += f"\n- {calc['name']}: {calc['formula']}"

        if user_question:
            prompt += f"\n\n**Question:** {user_question}"
        else:
            prompt += "\n\nPlease provide an analysis of this Tableau workbook, including insights about its structure, potential improvements, and best practices."

    elif file_type in ["csv", "xlsx"]:
        prompt = f"""I have a dataset with the following characteristics:

**File Size:** {file_info.get('file_size_mb', 'Unknown')} MB
**Rows:** {file_info['rows']:,}
**Columns:** {file_info['columns']}
**Column Names:** {', '.join(file_info['column_names'])}

**Data Types:**
"""
        for col, dtype in file_info['dtypes'].items():
            prompt += f"\n- {col}: {dtype}"

        prompt += "\n\n**Missing Values:**\n"
        for col, missing in file_info['missing_values'].items():
            if missing > 0:
                prompt += f"- {col}: {missing}\n"

        if user_question:
            prompt += f"\n\n**Question:** {user_question}"
        else:
            prompt += "\n\nPlease provide an analysis of this dataset suitable for Tableau visualization, including insights about data quality, suggested visualizations, and any data preparation recommendations."

    return prompt

def encode_image_to_base64(image_file):
    """Convert uploaded image to base64"""
    try:
        image = Image.open(image_file)
        buffered = BytesIO()
        image.save(buffered, format=image.format or "PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str, image.format or "PNG"
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None

def analyze_image_with_claude(image_base64, image_format, analysis_type="dashboard"):
    """Analyze screenshots of Tableau dashboards/worksheets using Claude's vision"""
    client = get_anthropic_client()

    prompts = {
        "dashboard": """Analyze this Tableau dashboard screenshot and provide:
1. **Visual Design Issues**: Color schemes, layout problems, text readability
2. **Data Visualization Best Practices**: Chart choices, appropriate use of visual elements
3. **User Experience**: Navigation, interactivity, dashboard organization
4. **Performance Concerns**: Potential rendering issues, overly complex visuals
5. **Accessibility**: Color blindness considerations, contrast ratios
6. **Recommendations**: Specific improvements with rationale""",

        "worksheet": """Analyze this Tableau worksheet and identify:
1. **Chart Effectiveness**: Is the right chart type used for the data?
2. **Data Clarity**: Are labels, legends, and axes clear?
3. **Visual Hierarchy**: Does the eye flow naturally to key insights?
4. **Common Pitfalls**: Truncated axes, misleading scales, pie chart overuse
5. **Improvements**: Specific suggestions to enhance this visualization""",

        "error": """Analyze this Tableau error screenshot and provide:
1. **Error Identification**: What is the specific error shown?
2. **Root Cause**: Why is this error occurring?
3. **Solution Steps**: Step-by-step fix with explanations
4. **Prevention**: How to avoid this error in the future
5. **Related Issues**: Other problems that might stem from this"""
    }

    prompt = prompts.get(analysis_type, prompts["dashboard"])

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": f"image/{image_format.lower()}",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def analyze_sql_query(query):
    """Analyze and optimize SQL queries for Tableau data sources"""
    client = get_anthropic_client()

    prompt = f"""Analyze this SQL query for use with Tableau and provide:

SQL Query:
```sql
{query}
```

Please provide:
1. **Query Analysis**: What this query does and its purpose
2. **Performance Issues**: Identify slow operations, missing indexes, inefficient joins
3. **Tableau-Specific Optimization**:
   - Extract vs Live connection recommendations
   - Aggregation strategies
   - Data source filters
4. **Optimized Version**: Rewrite the query for better performance
5. **ETL Recommendations**: Should this be pre-aggregated or transformed?
6. **Best Practices**: Tableau-specific SQL best practices violated or followed
7. **Index Suggestions**: What indexes would help this query"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error analyzing SQL: {str(e)}"

def chat_with_claude(messages, include_images=False):
    """Send messages to Claude and get response with optional image support"""
    client = get_anthropic_client()

    try:
        # If we have images in session state and include_images is True, add them to the first message
        if include_images and st.session_state.uploaded_images:
            # Restructure messages to include images
            enhanced_messages = []
            for i, msg in enumerate(messages):
                if i == 0 and msg["role"] == "user":
                    # Add images to first user message
                    content = []
                    for img_data in st.session_state.uploaded_images:
                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": img_data["media_type"],
                                "data": img_data["base64"]
                            }
                        })
                    content.append({
                        "type": "text",
                        "text": msg["content"]
                    })
                    enhanced_messages.append({
                        "role": "user",
                        "content": content
                    })
                else:
                    enhanced_messages.append(msg)
            messages = enhanced_messages

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error communicating with Claude: {str(e)}"

# Main UI
st.markdown("""
<div style="text-align: center; padding: 1rem 0 2rem 0;">
    <h1 style="margin-bottom: 0.5rem;">Tableau Data Assistant</h1>
    <p style="font-size: 0.875rem; color: #B4B4B4; font-weight: 400;">
        Clean data • Analyze screenshots • Optimize SQL
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar for file uploads
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0; margin: 0 0 1rem 0; border-bottom: 1px solid #565869;">
        <h3 style="font-size: 0.875rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
            Data Files
        </h3>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload CSV or Excel files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        help="Upload .csv or .xlsx files for data cleaning and analysis",
        key="data_uploader"
    )

    if uploaded_files:
        # Get list of already processed files
        processed_files = [f["name"] for f in st.session_state.uploaded_files_info]
        new_files = [f for f in uploaded_files if f.name not in processed_files]

        if new_files:
            st.info(f"🔄 Auto-analyzing {len(new_files)} new file(s)...")

            for uploaded_file in new_files:
                file_extension = Path(uploaded_file.name).suffix.lower()

                with st.spinner(f"Processing {uploaded_file.name}..."):
                    if file_extension in [".csv", ".xlsx"]:
                        info, df = analyze_csv_excel(uploaded_file)
                        if info:
                            st.session_state.uploaded_files_info.append({
                                "name": uploaded_file.name,
                                "type": file_extension[1:],
                                "info": info
                            })

                            # Store the dataframe
                            st.session_state.cleaned_dataframes[uploaded_file.name] = {
                                "original": df,
                                "cleaned": None
                            }

                            # Auto-analyze with Claude
                            analysis_prompt = create_analysis_prompt(file_extension[1:], info)
                            analysis = chat_with_claude([{"role": "user", "content": analysis_prompt}])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"📊 **Auto-Analysis of {uploaded_file.name}:**\n\n{analysis}"
                            })

                            # Detect anomalies in original data
                            st.info(f"🔍 Detecting anomalies in {uploaded_file.name}...")
                            anomalies = detect_anomalies(df)

                            if anomalies:
                                anomaly_msg = f"⚠️ **Anomaly Detection for {uploaded_file.name}:**\n\n"
                                anomaly_msg += f"Found {len(anomalies)} potential issues in your data:\n\n"

                                # Group by severity
                                high_severity = [a for a in anomalies if a['severity'] == 'high']
                                medium_severity = [a for a in anomalies if a['severity'] == 'medium']
                                low_severity = [a for a in anomalies if a['severity'] == 'low']

                                if high_severity:
                                    anomaly_msg += "**🔴 High Priority Issues:**\n"
                                    for anomaly in high_severity:
                                        anomaly_msg += f"- {anomaly['description']}\n"
                                    anomaly_msg += "\n"

                                if medium_severity:
                                    anomaly_msg += "**🟡 Medium Priority Issues:**\n"
                                    for anomaly in medium_severity:
                                        anomaly_msg += f"- {anomaly['description']}\n"
                                    anomaly_msg += "\n"

                                if low_severity:
                                    anomaly_msg += "**🟢 Low Priority Issues:**\n"
                                    for anomaly in low_severity:
                                        anomaly_msg += f"- {anomaly['description']}\n"
                                    anomaly_msg += "\n"

                                anomaly_msg += "\n💡 **Recommendation:** Review these anomalies before proceeding with visualization. Some may need investigation or cleaning."

                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": anomaly_msg
                                })

                            # Suggest visualizations
                            st.info(f"📈 Generating visualization suggestions for {uploaded_file.name}...")
                            viz_suggestions = suggest_visualizations(df)

                            if viz_suggestions:
                                viz_msg = f"📊 **Visualization Templates for {uploaded_file.name}:**\n\n"
                                viz_msg += "Based on your data structure, here are recommended Tableau visualizations:\n\n"

                                # Group by priority
                                high_priority = [v for v in viz_suggestions if v['priority'] == 'high']
                                medium_priority = [v for v in viz_suggestions if v['priority'] == 'medium']
                                low_priority = [v for v in viz_suggestions if v['priority'] == 'low']

                                if high_priority:
                                    viz_msg += "**🌟 Highly Recommended:**\n\n"
                                    for viz in high_priority:
                                        viz_msg += f"**{viz['viz_type']}** - {viz['use_case']}\n"
                                        viz_msg += f"- {viz['description']}\n"
                                        viz_msg += f"- 💡 Tableau Tip: {viz['tableau_tips']}\n\n"

                                if medium_priority:
                                    viz_msg += "**📌 Also Consider:**\n\n"
                                    for viz in medium_priority:
                                        viz_msg += f"**{viz['viz_type']}** - {viz['use_case']}\n"
                                        viz_msg += f"- {viz['description']}\n\n"

                                if low_priority:
                                    viz_msg += "**📋 Additional Options:**\n\n"
                                    for viz in low_priority:
                                        viz_msg += f"**{viz['viz_type']}** - {viz['use_case']}\n"
                                        viz_msg += f"- {viz['description']}\n\n"

                                viz_msg += "\n🎨 **Ready to build?** Ask me about any of these visualization types for step-by-step Tableau instructions!"

                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": viz_msg
                                })

                            # Auto-clean if data quality issues detected
                            total_missing = sum(info['missing_values'].values())
                            if total_missing > 0 or info['rows'] > 100:
                                st.info(f"🧹 Auto-cleaning {uploaded_file.name}...")
                                cleaned_df, summary = clean_data_for_tableau(df, uploaded_file.name)
                                st.session_state.cleaned_dataframes[uploaded_file.name]['cleaned'] = cleaned_df
                                st.session_state.cleaned_dataframes[uploaded_file.name]['summary'] = summary

                                # Report cleaning results
                                cleaning_msg = f"✅ **Auto-Cleaned {uploaded_file.name}:**\n\n"
                                cleaning_msg += f"- Original: {summary['original_rows']:,} rows × {summary['original_columns']} columns\n"
                                cleaning_msg += f"- Cleaned: {summary['cleaned_rows']:,} rows × {summary['cleaned_columns']} columns\n"
                                cleaning_msg += f"- {summary['cleaning_actions']} cleaning actions performed\n\n"
                                cleaning_msg += "**Actions:**\n" + "\n".join([f"- {action}" for action in summary['report']])
                                cleaning_msg += f"\n\n💾 **Ready to download!** Check the sidebar for the download button."

                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": cleaning_msg
                                })

                            st.success(f"✅ Processed {uploaded_file.name}")
                        else:
                            st.error(f"❌ Error analyzing {uploaded_file.name}: {df}")

            st.rerun()
        else:
            st.success(f"✅ {len(uploaded_files)} file(s) loaded")

    # Display parsed files info
    if st.session_state.uploaded_files_info:
        st.markdown("""
        <div style="padding: 0.5rem 0; margin: 1.5rem 0 1rem 0; border-bottom: 2px solid rgba(255,255,255,0.2);">
            <h3 style="margin: 0; font-size: 1.3rem;">📋 Loaded Files</h3>
        </div>
        """, unsafe_allow_html=True)
        for file_info in st.session_state.uploaded_files_info:
            with st.expander(f"📄 {file_info['name']}"):
                st.json(file_info['info'], expanded=False)

    # Download Cleaned Files Section
    cleaned_files = {k: v for k, v in st.session_state.cleaned_dataframes.items() if v.get('cleaned') is not None}
    if cleaned_files:
        st.markdown("""
        <div style="padding: 0.5rem 0; margin: 1.5rem 0 1rem 0; border-bottom: 2px solid rgba(255,255,255,0.2);">
            <h3 style="margin: 0; font-size: 1.3rem;">💾 Download Cleaned Files</h3>
        </div>
        """, unsafe_allow_html=True)

        for filename, data in cleaned_files.items():
            with st.expander(f"📥 {filename} (Ready)", expanded=True):
                # Create download button
                csv = data['cleaned'].to_csv(index=False)
                st.download_button(
                    label=f"📥 Download cleaned_{filename}",
                    data=csv,
                    file_name=f"cleaned_{filename}",
                    mime="text/csv",
                    key=f"download_{filename}"
                )

                # Show cleaning summary
                if 'summary' in data:
                    summary = data['summary']
                    st.markdown(f"""
**Cleaning Summary:**
- Original: {summary['original_rows']:,} rows × {summary['original_columns']} columns
- Cleaned: {summary['cleaned_rows']:,} rows × {summary['cleaned_columns']} columns
- {summary['cleaning_actions']} actions performed
                    """)

                    # Show data preview
                    with st.expander("Preview cleaned data"):
                        st.dataframe(data['cleaned'].head(10))

    # Screenshot Analysis Section
    st.markdown("""
    <div style="padding: 0.5rem 0; margin: 1.5rem 0 0.5rem 0; border-bottom: 1px solid #565869;">
        <h3 style="font-size: 0.875rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
            Screenshots
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # FIRST: Select analysis type
    analysis_type = st.selectbox(
        "1️⃣ What type of screenshot?",
        ["Dashboard", "Worksheet", "Error/Issue"],
        key="analysis_type",
        help="Select the type before uploading"
    )

    # SECOND: Upload screenshots
    uploaded_screenshots = st.file_uploader(
        "2️⃣ Upload Screenshots",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help=f"Upload PNG or JPG screenshots for {analysis_type.lower()} analysis",
        key="screenshot_uploader"
    )

    if uploaded_screenshots:
        # Get list of already analyzed images
        analyzed_images = [img["name"] for img in st.session_state.uploaded_images]
        new_screenshots = [s for s in uploaded_screenshots if s.name not in analyzed_images]

        if new_screenshots:
            st.info(f"🔄 Auto-analyzing {len(new_screenshots)} {analysis_type.lower()} screenshot(s)...")

            for screenshot in new_screenshots:
                with st.spinner(f"Analyzing {screenshot.name} as {analysis_type}..."):
                    img_base64, img_format = encode_image_to_base64(screenshot)
                    if img_base64:
                        # Store image with analysis type metadata
                        st.session_state.uploaded_images.append({
                            "name": screenshot.name,
                            "base64": img_base64,
                            "media_type": f"image/{img_format.lower()}",
                            "analysis_type": analysis_type
                        })

                        # Auto-analyze
                        analysis = analyze_image_with_claude(
                            img_base64,
                            img_format,
                            analysis_type.lower().replace("/", "_")
                        )

                        # Add detailed context to chat with analysis type
                        analysis_intro = f"📸 **Screenshot Analysis: {screenshot.name}**\n\n"
                        analysis_intro += f"**Type:** {analysis_type}\n"
                        analysis_intro += f"**Status:** Analysis complete\n\n"
                        analysis_intro += "---\n\n"

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": analysis_intro + analysis
                        })

                        # Add follow-up instructions
                        follow_up = f"\n\n💡 **Next Steps:**\n"
                        if analysis_type == "Dashboard":
                            follow_up += "- Ask me to elaborate on any design recommendations\n"
                            follow_up += "- Request specific color palette suggestions\n"
                            follow_up += "- Get advice on layout improvements\n"
                            follow_up += "- Learn about performance optimization"
                        elif analysis_type == "Worksheet":
                            follow_up += "- Ask for alternative chart type suggestions\n"
                            follow_up += "- Request help with calculated fields\n"
                            follow_up += "- Get guidance on data visualization best practices\n"
                            follow_up += "- Learn about effective labeling strategies"
                        else:  # Error/Issue
                            follow_up += "- Ask me to walk through the solution step-by-step\n"
                            follow_up += "- Request related documentation or resources\n"
                            follow_up += "- Get help with similar error scenarios\n"
                            follow_up += "- Learn prevention strategies"

                        follow_up += "\n**I have full context of your screenshot and am ready to help with follow-up questions!**"

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": follow_up
                        })

            st.success(f"✅ Analyzed {len(new_screenshots)} {analysis_type.lower()} screenshot(s)")
            st.rerun()
        else:
            st.success(f"✅ {len(uploaded_screenshots)} screenshot(s) analyzed")

    # SQL Query Analyzer Section
    st.markdown("""
    <div style="padding: 0.5rem 0; margin: 1.5rem 0 0.5rem 0; border-bottom: 1px solid #565869;">
        <h3 style="font-size: 0.875rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
            SQL Optimizer
        </h3>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📝 Paste SQL Query", expanded=False):
        sql_query = st.text_area(
            "Enter your SQL query:",
            height=150,
            placeholder="SELECT * FROM sales WHERE date > '2024-01-01'",
            help="Paste SQL queries from your Tableau data sources for optimization analysis"
        )

        if st.button("🚀 Analyze & Optimize SQL"):
            if sql_query.strip():
                with st.spinner("Analyzing SQL query..."):
                    analysis = analyze_sql_query(sql_query)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"**SQL Query Analysis:**\n\n{analysis}"
                    })
                    st.success("✅ SQL analysis complete!")
                    st.rerun()
            else:
                st.warning("Please enter a SQL query")

    # API Key status
    st.divider()
    if os.getenv("ANTHROPIC_API_KEY"):
        st.success("✅ API Key Loaded")
    else:
        st.error("❌ API Key Missing")
        st.info("Add ANTHROPIC_API_KEY to .env file")

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.uploaded_images = []
        st.rerun()

# Chat interface - no header needed for ChatGPT style

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your Tableau workbooks or data..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare context from uploaded files
    context = ""
    if st.session_state.uploaded_files_info:
        context = "**Context from uploaded files:**\n\n"
        for file_data in st.session_state.uploaded_files_info:
            context += create_analysis_prompt(
                file_data["type"],
                file_data["info"]
            ) + "\n\n---\n\n"

    # Create messages for Claude
    claude_messages = []

    # Add context if available
    if context:
        claude_messages.append({
            "role": "user",
            "content": context
        })
        claude_messages.append({
            "role": "assistant",
            "content": "I've reviewed the files you've uploaded. How can I help you analyze them?"
        })

    # Add conversation history
    for msg in st.session_state.messages:
        claude_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Get response from Claude
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_with_claude(claude_messages)
            st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Welcome message if no chat history
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem; max-width: 700px; margin: 0 auto;">
        <h2 style="color: #ECECEC; font-size: 1.75rem; margin-bottom: 2rem; font-weight: 600;">
            How can I help you today?
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards in a clean grid
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; border: 1px solid #3f3f3f; height: 140px;">
            <div style="font-size: 2rem; margin-bottom: 0.75rem;">📊</div>
            <h4 style="color: #ECECEC; margin-bottom: 0.5rem; font-size: 1rem; font-weight: 600;">Data Files</h4>
            <p style="color: #B4B4B4; font-size: 0.75rem;">Clean CSV & Excel</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; border: 1px solid #3f3f3f; height: 140px;">
            <div style="font-size: 2rem; margin-bottom: 0.75rem;">📸</div>
            <h4 style="color: #ECECEC; margin-bottom: 0.5rem; font-size: 1rem; font-weight: 600;">Screenshots</h4>
            <p style="color: #B4B4B4; font-size: 0.75rem;">Visual analysis</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; border: 1px solid #3f3f3f; height: 140px;">
            <div style="font-size: 2rem; margin-bottom: 0.75rem;">💾</div>
            <h4 style="color: #ECECEC; margin-bottom: 0.5rem; font-size: 1rem; font-weight: 600;">SQL</h4>
            <p style="color: #B4B4B4; font-size: 0.75rem;">Optimize queries</p>
        </div>
        """, unsafe_allow_html=True)
