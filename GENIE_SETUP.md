# 🧞 Databricks Genie Integration Setup

## Why Genie?

**Databricks Genie** is specifically designed for data analysis and understands your data better than generic LLMs:

### ✅ **Advantages over Foundation Model APIs:**

1. **Knows Your Data Schema**
   - Genie already understands your tables, columns, and relationships
   - No need to provide schema descriptions
   - Better at generating accurate SQL

2. **Optimized for SQL**
   - Purpose-built for database queries
   - Understands data types and constraints
   - Handles complex joins and aggregations

3. **Conversation Memory**
   - Maintains context across the conversation
   - Can reference previous queries
   - Builds on prior answers

4. **Pre-Trained on Your Data**
   - If you've already been using Genie, it knows your patterns
   - Learns from your Genie Space usage
   - Better at understanding domain-specific terms

5. **Integrated with Unity Catalog**
   - Automatically respects permissions
   - Knows what data you have access to
   - Understands catalog structure

---

## 📋 Prerequisites

### You Need:
✅ **Databricks workspace** with Genie enabled  
✅ **Genie Space** created for your data  
✅ **SQL Warehouse** configured  
✅ **Personal Access Token** (PAT)

### Check if Genie is Available:
1. Go to Databricks Console
2. Look for **AI/BI** or **Genie** in the left sidebar
3. If you see it, you're good to go!

---

## 🔍 Find Your Genie Space ID

### Step-by-Step:

1. **Go to Databricks Console**
   - Navigate to your workspace URL

2. **Open Genie**
   - Click **AI/BI** → **Genie Spaces** (or just **Genie**)

3. **Select Your Space**
   - Click on the Genie Space you want to use
   - Example: "Invoice Analysis" or "Hold Busters Analytics"

4. **Copy the Space ID from URL**
   - Look at the browser URL bar
   - Format: `https://your-workspace.cloud.databricks.com/genie/spaces/<SPACE_ID>`
   - Example: `https://dbc-abc123.cloud.databricks.com/genie/spaces/01ef9a7b8c2d3e4f`
   - The Space ID is: `01ef9a7b8c2d3e4f`

5. **Alternative: Use Genie API**
   ```python
   from databricks.sdk import WorkspaceClient
   client = WorkspaceClient()
   spaces = client.genie.list_spaces()
   for space in spaces:
       print(f"Space: {space.name}, ID: {space.id}")
   ```

---

## ⚙️ Configuration

### Update `.streamlit/secrets.toml`:

```toml
[databricks]
server_hostname = "dbc-4a93b454-f17b.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/b1bcf72a9e8b65b8"
token = "dapi1234567890abcdef"

# ADD THIS LINE - Your Genie Space ID
genie_space_id = "01ef9a7b8c2d3e4f"
```

