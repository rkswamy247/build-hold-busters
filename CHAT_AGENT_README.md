# 🤖 AI Chat Agent for Hold Busters

Your Hold Busters dashboard now includes an intelligent AI assistant powered by Claude!

---

## 🚀 Quick Start

### **Step 1: Get Anthropic API Key**

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Click **API Keys** in left sidebar
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-...`)

### **Step 2: Configure API Key**

1. Open `.streamlit/secrets.toml`
2. Find the `[anthropic]` section
3. Replace `YOUR_ANTHROPIC_API_KEY_HERE` with your actual key:

```toml
[anthropic]
api_key = "sk-ant-api03-..."  # Your actual key
```

4. Save the file

### **Step 3: Install Dependencies**

```powershell
# Activate your venv
.\venv\Scripts\Activate.ps1

# Install anthropic package
pip install anthropic
```

### **Step 4: Run the App**

```powershell
# Easy way - use the script
.\run_with_chat.ps1

# OR manually
streamlit run app_with_chat.py
```

---

## 💬 What the Chat Agent Can Do

### **Answer Questions**
- "How many invoices are on hold?"
- "What's the average days pending?"
- "Which vendor has the most invoices?"

### **Generate & Execute SQL**
- "Show me all invoices over $50,000"
- "List the top 10 vendors by total amount"
- "Find invoices from California that are on hold"

### **Provide Insights**
- "What are the most common hold reasons?"
- "Which states have the longest approval times?"
- "Analyze invoice trends over time"

### **Business Analysis**
- "Summarize invoice status by state"
- "Compare vendor performance"
- "Identify bottlenecks in approval process"

---

## 🎯 Example Conversations

### **Basic Query**
```
You: How many invoices are on hold?

Claude: Let me check that for you.

[Generates and executes SQL]

Based on the current data, there are 234 invoices currently on hold, 
representing approximately 18% of all invoices in the system.
```

### **Complex Analysis**
```
You: Show me the top 5 vendors with the most held invoices over $10,000

Claude: I'll query that information for you.

[Generates SQL with filters and aggregations]

Here are the top 5 vendors:
1. Acme Corp - 42 invoices, $847,320 total
2. TechSupply Inc - 38 invoices, $612,450 total
...

These 5 vendors account for 45% of all high-value held invoices.
```

### **Suggested Questions**
The chat interface includes suggested questions like:
- How many invoices are currently on hold?
- Which vendor has the most pending invoices?
- Show me invoices over $50,000 that are on hold
- What's the average days pending for held invoices?
- Which states have the most invoice holds?

---

## 📊 Features

### **3 Main Tabs:**

1. **💬 AI Chat Assistant**
   - Natural language interface
   - Suggested questions
   - Query execution
   - Results display
   - Chat history

2. **📊 Dashboard**
   - KPI metrics
   - Quick overview
   - Summary statistics

3. **📋 Data Explorer**
   - Filter by status
   - Custom row limits
   - Download results
   - Quick data access

---

## 💡 Tips for Best Results

### **Be Specific**
❌ "Show me invoices"
✅ "Show me invoices from last month that are on hold"

### **Ask Follow-up Questions**
```
You: Which vendor has the most held invoices?
Claude: [Provides answer]

You: Show me details for that vendor
Claude: [Shows detailed breakdown]
```

### **Request Visualizations**
"Can you analyze invoice trends by month and state?"

### **Business Context**
"What's causing the backlog in California?"

---

## 🔧 Configuration

### **Schema Information**
The agent knows about your database schema:
- **invoices** table: Invoice details, amounts, status, dates
- **invoice_lines** table: Line item details
- **projects** table: Project information

### **Claude Model**
Currently using: `claude-3-5-sonnet-20241022`
- Fast responses
- Excellent SQL generation
- Great at analysis

### **Token Usage**
- Typical query: ~500-1000 tokens
- Cost: ~$0.003 per query
- Chat history: Last 10 messages kept for context

---

## 🔒 Security Notes

1. **API Key**: Never commit `secrets.toml` to git (already in `.gitignore`)
2. **Data Access**: Agent only has READ access (SELECT queries)
3. **Query Limits**: Results limited to reasonable sizes
4. **Token Management**: Only recent conversation context sent to Claude

---

## 🐛 Troubleshooting

### **"API key not configured"**
- Check `.streamlit/secrets.toml` has your actual API key
- Make sure there are no extra spaces or quotes
- Restart the app after updating

### **"Connection failed"**
- Verify Databricks SQL Warehouse is running
- Check your internet connection
- Ensure Databricks token is valid

### **"Query execution error"**
- Ask Claude to revise the query
- Check if table/column names are correct
- Verify you have SELECT permissions

### **Chat not responding**
- Check your Anthropic API key is valid
- Verify you have API credits
- Check console for error messages

---

## 💰 Pricing

**Anthropic Claude Pricing** (as of Nov 2024):
- Claude 3.5 Sonnet: $3 per million input tokens, $15 per million output tokens
- Typical conversation: ~2000 tokens total = ~$0.006 per interaction
- 100 queries ≈ $0.60

**Free Tier**: 
- Anthropic offers free credits for new accounts
- Check https://console.anthropic.com/ for current offers

---

## 🎉 Have Fun!

Your invoice analysis just got a whole lot smarter. Ask Claude anything about your data and let AI do the heavy lifting!

---

## 📞 Need Help?

- **Anthropic Docs**: https://docs.anthropic.com/
- **API Status**: https://status.anthropic.com/
- **Claude Model Info**: https://www.anthropic.com/claude

---

**Enjoy your AI-powered invoice analysis!** 🚀📊🤖

