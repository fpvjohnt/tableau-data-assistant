"""
Enhanced Tableau Data Assistant with Live Screen Analysis
Replaces screenshot uploads with real-time screen recording and analysis
"""
import streamlit as st
import anthropic
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import utilities
from utils.screen_recorder import LiveAnalysisSession, create_live_session
from utils.logger import get_logger
from utils import calculate_quality_score

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Tableau Analysis Assistant - Live Edition",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (keeping your dark theme)
st.markdown("""
<style>
    .stApp {
        background-color: #212121;
    }

    .main .block-container {
        padding-top: 2rem;
        background-color: #212121;
    }

    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2f2f2f;
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
    }

    .stButton > button:hover {
        background-color: #0d8f6d;
    }

    /* Live session indicator */
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

    .session-active {
        background-color: #1a3a2e;
        border: 2px solid #10a37f;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .analysis-card {
        background-color: #2f2f2f;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #10a37f;
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
    st.session_state.analysis_interval = 10  # seconds

def get_anthropic_client():
    """Initialize Anthropic client with API key"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found. Please add it to your .env file.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

# Main UI
st.markdown("""
<div style="text-align: center; padding: 1rem 0 2rem 0;">
    <h1 style="margin-bottom: 0.5rem;">🎥 Tableau Live Analysis Assistant</h1>
    <p style="font-size: 0.875rem; color: #B4B4B4; font-weight: 400;">
        Real-time screen analysis • AI-powered insights • Live feedback
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar for live session controls
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0; margin: 0 0 1rem 0; border-bottom: 1px solid #565869;">
        <h3 style="font-size: 0.875rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
            🎥 Live Screen Analysis
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Session controls
    if not st.session_state.session_active:
        st.info("📹 **Start a live session** to analyze your Tableau dashboards in real-time!")

        # Analysis settings
        st.subheader("Settings")
        analysis_mode = st.selectbox(
            "Analysis Type",
            ["Dashboard Review", "Error Detection", "Performance Check", "Design Critique", "Custom"]
        )

        if analysis_mode == "Custom":
            custom_prompt = st.text_area(
                "Custom Prompt",
                placeholder="What should I focus on during analysis?",
                height=100
            )
        else:
            custom_prompt = None

        # Analysis interval
        interval = st.slider(
            "Analysis Interval (seconds)",
            min_value=5,
            max_value=60,
            value=10,
            step=5,
            help="How often to analyze the screen"
        )
        st.session_state.analysis_interval = interval

        # Screen region selection
        st.subheader("Capture Area")
        capture_full_screen = st.checkbox("Full Screen", value=True)

        if not capture_full_screen:
            st.info("Configure custom region (x, y, width, height)")
            col1, col2 = st.columns(2)
            with col1:
                region_x = st.number_input("X", value=0)
                region_y = st.number_input("Y", value=0)
            with col2:
                region_w = st.number_input("Width", value=1920)
                region_h = st.number_input("Height", value=1080)
            region = (region_x, region_y, region_w, region_h)
        else:
            region = None

        # Start button
        if st.button("🚀 Start Live Session", use_container_width=True):
            try:
                client = get_anthropic_client()

                # Create prompt based on mode
                prompts = {
                    "Dashboard Review": """
                    Review this Tableau dashboard and provide:
                    1. **Visual Clarity**: Are charts easy to understand?
                    2. **Design Issues**: Any layout or color problems?
                    3. **Best Practices**: What could be improved?
                    Keep response concise (3-4 sentences).
                    """,
                    "Error Detection": """
                    Scan this screen for errors or issues:
                    1. **Errors**: Any visible error messages?
                    2. **Data Issues**: Missing data, null values, calculation errors?
                    3. **Quick Fix**: What's the immediate solution?
                    Be specific and actionable.
                    """,
                    "Performance Check": """
                    Analyze for performance issues:
                    1. **Complex Calculations**: Any visible slow calculations?
                    2. **Data Volume**: Too many marks or rows?
                    3. **Optimization Tips**: Quick wins for speed
                    """,
                    "Design Critique": """
                    Provide design feedback:
                    1. **Visual Hierarchy**: Is the most important info prominent?
                    2. **Color Usage**: Effective use of color?
                    3. **Typography**: Text readable and well-sized?
                    4. **Whitespace**: Good balance of elements?
                    """
                }

                prompt = custom_prompt if analysis_mode == "Custom" else prompts.get(analysis_mode)

                # Create session
                session = LiveAnalysisSession(client, analysis_prompt=prompt)
                session.start_session(region=region)

                st.session_state.live_session = session
                st.session_state.session_active = True
                st.session_state.analysis_mode = analysis_mode

                logger.info(f"Live session started: {analysis_mode}")
                st.rerun()

            except Exception as e:
                st.error(f"Failed to start session: {e}")
                logger.error(f"Session start failed: {e}")

    else:
        # Session is active
        st.markdown("""
        <div class="session-active">
            <span class="live-indicator"></span>
            <strong>LIVE SESSION ACTIVE</strong>
        </div>
        """, unsafe_allow_html=True)

        st.success(f"**Mode**: {st.session_state.analysis_mode}")
        st.info(f"**Analyzing every**: {st.session_state.analysis_interval}s")

        # Manual analysis button
        if st.button("🔍 Analyze Now", use_container_width=True):
            with st.spinner("Analyzing current screen..."):
                result = st.session_state.live_session.analyze_current_screen()
                if result['success']:
                    st.session_state.last_analysis = result
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"**Live Analysis ({result['timestamp'].strftime('%H:%M:%S')})**\n\n{result['analysis']}",
                        "timestamp": result['timestamp']
                    })
                    st.rerun()
                else:
                    st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")

        # Stop button
        if st.button("⏹️ Stop Session", use_container_width=True):
            if st.session_state.live_session:
                st.session_state.live_session.stop_session()
            st.session_state.live_session = None
            st.session_state.session_active = False
            logger.info("Live session stopped")
            st.rerun()

        # Session stats
        if st.session_state.live_session:
            history = st.session_state.live_session.get_analysis_history()
            st.divider()
            st.metric("Analyses Performed", len(history))
            if history:
                total_tokens = sum(h.get('tokens_used', 0) for h in history)
                st.metric("Total Tokens Used", f"{total_tokens:,}")

    # API Key status
    st.divider()
    if os.getenv("ANTHROPIC_API_KEY"):
        st.success("✅ API Key Loaded")
    else:
        st.error("❌ API Key Missing")

# Main content area
if st.session_state.session_active:
    # Auto-analyze at intervals
    if st.session_state.last_analysis is None or \
       (datetime.now() - st.session_state.last_analysis['timestamp']).total_seconds() > st.session_state.analysis_interval:

        # Trigger auto-analysis
        with st.spinner("🔍 Auto-analyzing screen..."):
            result = st.session_state.live_session.analyze_current_screen()
            if result['success']:
                st.session_state.last_analysis = result
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**🎯 Auto-Analysis ({result['timestamp'].strftime('%H:%M:%S')})**\n\n{result['analysis']}",
                    "timestamp": result['timestamp']
                })
                st.rerun()

# Display chat messages
if st.session_state.messages:
    st.subheader("📊 Analysis Feed")

    for message in reversed(st.session_state.messages[-10:]):  # Show last 10
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"⏰ {message['timestamp'].strftime('%I:%M:%S %p')}")
else:
    # Welcome message
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem;">
        <h2 style="color: #ECECEC; font-size: 1.75rem; margin-bottom: 2rem;">
            Welcome to Live Screen Analysis! 🎥
        </h2>
        <p style="color: #B4B4B4; max-width: 600px; margin: 0 auto;">
            This feature analyzes your Tableau dashboards in real-time as you work.
            Simply start a live session from the sidebar, and I'll provide continuous
            feedback on your dashboards, detect errors, and suggest improvements.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; height: 180px;">
            <div style="font-size: 2rem; margin-bottom: 0.75rem;">🎯</div>
            <h4 style="color: #ECECEC; margin-bottom: 0.5rem;">Real-Time Analysis</h4>
            <p style="color: #B4B4B4; font-size: 0.85rem;">Get instant feedback as you build dashboards</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; height: 180px;">
            <div style="font-size: 2rem; margin-bottom: 0.75rem;">🔍</div>
            <h4 style="color: #ECECEC; margin-bottom: 0.5rem;">Error Detection</h4>
            <p style="color: #B4B4B4; font-size: 0.85rem;">Catch issues before they become problems</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #2f2f2f; border-radius: 8px; height: 180px;">
            <div style="font-size: 2rem; margin-bottom: 0.75rem;">💡</div>
            <h4 style="color: #ECECEC; margin-bottom: 0.5rem;">Smart Suggestions</h4>
            <p style="color: #B4B4B4; font-size: 0.85rem;">AI-powered design improvements</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    ### 🚀 How It Works

    1. **Start Session**: Click "Start Live Session" in the sidebar
    2. **Choose Mode**: Select what you want me to focus on (Dashboard Review, Error Detection, etc.)
    3. **Work Normally**: Open Tableau and start working on your dashboards
    4. **Get Feedback**: I'll analyze your screen automatically and provide insights
    5. **Iterate**: Use my suggestions to improve your dashboards in real-time

    💡 **Pro Tip**: Use "Analyze Now" for instant feedback on a specific view!
    """)

# Chat input for custom questions
if prompt := st.chat_input("Ask a question about your Tableau work..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = get_anthropic_client()

            # If session is active, include current screen context
            context_message = ""
            if st.session_state.session_active and st.session_state.last_analysis:
                context_message = f"\n\n**Current Screen Context:**\n{st.session_state.last_analysis['analysis']}\n\n---\n\n"

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": context_message + prompt
                }]
            )

            answer = response.content[0].text
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #7f8c8d; font-size: 0.85rem;">
    <p>Powered by Claude Sonnet 4 with Vision | Real-time screen analysis</p>
</div>
""", unsafe_allow_html=True)
