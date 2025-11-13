"""
Dual-Monitor Optimized Tableau Data Assistant
Left Monitor: Tableau (captured with red border)
Right Monitor: Browser Chat (not captured)
"""
import streamlit as st
import anthropic
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import utilities
from utils.screen_recorder import LiveAnalysisSession
from utils.monitor_selector import MonitorSelector, select_monitor
from utils.window_selector import show_capture_border
from utils.tableau_expert import get_tableau_expert_context
from utils.csv_cleaner import clean_csv, get_data_discrepancies
from utils.data_quality import calculate_quality_score
from utils.logger import get_logger
import pandas as pd
import io

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Page configuration  
st.set_page_config(
    page_title="Tableau Live Analysis - Dual Monitor",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for dual monitor
st.markdown("""
<style>
    .stApp {
        background-color: #212121;
    }

    h1, h2, h3, p {
        color: #ECECEC;
    }

    .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #0d8f6d;
    }

    .dual-monitor-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        color: white;
    }

    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #ff4444;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .monitor-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
        margin: 4px;
    }

    .monitor-left {
        background-color: #ff6b6b;
        color: white;
    }

    .monitor-right {
        background-color: #4ecdc4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "live_session" not in st.session_state:
    st.session_state.live_session = None
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "analysis_interval" not in st.session_state:
    st.session_state.analysis_interval = 15
if "selected_monitor" not in st.session_state:
    st.session_state.selected_monitor = None
if "border_overlay" not in st.session_state:
    st.session_state.border_overlay = None
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "discrepancy_report" not in st.session_state:
    st.session_state.discrepancy_report = None
if "cleaning_report" not in st.session_state:
    st.session_state.cleaning_report = None
if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None

def get_anthropic_client():
    """Initialize Anthropic client"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

# Header
st.markdown("""
<div style="text-align: center; padding: 1rem 0 2rem 0;">
    <h1>🖥️ Dual-Monitor Tableau Analysis</h1>
    <p style="font-size: 0.875rem; color: #B4B4B4;">
        Left Monitor: Tableau (captured) • Right Monitor: Chat (you're here!)
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🖥️ Dual Monitor Setup")

    # Monitor setup explanation
    if not st.session_state.session_active:
        st.markdown("""
        <div style="background-color: #2f2f2f; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h4 style="margin-top: 0;">Perfect for Dual Screens!</h4>
            <p style="font-size: 0.9em; margin-bottom: 0.5rem;">
                <span class="monitor-badge monitor-left">LEFT</span> Tableau (captured)<br>
                <span class="monitor-badge monitor-right">RIGHT</span> Browser Chat (this window)
            </p>
            <p style="font-size: 0.85em; color: #B4B4B4;">
                The AI will only watch your Tableau monitor and provide feedback here.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Analysis Settings")

        # Quick setup buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🖥️ Left Monitor\n(Tableau)", use_container_width=True):
                selector = MonitorSelector()
                left_mon = min(selector.get_monitors(), key=lambda m: m['x'])
                st.session_state.selected_monitor = left_mon
                st.success(f"✓ Monitor {left_mon['id']} selected")

        with col2:
            if st.button("🖵 Custom\nSelection", use_container_width=True):
                region = select_monitor("Select Monitor for Tableau")
                if region:
                    st.session_state.selected_monitor = {'x': region[0], 'y': region[1], 
                                                        'width': region[2], 'height': region[3]}
                    st.success("✓ Monitor selected")

        # Show selected monitor
        if st.session_state.selected_monitor:
            mon = st.session_state.selected_monitor
            st.info(f"📐 Capture: {mon['width']}×{mon['height']} at ({mon['x']}, {mon['y']})")

        st.markdown("---")

        # Analysis mode
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["Dashboard Review", "Error Detection", "Performance Check", "Design Critique", "Custom"],
            help="What should I focus on?"
        )

        # Custom prompt
        if analysis_mode == "Custom":
            custom_prompt = st.text_area(
                "Custom Instructions",
                placeholder="Specific things to watch for...",
                height=100
            )
        else:
            custom_prompt = None

        # Interval
        interval = st.slider(
            "Check Every (seconds)",
            5, 60, 15, 5,
            help="How often to analyze Tableau"
        )
        st.session_state.analysis_interval = interval

        st.markdown("---")

        # Start button
        if st.button("🚀 Start Monitoring", type="primary", use_container_width=True):
            if not st.session_state.selected_monitor:
                st.error("Please select a monitor first!")
            else:
                try:
                    client = get_anthropic_client()

                    # Get Tableau expert prompt
                    prompt_type = {
                        "Dashboard Review": "design_review",
                        "Error Detection": "calculation_error",
                        "Performance Check": "performance_issue",
                        "Design Critique": "design_review"
                    }.get(analysis_mode, "general")

                    expert_prompt = get_tableau_expert_context(prompt_type)
                    full_prompt = expert_prompt + "\n\n" + (custom_prompt or "")

                    # Create session
                    session = LiveAnalysisSession(client, analysis_prompt=full_prompt)

                    # Get monitor region
                    mon = st.session_state.selected_monitor
                    region = (mon['x'], mon['y'], mon['width'], mon['height'])

                    session.start_session(region=region)

                    # Show red border
                    border = show_capture_border(mon['x'], mon['y'], mon['width'], mon['height'])
                    st.session_state.border_overlay = border

                    st.session_state.live_session = session
                    st.session_state.session_active = True
                    st.session_state.analysis_mode = analysis_mode

                    logger.info(f"Dual-monitor session started: {analysis_mode}")
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to start: {e}")
                    logger.error(f"Session start failed: {e}")

    else:
        # Active session
        st.markdown("""
        <div class="dual-monitor-indicator">
            <div><span class="live-indicator"></span><strong>MONITORING ACTIVE</strong></div>
            <div style="font-size: 0.9em; margin-top: 0.5rem;">
                Watching your Tableau screen
            </div>
        </div>
        """, unsafe_allow_html=True)

        mon = st.session_state.selected_monitor
        st.metric("Capturing", f"{mon['width']}×{mon['height']}")
        st.metric("Mode", st.session_state.analysis_mode)
        st.metric("Interval", f"{st.session_state.analysis_interval}s")

        st.markdown("---")

        # Manual analyze
        if st.button("🔍 Analyze Now", use_container_width=True):
            with st.spinner("Analyzing Tableau..."):
                result = st.session_state.live_session.analyze_current_screen()
                if result['success']:
                    st.session_state.last_analysis = result
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"**📊 Analysis ({result['timestamp'].strftime('%H:%M:%S')})**\n\n{result['analysis']}",
                        "timestamp": result['timestamp']
                    })
                    st.rerun()
                else:
                    st.error(f"Failed: {result.get('error', 'Unknown')}")

        # Stop button
        if st.button("⏹️ Stop Monitoring", use_container_width=True):
            if st.session_state.live_session:
                st.session_state.live_session.stop_session()
            if st.session_state.border_overlay:
                st.session_state.border_overlay.hide()
            st.session_state.live_session = None
            st.session_state.session_active = False
            st.session_state.border_overlay = None
            logger.info("Session stopped")
            st.rerun()

        st.markdown("---")

        # Stats
        if st.session_state.live_session:
            history = st.session_state.live_session.get_analysis_history()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Analyses", len(history))
            with col2:
                if history:
                    tokens = sum(h.get('tokens_used', 0) for h in history)
                    st.metric("Tokens", f"{tokens:,}")

