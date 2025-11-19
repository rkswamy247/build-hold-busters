# 🚀 Quick Start: Using Genie AI in Your Dashboard

## What You Can Do Now

Your `app.py` dashboard now has **Databricks Genie AI** integrated! Users can ask questions in plain English and get instant answers about their data.

## Starting the App

```powershell
.\run_app.ps1
```

## Using Genie AI (Step by Step)

### Step 1: Navigate to Genie AI Tab
- Open the app in your browser
- Click the first tab: **"🧞 Genie AI"**

### Step 2: Ask a Question
Type natural language questions like:

```
How many invoices are currently on hold?
What are the top 5 vendors by invoice count?
Show me invoices over $10,000
Which vendors have the most invoices?
What's the total amount of invoices on hold?
```

### Step 3: View the Answer
- Genie will respond with a natural language answer
- Click **"📝 View SQL"** to see the query it generated (optional)

### Step 4: Provide Feedback (Optional)
- Click **👍** if the answer is correct
- Click **👎** if the answer needs improvement
  - Enter what should be corrected
  - Click "Submit Feedback"
  - Genie will remember this for future questions!

### Step 5: Check Genie's Memory
Look at the sidebar:
- **💾 X corrections saved**: Shows how many improvements Genie has learned
- Click **"View Saved Feedback"** to see recent corrections
- Click **"🗑️ Clear All Feedback"** to reset (if needed)

## Tab Layout

```
Tab 1: 🧞 Genie AI         ← NEW! AI-powered Q&A
Tab 2: 📈 Overview          ← Dashboard charts
Tab 3: 📋 Invoice Details   ← Table view
Tab 4: 🔍 Deep Analysis     ← Advanced analytics
Tab 5: 🚨 Error Analysis    ← Hold error patterns
Tab 6: 💾 Custom Query      ← SQL query tool
```

## Configuration Check

Make sure `.streamlit/secrets.toml` has:

```toml
[databricks]
server_hostname = "your-workspace.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/your-warehouse-id"
token = "your-databricks-token"
default_schema = "hackathon.hackathon_build_hold_busters"
genie_space_id = "YOUR_GENIE_SPACE_ID"  # ← Required!
```

**Don't have a Genie Space ID yet?**
```bash
python find_genie_space_id.py
```

## Example Questions to Try

### Business Questions
- "How many invoices are on hold?"
- "What's the average invoice amount?"
- "Which vendor has the most invoices?"

### Analytical Questions
- "Show me the top 10 vendors by total amount"
- "What percentage of invoices are on hold?"
- "Which invoices have been pending the longest?"

### Specific Queries
- "Show me invoices from ABC Company"
- "What are all the unique invoice statuses?"
- "List invoices over $50,000"

## Troubleshooting

### "Genie Space ID not configured" Error
1. Run `python find_genie_space_id.py`
2. Copy the Space ID
3. Add to `.streamlit/secrets.toml` under `[databricks]`
4. Restart the app

### Timeout Waiting for Response
- Genie has a 120-second timeout
- If queries consistently timeout, try:
  - Simplifying the question
  - Making sure your Databricks SQL Warehouse is running
  - Checking if the Genie Space is active

### Wrong Answers
1. Click **👎** (thumbs down)
2. Enter a correction like:
   - "Should use table hackathon.hackathon_build_hold_busters.invoices"
   - "The status column is called sitetracker__Status__c"
3. Submit feedback
4. Ask the question again - Genie will remember!

## Features

✅ **Natural Language Queries**: No SQL knowledge required
✅ **SQL Transparency**: View the generated query anytime
✅ **Persistent Learning**: Corrections carry across sessions
✅ **Memory Management**: View and clear feedback from sidebar
✅ **Conversation Reset**: Start fresh while keeping corrections

## Support Files

- **GENIE_INTEGRATION_SUMMARY.md**: Full technical details
- **GENIE_SETUP.md**: Detailed setup guide
- **GENIE_CHAT_MODULE.md**: Developer documentation
- **HOW_TO_VERIFY_FEEDBACK.md**: Feedback verification guide

---

**Ready to ask Genie anything?** 🧞✨

```powershell
.\run_app.ps1
```

