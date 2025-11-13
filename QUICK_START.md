## 🚀 Quick Start Guide - Enhanced Tableau Data Assistant

### Installation (5 minutes)

```bash
# Navigate to project
cd /Users/nrjs/Desktop/Tableau_Project

# Activate virtual environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "from utils import get_logger; print('✅ Installation successful!')"
```

### Run the Application

```bash
# Start the Streamlit app
streamlit run scripts/tableau_chatbot.py
```

### Quick Feature Demo

#### 1. Use Enhanced Logging

```python
from utils import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.error("Something went wrong")

# Check logs
tail -f logs/app.log
```

#### 2. Cache Expensive Operations

```python
from utils import cached

@cached(ttl=3600, key_prefix="analysis")
def expensive_analysis(dataframe):
    # This will be cached for 1 hour
    return perform_complex_analysis(dataframe)
```

#### 3. Calculate Data Quality

```python
from utils import calculate_quality_score

quality = calculate_quality_score(df)
print(f"Quality Score: {quality['overall_score']}/100")
print(f"Grade: {quality['grade']}")
```

#### 4. Create Interactive Visualizations

```python
from utils.visualizations import create_visualizations

vizualizations = create_visualizations(df, quality_score)

# In Streamlit:
st.plotly_chart(visualizations['quality_gauge'])
st.plotly_chart(visualizations['correlations'])
```

#### 5. Generate Reports

```python
from utils import get_report_generator

report_gen = get_report_generator()

# PDF Report
pdf_path = report_gen.generate_pdf_report(
    filename="my_analysis",
    title="Data Analysis Report",
    data_summary=info,
    quality_score=quality_score
)

# HTML Report
html_path = report_gen.generate_html_report(
    filename="my_analysis",
    title="Data Analysis Report",
    data_summary=info,
    quality_score=quality_score
)
```

#### 6. Save/Load Sessions

```python
from utils import get_session_manager

session_mgr = get_session_manager()

# Save current session
session_id = session_mgr.save_session(
    messages=messages,
    files_info=files,
    session_name="My Analysis"
)

# Load session later
session_data = session_mgr.load_session(session_id)
messages = session_data['messages']
```

#### 7. Security Validation

```python
from utils import get_security_manager

security = get_security_manager()

# Validate uploaded file
is_valid, error = security.validate_file(file_path, file_content)
if not is_valid:
    print(f"Security error: {error}")

# Encrypt API key
encrypted = security.encrypt_api_key("sk-ant-...")
decrypted = security.decrypt_api_key(encrypted)
```

#### 8. Statistical Analysis

```python
from utils import perform_statistical_analysis

stats = perform_statistical_analysis(df)

# Check normality
print(stats['normality_tests'])

# Find correlations
print(stats['correlations'])

# Detect outliers
print(stats['outliers'])
```

### Configuration

Edit `config/settings.py` to customize:

```python
# File limits
MAX_FILE_SIZE_MB = 500

# Quality weights
QUALITY_WEIGHTS = {
    "completeness": 0.30,
    "uniqueness": 0.20,
    "validity": 0.25,
    "consistency": 0.15,
    "timeliness": 0.10
}

# Cache settings
CACHE_TTL = 3600  # 1 hour
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_data_quality.py -v

# With coverage
pytest tests/ --cov=utils --cov-report=html
```

### Troubleshooting

**Module not found?**
```bash
export PYTHONPATH="${PYTHONPATH}:/Users/nrjs/Desktop/Tableau_Project"
```

**python-magic errors?**
```bash
# macOS
brew install libmagic

# Linux
sudo apt-get install libmagic1
```

**Permission errors on cache/logs?**
```bash
chmod -R 755 cache/ logs/ sessions/ exports/
```

### Project Structure

```
Tableau_Project/
├── config/                 # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── logger.py          # Logging system
│   ├── cache_manager.py   # Caching
│   ├── security.py        # Security
│   ├── data_quality.py    # Quality scoring
│   ├── statistics.py      # Statistical analysis
│   ├── session_manager.py # Session persistence
│   ├── report_generator.py # Reports
│   └── visualizations.py  # Plotly charts
├── scripts/
│   ├── tableau_chatbot.py # Main application
│   └── tableau_chatbot_backup.py
├── tests/                 # Unit tests
│   ├── __init__.py
│   └── test_data_quality.py
├── cache/                 # Cached analyses
├── sessions/              # Saved sessions
├── exports/               # Generated reports
├── logs/                  # Application logs
├── requirements.txt
├── IMPLEMENTATION_GUIDE.md
└── QUICK_START.md
```

### Key Features Ready to Use

✅ **Logging**: Automatic file and console logging
✅ **Caching**: Speeds up repeated analyses
✅ **Security**: File validation and API key encryption
✅ **Quality Scoring**: 5-dimension data quality assessment
✅ **Statistics**: Normality tests, correlations, t-tests, chi-square
✅ **Sessions**: Save and restore your work
✅ **Reports**: Beautiful PDF and HTML exports
✅ **Visualizations**: Interactive Plotly dashboards

### Example Workflow

```python
# 1. Load and validate data
df = pd.read_csv("data.csv")

# 2. Calculate quality score
quality = calculate_quality_score(df)

# 3. Run statistical analysis
stats = perform_statistical_analysis(df)

# 4. Create visualizations
viz = create_visualizations(df, quality)

# 5. Generate report
report_gen.generate_pdf_report(
    filename="analysis_report",
    title="Data Analysis",
    data_summary={'rows': len(df), 'columns': len(df.columns)},
    quality_score=quality,
    statistical_analysis=stats
)

# 6. Save session
session_mgr.save_session(
    messages=messages,
    files_info=[{'name': 'data.csv', 'info': quality}],
    session_name="My Analysis Session"
)
```

### Next Steps

1. ✅ Install dependencies
2. ✅ Run tests to verify everything works
3. 📝 Integrate features into main app (see IMPLEMENTATION_GUIDE.md)
4. 🎨 Customize settings in config/settings.py
5. 🚀 Start analyzing data!

### Support

- Check logs: `tail -f logs/app.log`
- Clear cache: `rm -rf cache/*`
- Reset sessions: `rm -rf sessions/*`
- View documentation: `IMPLEMENTATION_GUIDE.md`

Happy analyzing! 🎉
