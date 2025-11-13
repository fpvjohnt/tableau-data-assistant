# 🚀 Quick Reference - Live Tableau Analysis

## Start the Enhanced App
```bash
streamlit run scripts/tableau_chatbot_enhanced.py
```
**URL**: http://localhost:8503

---

## 🎯 Quick Workflow

### 1. Start Session (30 seconds)
```
Sidebar → "🚀 Start Live Session"
   ↓
Choose mode: Dashboard Review / Error Detection / Performance Check
   ↓
Set interval: 10-60 seconds
   ↓
(Optional) Select specific Tableau window from picker dialog
   ↓
Click "Start"
   ↓
Red pulsing border appears around capture area ✨
```

### 2. Work Normally
```
Open Tableau → Work on your dashboard
   ↓
AI watches and analyzes automatically
   ↓
Feedback appears in chat every N seconds
   ↓
Click "🔍 Analyze Now" for instant feedback
```

### 3. Get Expert Help
```
See an error? → AI identifies it with exact fix
Need design advice? → AI suggests improvements
Want to optimize? → AI spots performance issues
```

---

## 🎨 Visual Indicators

### Red Pulsing Border
- ✅ Session is active
- ✅ Shows exactly what's being captured
- ✅ Confirms right window selected

### No Border
- ❌ Session not started yet
- ❌ Need to start session

---

## 💡 Analysis Modes

| Mode | Best For | Output Example |
|------|----------|----------------|
| **Dashboard Review** | Building dashboards | "Good layout. Consider larger title font." |
| **Error Detection** | Debugging | "Calc error in Sheet 1: Use ATTR([Field])" |
| **Performance Check** | Slow dashboards | "47k marks detected. Add TOP N filter." |
| **Design Critique** | Final polish | "Color scheme good. Increase padding 8px." |
| **Custom** | Specific needs | Your custom prompt |

---

## ⚡ Keyboard Shortcuts (In Chat)

Common questions to ask:
- `"How do I fix that error?"`
- `"Explain that calculation issue"`
- `"What's the priority for fixing?"`
- `"Show me the exact formula"`
- `"Is this ready to present?"`

---

## 🧠 Tableau Expertise Included

The AI knows:
- ✅ **All Tableau features** (worksheets, dashboards, stories, parameters, LODs)
- ✅ **Calculation syntax** (FIXED, INCLUDE, EXCLUDE, table calcs)
- ✅ **Common errors** ("Cannot mix aggregate", nulls, division by zero)
- ✅ **UI elements** (containers, marks card, shelves, data pane)
- ✅ **Best practices** (golden ratio, color accessibility, chart selection)
- ✅ **Performance** (mark count, extract vs live, filter efficiency)

---

## 🎯 Pro Tips

### Get Better Results:
1. **Full-screen Tableau** for clearer capture
2. **Choose specific window** instead of full screen
3. **15-30 second interval** = good balance
4. **Ask follow-ups** for deeper explanations
5. **Manual analyze** after making changes

### Save API Costs:
1. **Longer intervals** (30-60s)
2. **Manual analysis** only when needed
3. **Stop session** when not actively working

### Visual Feedback:
1. **Border pulsing** = Session active ✓
2. **Border disappeared** = Session stopped
3. **Dialog appears** = Choose window

---

## 🔧 Troubleshooting

### "No Tableau windows found"
→ Open Tableau first, then start session

### "Permission denied" (screen recording)
→ System Settings → Privacy → Screen Recording → Allow Terminal/Python

### Border not showing
→ Check if window selection succeeded
→ Try restarting session

### Analysis seems wrong
→ Ensure Tableau window is selected
→ Check if correct window has focus
→ Try manual analyze

---

## 📊 Example Session

```bash
# 1. Open Tableau Desktop
# 2. Open your workbook  
# 3. Open this app: http://localhost:8503
# 4. Click "Start Live Session"
# 5. Dialog shows: "Tableau - Superstore Dashboard (1920x1080)"
# 6. Click "Select Window"
# 7. Red border appears around Tableau! ✨
# 8. Set mode: "Dashboard Review"
# 9. Set interval: 15 seconds
# 10. Click "Start"
# 11. Build your dashboard...
# 12. Every 15s: Get AI feedback in chat
# 13. Click "Analyze Now" to verify changes
# 14. Ask questions: "How do I fix that?"
# 15. Click "Stop Session" when done
```

---

## 🎉 What You Get

### Instead of Screenshots:
❌ Manual capture → ✅ Automatic capture
❌ Upload one-by-one → ✅ Continuous monitoring  
❌ Generic feedback → ✅ Tableau-specific expertise
❌ Interrupt workflow → ✅ Seamless integration
❌ Guessing capture area → ✅ Visual red border

### Real-Time Intelligence:
✅ Sees your work evolve
✅ Provides progressive feedback
✅ Knows Tableau terminology
✅ Gives exact formula fixes
✅ References specific UI elements
✅ Understands your workflow

---

## 📞 Quick Help

**App not working?**
```bash
# Check logs
tail -f logs/app.log

# Restart app
# (Terminal: Ctrl+C, then relaunch)
```

**Want to stop?**
- Click "⏹️ Stop Session" in sidebar
- Or just close browser tab

**Need more help?**
- Read: `LIVE_SCREEN_ANALYSIS_GUIDE.md`
- Read: `FINAL_ENHANCEMENTS_SUMMARY.md`

---

**Your Tableau dashboards just got an AI coach!** 🚀📊✨

Happy analyzing!
