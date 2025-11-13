# 🎥 Live Screen Analysis Feature - User Guide

## Overview

Your Tableau Data Assistant now features **Live Screen Analysis** - a revolutionary way to get real-time AI feedback on your Tableau dashboards as you work!

Instead of uploading screenshots, the app now **continuously monitors your screen** and provides intelligent, context-aware suggestions in real-time.

---

## 🚀 Quick Start

### 1. Launch the Enhanced App

```bash
cd /Users/nrjs/Desktop/Tableau_Project
source venv/bin/activate
streamlit run scripts/tableau_chatbot_enhanced.py
```

**Access at**: http://localhost:8503

### 2. Start a Live Session

1. Click **"🚀 Start Live Session"** in the sidebar
2. Choose your **Analysis Type**:
   - **Dashboard Review**: General design and clarity feedback
   - **Error Detection**: Scans for errors and data issues
   - **Performance Check**: Identifies performance bottlenecks
   - **Design Critique**: Detailed visual design feedback
   - **Custom**: Write your own analysis prompt

3. Configure **settings**:
   - Analysis Interval (5-60 seconds)
   - Screen region (full screen or custom area)

4. Click **Start** and the AI will begin monitoring!

---

## 📊 How It Works

### Real-Time Analysis Loop

```
┌─────────────────────────────────────────┐
│  1. Capture Screen (every N seconds)   │
│          ↓                              │
│  2. Send to Claude Vision API           │
│          ↓                              │
│  3. Receive AI Analysis                 │
│          ↓                              │
│  4. Display in Chat Feed                │
│          ↓                              │
│  5. Repeat...                           │
└─────────────────────────────────────────┘
```

### What Gets Analyzed

- **Visual Design**: Color schemes, layout, typography
- **Data Issues**: Errors, null values, calculation problems
- **Best Practices**: Tableau-specific recommendations
- **Performance**: Slow calculations, too many marks
- **User Experience**: Navigation, interactivity, clarity

---

## 🎯 Analysis Modes Explained

### 🎨 Dashboard Review
Perfect for: General feedback while building dashboards

**Focus Areas:**
- Chart type appropriateness
- Visual clarity
- Layout organization
- Color effectiveness

**Example Output:**
```
✅ Clear hierarchy with sales trending chart prominent
⚠️ Consider using horizontal bar chart instead of vertical for better label readability
💡 Add filters for time period selection
```

### 🔍 Error Detection
Perfect for: Debugging and quality assurance

**Focus Areas:**
- Error messages
- Null/missing data
- Calculation errors
- Data type mismatches

**Example Output:**
```
🚨 Calculation error visible: "Cannot mix aggregate and non-aggregate"
📍 Location: Sales by Region chart
✅ Quick fix: Wrap Region field in ATTR() function
```

### ⚡ Performance Check
Perfect for: Optimizing slow dashboards

**Focus Areas:**
- Complex calculations
- Large data volumes
- Rendering performance
- Filter efficiency

**Example Output:**
```
⚠️ Table calculation appears complex (nested LOD)
💡 Consider pre-aggregating in data source
📊 Vizual has 50K+ marks - recommend filtering
```

### 🎨 Design Critique
Perfect for: Polishing for presentation

**Focus Areas:**
- Visual hierarchy
- Color psychology
- Typography
- Whitespace and balance

**Example Output:**
```
✨ Good use of color - blue for KPIs stands out
⚠️ Text size too small in footer (appears 8pt)
💡 Add more padding between charts
🎯 Consider larger font for main title
```

---

## 💡 Pro Tips

### 1. Optimal Analysis Intervals

- **Fast feedback** (5-10s): Best for active development
- **Moderate** (15-30s): Good balance of feedback vs. API usage
- **Conservative** (45-60s): Minimal API calls, occasional check-ins

### 2. Manual Analysis

Click **"🔍 Analyze Now"** for instant feedback on demand:
- Just made a change? Get immediate feedback
- Want a second opinion? Click analyze
- Before presenting? Run one final check

### 3. Screen Region Optimization

**Full Screen** (Default):
- ✅ Captures everything
- ❌ May include unnecessary UI elements

**Custom Region**:
- ✅ Focus on specific dashboard area
- ✅ Excludes toolbars and menus
- ✅ Faster processing

**How to find your region coordinates:**
1. Take a screenshot
2. Open in Preview (Mac) or Paint (Windows)
3. Note the pixel coordinates
4. Enter in the app

### 4. Ask Follow-Up Questions

The chat input is context-aware! Ask questions like:
- "How can I fix that calculation error you mentioned?"
- "What color scheme would you suggest?"
- "Explain why that chart type is better"

---

## 🔧 Troubleshooting

### "No frame available"
**Problem**: Screen capture isn't working
**Solutions:**
1. Grant screen recording permissions (System Settings > Privacy > Screen Recording)
2. Try restarting the session
3. Check if another app is using screen capture

### Analysis seems slow
**Problem**: Long delays between analyses
**Solutions:**
1. Increase analysis interval
2. Use custom region (smaller area = faster)
3. Check internet connection (API calls)

### Getting irrelevant feedback
**Problem**: AI analyzing wrong content
**Solutions:**
1. Use Custom Region to focus on Tableau window only
2. Switch to "Custom" mode with specific instructions
3. Make sure Tableau is the active window