# CSV Data Tools Section
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 CSV Data Tools")

    st.markdown("""
    <div style="background: #2f2f2f; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.85em;">
        💡 <strong>Auto-Analysis:</strong> Upload a CSV to automatically check for issues and get a cleaned version!
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=['csv'],
        help="Upload a CSV file - automatically analyzes and cleans"
    )

    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            st.success(f"✓ Loaded: {len(df)} rows × {len(df.columns)} cols")

            # Check if this is a new file
            file_changed = (
                'uploaded_filename' not in st.session_state or
                st.session_state.uploaded_filename != uploaded_file.name
            )

            # Store in session state
            st.session_state.uploaded_df = df
            st.session_state.uploaded_filename = uploaded_file.name

            # Auto-analyze on new file upload
            if file_changed:
                with st.spinner("🔍 Analyzing for discrepancies..."):
                    discrepancies = get_data_discrepancies(df)
                    st.session_state.discrepancy_report = discrepancies
                    logger.info(f"Auto-analyzed CSV: {uploaded_file.name}")

                with st.spinner("🧹 Cleaning data automatically..."):
                    cleaned_df, report = clean_csv(df)
                    st.session_state.cleaned_df = cleaned_df
                    st.session_state.cleaning_report = report
                    logger.info(f"Auto-cleaned CSV: {uploaded_file.name}")

                st.rerun()

            # Manual actions
            st.markdown("---")
            st.markdown("**Manual Actions:**")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Re-analyze", use_container_width=True):
                    with st.spinner("Re-analyzing..."):
                        discrepancies = get_data_discrepancies(df)
                        st.session_state.discrepancy_report = discrepancies
                        st.rerun()

            with col2:
                if st.button("🧹 Re-clean", use_container_width=True):
                    with st.spinner("Re-cleaning..."):
                        cleaned_df, report = clean_csv(df)
                        st.session_state.cleaned_df = cleaned_df
                        st.session_state.cleaning_report = report
                        st.rerun()

        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            logger.error(f"CSV upload error: {e}")

# Main content
if st.session_state.session_active:
    # Auto-analysis
    if st.session_state.last_analysis is None or \
       (datetime.now() - st.session_state.last_analysis['timestamp']).total_seconds() > st.session_state.analysis_interval:

        with st.spinner("🔍 Auto-analyzing Tableau..."):
            result = st.session_state.live_session.analyze_current_screen()
            if result['success']:
                st.session_state.last_analysis = result
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**🎯 Auto-Check ({result['timestamp'].strftime('%H:%M:%S')})**\n\n{result['analysis']}",
                    "timestamp": result['timestamp']
                })
                st.rerun()

# Display CSV Reports
if 'discrepancy_report' in st.session_state and st.session_state.discrepancy_report:
    st.subheader("🔍 CSV Discrepancy Report")

    report = st.session_state.discrepancy_report

    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Issues", report['summary']['total_issues'])
    with col2:
        st.metric("Severity", report['summary']['severity'])
    with col3:
        if st.button("Clear Report"):
            st.session_state.discrepancy_report = None
            st.rerun()

    st.info(f"**Recommendation:** {report['summary']['recommendation']}")

    # Detailed issues
    with st.expander("📋 Missing Values", expanded=True):
        if report['missing_values']['columns_with_missing']:
            for col, info in report['missing_values']['columns_with_missing'].items():
                st.warning(f"**{col}**: {info['count']} missing ({info['percentage']}%)")
        else:
            st.success("No missing values found!")

    with st.expander("🔄 Duplicates"):
        if report['duplicates']['total_duplicates'] > 0:
            st.warning(f"Found {report['duplicates']['total_duplicates']} duplicate rows ({report['duplicates']['percentage']}%)")
        else:
            st.success("No duplicates found!")

    with st.expander("📊 Outliers"):
        if report['outliers']:
            for col, info in report['outliers'].items():
                st.warning(f"**{col}**: {info['count']} outliers ({info['percentage']}%) - Range: {info['range']}")
        else:
            st.success("No outliers detected!")

    with st.expander("📝 Text Issues"):
        if report['text_issues']:
            for issue in report['text_issues']:
                st.warning(f"**{issue['column']}**: {issue['issue']}")
        else:
            st.success("No text issues found!")

    st.markdown("---")

if 'cleaning_report' in st.session_state and st.session_state.cleaning_report:
    st.subheader("🧹 CSV Cleaning Report")

    report = st.session_state.cleaning_report

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Size", report['summary']['original_size'])
    with col2:
        st.metric("Final Size", report['summary']['final_size'])
    with col3:
        st.metric("Improvements", report['summary']['quality_improvements'])

    # Operations performed
    with st.expander("✅ Cleaning Operations", expanded=True):
        for op in report['operations']:
            st.success(f"✓ {op}")

    # Recommendations
    with st.expander("💡 Recommendations"):
        for rec in report['recommendations']:
            st.info(rec)

    # Download cleaned CSV
    if 'cleaned_df' in st.session_state and st.session_state.cleaned_df is not None:
        csv_buffer = io.StringIO()
        st.session_state.cleaned_df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()

        original_name = st.session_state.get('uploaded_filename', 'data.csv')
        cleaned_name = original_name.replace('.csv', '_cleaned.csv')

        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_str,
            file_name=cleaned_name,
            mime='text/csv',
            use_container_width=True
        )

        if st.button("Clear Report", key="clear_cleaning"):
            st.session_state.cleaning_report = None
            st.session_state.cleaned_df = None
            st.rerun()

    st.markdown("---")

# Display messages
if st.session_state.messages:
    st.subheader("💬 Analysis Feed")
    for message in reversed(st.session_state.messages[-20:]):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"⏰ {message['timestamp'].strftime('%I:%M:%S %p')}")
else:
    # Welcome
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem;">
        <h2>Welcome to Dual-Monitor Analysis! 🖥️📊</h2>
        <p style="color: #B4B4B4; max-width: 700px; margin: 1rem auto;">
            This mode is optimized for your dual-monitor setup:
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; height: 200px;">
            <div style="font-size: 3rem;">🖥️</div>
            <h4 style="color: #ECECEC;">Left Monitor</h4>
            <p style="color: #B4B4B4; font-size: 0.9em;">
                Tableau<br>
                (being captured)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; height: 200px;">
            <div style="font-size: 3rem;">🔴</div>
            <h4 style="color: #ECECEC;">Red Border</h4>
            <p style="color: #B4B4B4; font-size: 0.9em;">
                Shows capture area<br>
                (on Tableau monitor)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; height: 200px;">
            <div style="font-size: 3rem;">💬</div>
            <h4 style="color: #ECECEC;">Right Monitor</h4>
            <p style="color: #B4B4B4; font-size: 0.9em;">
                This browser<br>
                (feedback appears here)
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    ### 🚀 Quick Start

    1. **Select Monitor** (sidebar) → Choose "Left Monitor" or custom
    2. **Choose Mode** → Dashboard Review, Error Detection, etc.
    3. **Click "Start Monitoring"** → Red border appears on Tableau!
    4. **Work in Tableau** → AI watches and provides feedback here
    5. **Get Insights** → Appears in this chat automatically

    💡 **Pro Tip**: Arrange windows so you can see both monitors at once!
    """)

# Chat input
if prompt := st.chat_input("Ask about Tableau..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = get_anthropic_client()
            
            context = ""
            if st.session_state.session_active and st.session_state.last_analysis:
                context = f"\n\nCurrent screen context:\n{st.session_state.last_analysis['analysis']}\n\n---\n\n"

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": context + prompt}]
            )

            answer = response.content[0].text
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
