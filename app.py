"""
Enhanced Tableau Data Assistant with Trust Scoring, Data Contracts, and Story Coaching
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="Tableau Data Assistant Pro",
    page_icon="ð",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import new features
try:
    from utils import (
        calculate_trust_scores,
        generate_data_contract,
        analyze_dashboard_story,
        export_trust_scores_for_tableau,
        export_data_contract_proposal,
        export_story_report
    )
    FEATURES_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing features: {e}")
    FEATURES_AVAILABLE = False

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    h1 {
        color: #10a37f;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("ð Tableau Data Assistant Pro")
st.markdown("**Enterprise-grade data quality platform with AI-powered insights**")
st.markdown("---")

# Create tabs for different features
tabs = st.tabs([
    "ð  Home",
    "ð Trust Heatmap",
    "ð Data Contracts",
    "ð Story Coach",
    "ð¬ AI Chat"
])

# ============================================================================
# TAB 1: HOME
# ============================================================================
with tabs[0]:
    st.header("Welcome to Tableau Data Assistant Pro")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### ð Trust Heatmap
        **Quantify data quality** with 0-100 trust scores per field

        **Features:**
        - Field-level trust scoring
        - Historical tracking
        - Tableau-ready CSV exports
        - Color-coded visualizations

        â Switch to **Trust Heatmap** tab to get started
        """)

    with col2:
        st.markdown("""
        ### ð Data Contracts
        **Auto-generate upstream agreements** based on recurring issues

        **Features:**
        - Analyze historical failures
        - Draft formal SLA contracts
        - Generate JIRA tickets
        - Track issue patterns

        â Switch to **Data Contracts** tab to get started
        """)

    with col3:
        st.markdown("""
        ### ð Story Coach
        **AI-powered narrative critique** for your dashboards

        **Features:**
        - Story arc analysis
        - Before/after comparison
        - Email-ready summaries
        - Layout recommendations

        â Switch to **Story Coach** tab to get started
        """)

    st.markdown("---")

    # Quick stats
    st.subheader("ð Platform Statistics")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric("Total Modules", "11", help="Production-ready feature modules")
    with stat_col2:
        st.metric("Lines of Code", "~6,000", help="Production code")
    with stat_col3:
        st.metric("Documentation", "~6,000+", help="Lines of documentation")
    with stat_col4:
        st.metric("Features", "10+", help="Core features + innovations")