### High API usage
**Problem**: Too many Claude API calls
**Solutions:**
1. Increase analysis interval (30-60s)
2. Use "Analyze Now" instead of auto-analysis
3. Stop session when not actively working

---

## 📈 Best Practices

### For Dashboard Development

```
1. Start session with "Dashboard Review" mode
2. Set interval to 15 seconds
3. Build your dashboard normally
4. Review AI suggestions in the feed
5. Implement changes
6. Click "Analyze Now" to verify improvements
```

### For Debugging

```
1. Start session with "Error Detection" mode
2. Set interval to 10 seconds (fast feedback)
3. Reproduce the issue on screen
4. Wait for AI to identify the problem
5. Ask follow-up questions in chat
6. Verify fix with manual analysis
```

### For Final Polish

```
1. Start session with "Design Critique" mode
2. Set interval to 30 seconds
3. Slowly navigate through dashboard
4. Collect all design suggestions
5. Implement changes in batch
6. Final manual analysis before presenting
```

---

## 🎓 Advanced Usage

### Custom Prompts

Create highly specific analysis modes:

**Example 1: Color Accessibility**
```
Check this dashboard for color blindness accessibility.
Identify any red-green combinations that would be
problematic. Suggest alternative color palettes.
```

**Example 2: Executive Dashboard**
```
This is an executive dashboard for C-level.
Check if KPIs are immediately clear, numbers are
large enough, and insights are obvious at a glance.
```

**Example 3: Data Quality**
```
Focus on data quality issues: missing values,
suspicious outliers, calculation errors, and
data freshness indicators.
```

### Workflow Integration

**Morning Dashboard Review:**
```
1. Open Tableau
2. Start "Dashboard Review" session (30s interval)
3. Go through each dashboard in workbook
4. Take notes of AI suggestions
5. Stop session
6. Implement improvements
```

**Pre-Presentation Check:**
```
1. Open final dashboard
2. Start "Design Critique" session
3. Manual analyze each sheet
4. Fix any issues found
5. Final manual analysis
6. Present with confidence!
```

---

## 📊 Session Statistics

Track your usage:
- **Analyses Performed**: Total number of screen captures analyzed
- **Tokens Used**: API usage (for cost tracking)
- **Session Duration**: How long you've been analyzing

---

## 🔒 Privacy & Security

### What's Captured
- Only the screen region you specify
- Screenshots are analyzed in real-time
- **Not permanently stored** (unless you save the chat)

### Data Security
- All communication encrypted (HTTPS)
- API key securely stored
- Images sent to Claude API, not third parties
- No data retention after session ends

### Screen Recording Permissions
- macOS requires explicit permission
- Grant in: System Settings > Privacy & Security > Screen Recording
- Permission only needed once

---

## 💰 API Cost Considerations

### Token Usage
- Each analysis: ~1,000-2,000 tokens
- Cost: ~$0.003-$0.006 per analysis (Claude Sonnet 4)

### Optimization Tips
1. **Longer intervals** = fewer API calls
2. **Smaller regions** = slightly fewer tokens
3. **Manual analysis** = full control over costs
4. **Custom prompts** (shorter) = fewer tokens

### Sample Costs
- 1 hour session @ 15s interval = ~240 analyses = $0.72-$1.44
- 1 hour session @ 60s interval = ~60 analyses = $0.18-$0.36
- 10 manual analyses = $0.03-$0.06

**Totally worth it for the productivity boost!** 🚀

---

## 🆚 vs. Screenshot Upload (Old Method)

| Feature | Live Screen Analysis | Screenshot Upload |
|---------|---------------------|-------------------|
| **Speed** | Real-time, continuous | Manual, one-at-a-time |
| **Workflow** | Seamless, work normally | Interrupt to capture |
| **Context** | Automatic context awareness | Must explain each time |
| **Coverage** | Continuous monitoring | Spot checks only |
| **Convenience** | Set & forget | Constant manual work |
| **Use Case** | Active development | One-off reviews |

---

## 🎉 What Makes This Powerful

### 1. Continuous Learning
The AI sees your work **evolve in real-time**, understanding:
- Your design process
- What you're trying to achieve
- Iterative improvements you make

### 2. Proactive Insights
Instead of asking "What's wrong?", the AI **tells you** before you even realize there's an issue!

### 3. Natural Workflow
No more:
- ❌ Taking screenshots
- ❌ Uploading files
- ❌ Waiting for analysis
- ❌ Context switching

Just work naturally and get intelligent feedback! ✨

---

## 📝 Quick Reference Commands

In the chat, try these:
- `"Explain the last issue you found"`
- `"How urgent is that design problem?"`
- `"What should I prioritize fixing?"`
- `"Show me an example of that best practice"`
- `"Is this dashboard ready to present?"`

---

## 🚀 Next Steps

1. **Try it now!** Start a session and open Tableau
2. **Experiment** with different analysis modes
3. **Find your workflow** - what interval works best?
4. **Share feedback** - how can we make it better?

---

## 📞 Support

**Issues?** Check the logs:
```bash
tail -f logs/app.log
```

**Questions?** Ask in the chat - the AI understands questions about itself!

---

**Happy analyzing!** 🎊

Your Tableau dashboards are about to get a whole lot better with real-time AI coaching! 🚀📊✨
