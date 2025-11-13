# Tableau Analysis Assistant

A Streamlit-based chatbot powered by Claude AI that helps you analyze Tableau workbooks and data files. Get insights, recommendations, and best practices for your Tableau visualizations and dashboards.

## Features

- **Tableau Workbook Analysis**: Upload and analyze .twb and .twbx files
- **Data File Analysis**: Process CSV and Excel files for Tableau preparation
- **🆕 Data Cleaning & Preparation**: Automated data cleaning specifically optimized for Tableau
- **Interactive Chat**: Ask questions and get intelligent responses from Claude
- **File Parsing**: Automatically extract worksheets, dashboards, data sources, and calculated fields
- **Data Insights**: Get recommendations for visualizations, data quality checks, and optimizations
- **Best Practices**: Receive guidance on Tableau development standards
- **Export Ready Data**: Download cleaned, Tableau-optimized CSV files

## What You Can Analyze

### Tableau Files
- **.twb**: Tableau Workbook XML files
- **.twbx**: Tableau Packaged Workbooks

### Data Files
- **.csv**: Comma-separated values
- **.xlsx**: Excel spreadsheets

## Installation

### Prerequisites
- Python 3.13+ (or 3.10+)
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd /Users/nrjs/Desktop/Tableau_Project
   ```

2. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies** (already done if you followed setup)
   ```bash
   pip install anthropic streamlit pandas openpyxl python-dotenv
   ```

4. **Configure your API key**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

## Usage

### Starting the Application

1. **Activate the virtual environment** (if not already active)
   ```bash
   source venv/bin/activate
   ```

2. **Run the Streamlit app**
   ```bash
   streamlit run scripts/tableau_chatbot.py
   ```

3. **Access the app**

   The app will automatically open in your browser at `http://localhost:8501`

### Using the Chat Interface

1. **Upload Files**: Use the sidebar to upload Tableau workbooks or data files
2. **Analyze**: Click "Analyze Files" to process uploaded files
3. **Clean Data** (for CSV/Excel): Use the "Clean Data for Tableau" section to prepare your data
   - Click "Clean [filename]" to automatically clean the data
   - Review the cleaning report to see what was changed
   - Download the cleaned CSV file ready for Tableau
4. **Ask Questions**: Type questions in the chat input at the bottom
5. **Get Insights**: Receive analysis and recommendations from Claude

### Example Questions

- "What insights can you provide about this workbook's structure?"
- "How can I improve the performance of these dashboards?"
- "What visualizations would work best for this dataset?"
- "Review my calculated fields and suggest improvements"
- "What data quality issues do you see in this CSV?"
- "What are Tableau best practices for dashboard design?"

## Project Structure

```
Tableau_Project/
├── scripts/
│   └── tableau_chatbot.py    # Main Streamlit application
├── data/                      # Place your data files here
├── logs/                      # Application logs
├── reports/                   # Generated reports
├── venv/                      # Python virtual environment
├── .env                       # API keys (create from .env.example)
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Features Breakdown

### Tableau Workbook Parser
- Extracts worksheet names and structure
- Identifies dashboards and their components
- Lists data sources and connections
- Parses calculated fields and formulas
- Handles both .twb (XML) and .twbx (packaged) formats

### Data Analysis & Cleaning
- Provides column statistics and data types
- Identifies missing values and data quality issues
- **Automated Data Cleaning**:
  - Standardizes column names (removes special characters, spaces)
  - Removes empty rows and columns
  - Eliminates duplicate records
  - Auto-detects and converts data types (dates, numbers, text)
  - Handles missing values with indicator columns
  - Removes currency symbols and formatting from numeric data
  - Trims whitespace from text fields
  - Optimizes dataset size for Tableau performance
- Suggests appropriate visualization types
- Recommends data preparation steps
- Exports cleaned data as Tableau-ready CSV files

### Claude Integration
- Uses Claude Sonnet 4.5 for intelligent analysis
- Maintains conversation context across messages
- Provides contextual recommendations based on uploaded files

## Tips for Best Results

1. **Upload multiple files** to get comparative analysis
2. **Ask specific questions** about particular aspects of your work
3. **Include context** in your questions (e.g., "for a sales dashboard...")
4. **Request examples** when asking for best practices
5. **Follow up** on recommendations with implementation questions

## Troubleshooting

### API Key Issues
- Make sure `.env` file exists in the project root
- Verify your API key is correct and has no extra spaces
- Check that you have API credits available in your Anthropic account

### File Upload Issues
- Ensure files are valid Tableau workbooks or data files
- Check that .twbx files aren't corrupted
- For large files, increase timeout in Streamlit settings

### Performance
- For large workbooks, analysis may take longer
- Consider uploading smaller data samples for initial testing
- Close and reopen the app if it becomes unresponsive

## Limitations

- Very large workbooks (>100MB) may take time to process
- Complex calculated fields might not parse completely
- Some Tableau-specific features may not be fully analyzed
- Data source connections are identified but not validated

## Future Enhancements

Potential features to add:
- Export analysis reports as PDF
- Compare multiple workbooks
- Generate Tableau-ready data transformations
- Create calculation templates
- Dashboard screenshot analysis
- Performance profiling recommendations

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and rotate them regularly
- Be mindful of sensitive data in uploaded files
- The app runs locally and files are processed in memory

## Support

For issues or questions:
- Check the Anthropic API documentation: https://docs.anthropic.com/
- Review Streamlit documentation: https://docs.streamlit.io/
- Tableau documentation: https://help.tableau.com/

## License

This project is for educational and analytical purposes.

---

**Built with:**
- Streamlit for the web interface
- Anthropic Claude for AI analysis
- Python for backend processing
- pandas for data manipulation