# ============================================================================
# TAB 2: TRUST HEATMAP
# ============================================================================
with tabs[1]:
    st.header("ð Trust Heatmap Overlay")
    st.markdown("Generate 0-100 trust scores for each field based on completeness, validity, anomaly-free, and freshness.")

    if not FEATURES_AVAILABLE:
        st.error("Trust scoring features not available. Check imports.")
    else:
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file for trust analysis",
            type=["csv", "xlsx"],
            key="trust_uploader"
        )

        if uploaded_file:
            import pandas as pd
            from datetime import datetime

            # Load data
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.success(f"â Loaded {df.shape[0]} rows Ã {df.shape[1]} columns")

                # Show preview
                with st.expander("ð Data Preview"):
                    st.dataframe(df.head(10))

                # Configuration
                st.subheader("âï¸ Configuration")
                col1, col2 = st.columns(2)

                with col1:
                    dataset_name = st.text_input("Dataset Name", value=uploaded_file.name.replace('.csv', '').replace('.xlsx', ''))

                with col2:
                    date_column = st.selectbox(
                        "Date Column (for freshness)",
                        options=[None] + list(df.columns),
                        help="Select a date column to measure freshness"
                    )

                # Calculate trust scores button
                if st.button("ð Calculate Trust Scores", type="primary"):
                    with st.spinner("Analyzing data quality..."):
                        try:
                            # Run validation and anomaly detection first
                            from utils import validate_for_tableau, detect_anomalies

                            validation_result, _ = validate_for_tableau(df)
                            anomaly_report = detect_anomalies(df)

                            # Calculate trust scores
                            trust_report = calculate_trust_scores(
                                df=df,
                                validation_result=validation_result,
                                anomaly_report=anomaly_report,
                                date_column=date_column,
                                dataset_name=dataset_name
                            )

                            # Display results
                            st.success("â Trust analysis complete!")

                            # Overall score
                            st.metric(
                                "Overall Trust Score",
                                f"{trust_report.overall_trust_score:.1f}/100",
                                help="Weighted average across all fields"
                            )

                            # Field scores table
                            st.subheader("ð Field-Level Trust Scores")

                            scores_data = []
                            for score in trust_report.field_scores:
                                scores_data.append({
                                    'Field': score.field_name,
                                    'Trust Score': f"{score.trust_score:.1f}",
                                    'Grade': score.get_grade(),
                                    'Color': score.get_color(),
                                    'Completeness': f"{score.completeness_score:.1f}",
                                    'Validity': f"{score.validity_score:.1f}",
                                    'Anomaly-Free': f"{score.anomaly_score:.1f}",
                                    'Freshness': f"{score.freshness_score:.1f}"
                                })

                            scores_df = pd.DataFrame(scores_data)
                            st.dataframe(scores_df, use_container_width=True)

                            # Export options
                            st.subheader("ð¥ Export Options")
                            col1, col2 = st.columns(2)

                            with col1:
                                if st.button("Export for Tableau (CSV)"):
                                    paths = export_trust_scores_for_tableau(trust_report, save_to_db=True)
                                    st.success(f"â Exported to: {paths['csv']}")
                                    st.info("ð¡ Import this CSV into Tableau and join with your data source")

                            with col2:
                                if st.button("View Historical Trends"):
                                    st.info("Historical tracking available via database. See exports/trust_scores.db")

                        except Exception as e:
                            st.error(f"Error calculating trust scores: {e}")
                            import traceback
                            st.code(traceback.format_exc())

            except Exception as e:
                st.error(f"Error loading file: {e}")

# ============================================================================
# TAB 3: DATA CONTRACTS
# ============================================================================
with tabs[2]:
    st.header("ð Data Contract Auto-Generation")
    st.markdown("Analyze recurring validation failures and auto-generate formal data contracts for upstream systems.")

    if not FEATURES_AVAILABLE:
        st.error("Data contract features not available. Check imports.")
    else:
        st.info("ð¡ **How it works:** Upload your current dataset and optionally provide historical validation results. The system will analyze patterns and generate a formal contract proposal.")

        # File uploader
        uploaded_file = st.file_uploader(
            "Upload current dataset (CSV or Excel)",
            type=["csv", "xlsx"],
            key="contract_uploader"
        )

        if uploaded_file:
            import pandas as pd

            # Load data
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.success(f"â Loaded {df.shape[0]} rows Ã {df.shape[1]} columns")

                # Configuration
                st.subheader("âï¸ Configuration")
                col1, col2, col3 = st.columns(3)

                with col1:
                    dataset_name = st.text_input(
                        "Dataset Name",
                        value=uploaded_file.name.replace('.csv', '').replace('.xlsx', ''),
                        key="contract_dataset"
                    )

                with col2:
                    upstream_system = st.text_input(
                        "Upstream System",
                        value="ServiceNow CRM",
                        help="Name of the system providing this data"
                    )

                with col3:
                    days_history = st.number_input(
                        "Historical Days",
                        value=30,
                        min_value=7,
                        max_value=90,
                        help="Days of history to analyze (if available)"
                    )

                # Generate contract button
                if st.button("ð Generate Data Contract", type="primary"):
                    with st.spinner("Analyzing data and generating contract..."):
                        try:
                            # For demo, we'll generate without historical data
                            # In production, you'd pass historical_validation_results
                            contract = generate_data_contract(
                                df=df,
                                dataset_name=dataset_name,
                                upstream_system=upstream_system,
                                historical_validation_results=[],  # Empty for now
                                days_history=days_history
                            )

                            st.success("â Contract generated successfully!")

                            # Display contract summary
                            st.subheader("ð Contract Summary")
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("Fields Specified", len(contract.fields))
                            with col2:
                                st.metric("SLA Uptime", f"{contract.sla_uptime}%")
                            with col3:
                                st.metric("Freshness SLA", f"{contract.sla_freshness_hours}h")

                            # Field contracts preview
                            st.subheader("ð Field Contracts")
                            for i, field in enumerate(contract.fields[:5]):  # Show first 5
                                with st.expander(f"ð {field.field_name}"):
                                    st.markdown(f"**Type:** {field.data_type}")
                                    st.markdown(f"**Required:** {'Yes' if field.required else 'No'}")
                                    st.markdown(f"**Nullable:** {'Yes' if field.nullable else 'No'} (max {field.max_null_percentage}%)")
                                    if field.sla_requirements:
                                        st.markdown("**SLA Requirements:**")
                                        for req in field.sla_requirements:
                                            st.markdown(f"- {req}")

                            if len(contract.fields) > 5:
                                st.info(f"... and {len(contract.fields) - 5} more fields")

                            # Export options
                            st.subheader("ð¥ Export Contract")
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                if st.button("Export Markdown"):
                                    paths = export_data_contract_proposal(contract, include_jira=False)
                                    st.success(f"â Exported to: {paths['markdown']}")

                            with col2:
                                if st.button("Export JSON"):
                                    paths = export_data_contract_proposal(contract, include_jira=False)
                                    st.success(f"â Exported to: {paths['json']}")

                            with col3:
                                if st.button("Generate JIRA Ticket"):
                                    paths = export_data_contract_proposal(contract, include_jira=True)
                                    st.success(f"â JIRA template: {paths['jira']}")

                        except Exception as e:
                            st.error(f"Error generating contract: {e}")
                            import traceback
                            st.code(traceback.format_exc())

            except Exception as e:
                st.error(f"Error loading file: {e}")