**Where to find these:**
- **server_hostname**: Workspace URL (without https://)
- **http_path**: SQL Warehouse → Connection Details
- **token**: User Settings → Developer → Access Tokens
- **genie_space_id**: See instructions above

---

## 🚀 Run the App

### Quick Start:

```powershell
.\run_with_genie.ps1
```

### Manual Start:

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Install dependencies (if not done)
pip install streamlit databricks-sql-connector databricks-sdk

# Run app
streamlit run app_with_genie.py
```

---

## 💬 How It Works

### Architecture:

```
┌─────────────────────────────────────┐
│  Streamlit App (Your Computer)      │
│                                     │
│  User asks: "How many invoices      │
│  are on hold?"                      │
└─────────────┬───────────────────────┘
              │
              │ Databricks SDK
              ▼
┌─────────────────────────────────────┐
│  Databricks Workspace               │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Genie AI                     │  │
│  │  - Understands schema         │  │
│  │  - Generates SQL              │  │
│  │  - Executes query             │  │
│  │  - Returns results            │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Unity Catalog                │  │
│  │  hackathon.hackathon_build... │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              │
              │ Results
              ▼
┌─────────────────────────────────────┐
│  Streamlit App                      │
│  - Displays answer                  │
│  - Shows SQL (optional)             │
│  - Renders table                    │
└─────────────────────────────────────┘
```

### Conversation Flow:

1. **User asks question** in Streamlit
2. **App sends to Genie** via Databricks SDK
3. **Genie analyzes** using schema knowledge
4. **Generates SQL** specific to your data
5. **Executes query** on SQL Warehouse
6. **Returns results** with explanation
7. **App displays** in chat format

### Conversation Memory:
- Genie maintains `conversation_id`
- Follow-up questions use same conversation
- Can reference previous queries
- Click "🔄 New Conversation" to start fresh

---

## ✨ Features

### 🎯 **What You Get:**

1. **Intelligent SQL Generation**
   - Genie knows your schema
   - Generates correct table/column names
   - Handles complex queries

2. **Natural Language**
   - Ask questions like talking to a colleague
   - No SQL knowledge required
   - Genie explains what it's doing

3. **Conversation Context**
   - "Show me those invoices"
   - "What about last month?"
   - "Sort that by amount"

4. **Feedback System**
   - 👍 👎 buttons on every response
   - Tell Genie what's wrong
   - It adjusts and tries again

5. **SQL Transparency**
   - View generated SQL (hidden by default)
   - Learn from Genie's queries
   - Copy/modify SQL if needed

6. **All Standard Features**
   - Dashboard tab with metrics
   - Data Explorer tab
   - Export to JSON
   - Full Streamlit UI

---

## 🆚 Comparison: Genie vs Others

| Feature | Genie | Foundation Models | Claude (External) |
|---------|-------|-------------------|-------------------|
| **Schema Knowledge** | ✅ Built-in | ❌ Must provide | ❌ Must provide |
| **SQL Accuracy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Conversation Memory** | ✅ Native | ⚠️ Manual | ⚠️ Manual |
| **Data Security** | ✅ In Databricks | ✅ In Databricks | ❌ External |
| **Setup Complexity** | 🟢 Just Space ID | 🟡 Model selection | 🟡 API key |
| **Cost** | Databricks usage | Databricks usage | Separate billing |
| **Best For** | **Data analysis** | General AI tasks | General AI tasks |

---

## 🛠️ Troubleshooting

### Error: "Genie Space not found"

**Solution:**
1. Verify Space ID is correct
2. Check you have access to that Space
3. Ensure Genie is enabled in workspace

```bash
# Verify with Python
from databricks.sdk import WorkspaceClient
client = WorkspaceClient()
spaces = list(client.genie.list_spaces())
print(f"Found {len(spaces)} Genie Spaces")
for space in spaces:
    print(f"  - {space.name}: {space.id}")
```

### Error: "Not authorized"

**Solution:**
1. Check PAT has correct permissions
2. Verify you're added to Genie Space
3. Ensure workspace has Genie enabled

### Slow Responses

**Normal behavior:**
- First message: 5-10 seconds (Genie analyzing)
- Follow-ups: 2-5 seconds
- Complex queries: up to 30 seconds

**If consistently slow:**
1. Check SQL Warehouse is running
2. Try simpler queries first
3. Start new conversation (clears context)

### Wrong SQL Generated

**Use feedback system:**
1. Click 👎 on response
2. Explain what's wrong:
   - "The WHERE clause should filter by status='Hold'"
   - "Missing the schema prefix"
   - "Should use LEFT JOIN not INNER JOIN"
3. Genie will try again with your guidance

---

## 💡 Best Practices

### 1. **Start Conversations Clean**
- Click "🔄 New Conversation" for new topics
- Prevents confusion from mixed context

### 2. **Be Specific**
- ✅ "Show invoices on hold in California over $50k"
- ❌ "Show me some stuff"

### 3. **Use Follow-ups**
- After first query: "Sort that by date"
- Genie remembers the context

### 4. **Provide Feedback**
- Help Genie learn what you need
- Use 👎 + explanation for corrections

### 5. **Check the SQL**
- Expand "🔍 View SQL Query"
- Learn from Genie's patterns
- Verify complex queries

---

## 📊 Example Questions

### Good Questions for Genie:

```
"How many invoices are currently on hold?"
→ Genie generates: SELECT COUNT(*) FROM ... WHERE status = 'Hold'

"Which vendor has the most pending invoices?"
→ Genie groups by vendor, counts, orders

"Show me invoices over $50,000 that are on hold"
→ Genie filters by amount and status

"What's the average days pending for held invoices?"
→ Genie calculates AVG with WHERE clause

"Compare this month vs last month"
→ Genie uses date functions, CASE statements

"Break that down by state"
→ Genie remembers previous query, adds GROUP BY
```

---

## 🎓 Advanced Usage

### Multiple Genie Spaces

You can switch between Genie Spaces:

```toml
# Option 1: Default space
[databricks]
genie_space_id = "01ef9a7b..."

# Option 2: Multiple spaces (use dropdown in app)
genie_spaces = [
    {name = "Invoice Analysis", id = "01ef9a7b..."},
    {name = "Sales Data", id = "01ef8c6d..."}
]
```

### Custom Instructions

Add space-specific context in Genie Space settings:
1. Go to Genie Space
2. Click Settings
3. Add "Instructions" for Genie
4. Example: "Always include vendor name in invoice queries"

---

## 🚀 Ready to Use Genie!

### Quick Checklist:
- ☐ Genie Space ID added to `secrets.toml`
- ☐ Databricks token valid
- ☐ SQL Warehouse running
- ☐ Dependencies installed

### Run the app:
```powershell
.\run_with_genie.ps1
```

### Ask your first question:
```
"How many invoices are currently on hold?"
```

Genie will understand your data and give you accurate results! 🎉

---

## 📚 Additional Resources

- [Databricks Genie Documentation](https://docs.databricks.com/en/genie/index.html)
- [Genie API Reference](https://docs.databricks.com/api/workspace/genie)
- [Databricks SDK Python](https://databricks-sdk-py.readthedocs.io/)

---

**Need help?** Check the error messages in the app - they provide specific guidance!