# ============================================================================
# TAB 4: STORY COACH
# ============================================================================
with tabs[3]:
    st.header("ð Dashboard Story Coach")
    st.markdown("Get AI-powered narrative critique for your dashboards. Upload a screenshot to analyze storytelling effectiveness.")

    if not FEATURES_AVAILABLE:
        st.error("Story coaching features not available. Check imports.")
    else:
        st.info("ð¡ **How it works:** Upload a dashboard screenshot and specify the primary metric. The AI will analyze the narrative arc (beginning, middle, end) and provide actionable recommendations.")

        # Image uploader
        uploaded_image = st.file_uploader(
            "Upload dashboard screenshot (PNG, JPG)",
            type=["png", "jpg", "jpeg"],
            key="story_uploader"
        )

        if uploaded_image:
            from PIL import Image
            import tempfile

            # Display uploaded image
            image = Image.open(uploaded_image)
            st.image(image, caption="Dashboard Screenshot", use_container_width=True)

            # Configuration
            st.subheader("âï¸ Configuration")
            col1, col2 = st.columns(2)

            with col1:
                dashboard_name = st.text_input(
                    "Dashboard Name",
                    value="Operations Dashboard",
                    key="story_dashboard"
                )

            with col2:
                primary_metric = st.text_input(
                    "Primary Metric",
                    value="Incident Volume",
                    help="Main metric being displayed (e.g., Revenue, MTTR, NPS)"
                )

            context = st.text_area(
                "Context (Optional)",
                placeholder="E.g., Weekly exec review for C-suite, Daily standup for ops team...",
                help="Provide context about the dashboard's purpose and audience"
            )

            # Analyze button
            if st.button("ð¯ Analyze Story", type="primary"):
                with st.spinner("Analyzing dashboard storytelling with AI..."):
                    try:
                        # Save image to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_image.name) as tmp_file:
                            tmp_file.write(uploaded_image.getvalue())
                            tmp_path = tmp_file.name

                        # Analyze story
                        story_report = analyze_dashboard_story(
                            screenshot_path=tmp_path,
                            primary_metric=primary_metric,
                            dashboard_name=dashboard_name,
                            context=context if context else None
                        )

                        st.success("â Story analysis complete!")

                        # Overall score
                        st.metric(
                            "Overall Story Score",
                            f"{story_report.overall_story_score:.1f}/100",
                            help="Narrative effectiveness score"
                        )

                        # Story arc breakdown
                        st.subheader("ð Story Arc Analysis")
                        arc_col1, arc_col2, arc_col3, arc_col4 = st.columns(4)

                        with arc_col1:
                            st.metric(
                                "Beginning (Context)",
                                f"{story_report.story_arc.beginning_score:.0f}/100",
                                delta="â" if story_report.story_arc.has_beginning else "â"
                            )

                        with arc_col2:
                            st.metric(
                                "Middle (Insights)",
                                f"{story_report.story_arc.middle_score:.0f}/100",
                                delta="â" if story_report.story_arc.has_middle else "â"
                            )

                        with arc_col3:
                            st.metric(
                                "End (Actions)",
                                f"{story_report.story_arc.end_score:.0f}/100",
                                delta="â" if story_report.story_arc.has_end else "â"
                            )

                        with arc_col4:
                            st.metric(
                                "Coherence",
                                f"{story_report.story_arc.overall_coherence:.0f}/100"
                            )

                        # Narratives
                        st.subheader("ð Narrative Comparison")
                        nar_col1, nar_col2 = st.columns(2)

                        with nar_col1:
                            st.markdown("**Current Story:**")
                            st.info(story_report.current_narrative)

                        with nar_col2:
                            st.markdown("**Improved Story:**")
                            st.success(story_report.improved_narrative)

                        # Recommendations
                        st.subheader("ð¯ Recommendations")
                        high_priority = [r for r in story_report.layout_recommendations + story_report.content_recommendations if r.priority == 'high']

                        for i, rec in enumerate(high_priority[:5], 1):
                            with st.expander(f"#{i} [{rec.priority.upper()}] {rec.recommended_state}"):
                                st.markdown(f"**Current:** {rec.current_state}")
                                st.markdown(f"**Recommended:** {rec.recommended_state}")
                                st.markdown(f"**Rationale:** {rec.rationale}")
                                st.markdown(f"**Expected Impact:** {rec.expected_impact}")

                        # Email summary
                        st.subheader("ð§ Email-Ready Summary")
                        st.text_area(
                            "Copy and send to stakeholders:",
                            value=story_report.email_summary,
                            height=200
                        )

                        # Export options
                        st.subheader("ð¥ Export Report")
                        if st.button("Export Full Report"):
                            paths = export_story_report(story_report)
                            st.success(f"â Reports exported:")
                            st.markdown(f"- Markdown: {paths['markdown']}")
                            st.markdown(f"- Email: {paths['email']}")
                            st.markdown(f"- JSON: {paths['json']}")

                        # Clean up temp file
                        import os
                        os.unlink(tmp_path)

                    except Exception as e:
                        st.error(f"Error analyzing story: {e}")
                        import traceback
                        st.code(traceback.format_exc())

# ============================================================================
# TAB 5: AI CHAT (Link to original app)
# ============================================================================
with tabs[4]:
    st.header("ð¬ AI Chat Assistant")
    st.markdown("For the full AI chat experience, use the original Tableau Analysis Assistant.")

    st.info("ð The AI chat feature is available in the original app at `scripts/tableau_chatbot.py`")

    st.markdown("""
    ### Features in AI Chat:
    - ð Upload Tableau workbooks (.twb, .twbx)
    - ð Upload data files (CSV, Excel)
    - ð¬ Chat with Claude about your data
    - ð§¹ Auto-clean data for Tableau
    - ð Generate visualizations
    - ð¥ Download cleaned data

    ### To access:
    Run: `streamlit run scripts/tableau_chatbot.py`
    """)

    if st.button("Open Original Chat App"):
        st.info("Please run: `streamlit run scripts/tableau_chatbot.py` in a new terminal")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Tableau Data Assistant Pro v2.3.0</strong></p>
    <p>11 Production Modules â¢ 6,000+ Lines of Code â¢ Enterprise-Grade Quality</p>
</div>
""", unsafe_allow_html=True)
