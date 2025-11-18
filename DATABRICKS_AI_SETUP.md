# 🚀 Databricks AI Setup Guide

## Overview

This version uses **Databricks Foundation Model APIs** instead of external AI services like Claude. All AI processing happens within your Databricks workspace.

---

## ✅ Benefits of Databricks AI

- **No External API Keys**: Uses your Databricks token
- **Data Security**: Everything stays in Databricks
- **Cost Control**: Databricks usage-based pricing
- **Model Choice**: DBRX, Llama 3, Mixtral, and more
- **Same Features**: All feedback & learning features preserved

---

## 📋 Prerequisites

### 1. Databricks Workspace Requirements

✅ **Databricks workspace** with Model Serving enabled  
✅ **SQL Warehouse** for data queries  
✅ **Personal Access Token** (PAT)  
✅ **Foundation Model API access** (usually enabled by default)

### 2. Available Models

Check what's available in your workspace:

1. Go to **Databricks Console**
2. Navigate to **Machine Learning** → **Serving**
3. Look for **Foundation Model APIs**

Common models:
- `databricks-dbrx-instruct` - Most capable Databricks model
- `databricks-meta-llama-3-70b-instruct` - Fast Llama 3
- `databricks-meta-llama-3-1-70b-instruct` - Latest Llama 3.1
- `databricks-mixtral-8x7b-instruct` - Mixtral alternative

---

## 🔧 Setup Instructions

### Step 1: Update Secrets Configuration

Edit `.streamlit/secrets.toml`:

```toml
[databricks]
server_hostname = "your-workspace.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/xxxxx"
token = "dapi1234567890abcdef"
model_endpoint = "databricks-dbrx-instruct"

# Model Options:
# - databricks-dbrx-instruct (Most capable)
# - databricks-meta-llama-3-70b-instruct (Fast & good)
# - databricks-meta-llama-3-1-70b-instruct (Latest Llama)
# - databricks-mixtral-8x7b-instruct (Alternative)
```

**Where to find these values:**

- **server_hostname**: Databricks workspace URL (without https://)
- **http_path**: SQL Warehouse → Connection Details → HTTP Path
- **token**: User Settings → Developer → Access Tokens → Generate New Token
- **model_endpoint**: See available models in step 2 above

### Step 2: Install Dependencies

```powershell
pip install -r requirements_databricks_ai.txt
```

Or install manually:
```powershell
pip install streamlit databricks-sql-connector databricks-sdk plotly pandas pyarrow
```

### Step 3: Run the App

```powershell
.\run_with_databricks_ai.ps1
```

Or manually:
```powershell
streamlit run app_with_databricks_ai.py
```

---

## 🎯 How It Works

### Architecture

```
┌─────────────────────────────────────┐
│  Streamlit App (Local/Databricks)  │
│                                     │
│  ┌───────────┐   ┌──────────────┐  │
│  │  User UI  │   │  Chat Agent  │  │
│  └─────┬─────┘   └──────┬───────┘  │
└────────┼─────────────────┼──────────┘
         │                 │
         │                 │ Databricks SDK
         │                 │
┌────────▼─────────────────▼──────────┐
│      Databricks Workspace           │
│                                      │
│  ┌────────────┐   ┌──────────────┐  │
│  │ SQL        │   │  Foundation  │  │
│  │ Warehouse  │   │  Model API   │  │
│  └────────────┘   └──────────────┘  │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Unity Catalog (Data)        │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

### Request Flow

1. **User asks question** in Streamlit
2. **App sends request** to Databricks Foundation Model API
3. **AI generates SQL** with proper schema names
4. **App executes SQL** on SQL Warehouse
5. **Results displayed** to user
6. **Feedback loop** improves future responses

---

## 🔍 Troubleshooting

### Error: "Model endpoint 'xxx' not found"

**Solution:**
1. Check available endpoints in Databricks Console
2. Update `model_endpoint` in `.streamlit/secrets.toml`
3. Try: `databricks-dbrx-instruct` or `databricks-meta-llama-3-70b-instruct`

### Error: "Not authorized to access model serving endpoint"

**Solution:**
1. Check workspace permissions
2. Verify PAT has correct scopes
3. Ensure Foundation Model APIs are enabled in workspace

### Error: "Connection failed"

**Solution:**
1. Verify `server_hostname` is correct (no https://)
2. Check `token` is valid (generate new if expired)
3. Ensure network access to Databricks

### Slow Responses

**Try:**
1. Switch to faster model (e.g., Llama 3 instead of DBRX)
2. Check SQL warehouse is running
3. Reduce conversation context (fewer messages in history)

---

## 💰 Cost Considerations

### Databricks Pricing

- **Model Serving**: Pay per token (input + output)
- **SQL Warehouse**: Charged per DBU/hour when running
- **Storage**: Minimal for chat history (in memory)

### Optimization Tips

1. **Use appropriate models**:
   - DBRX: Most capable, higher cost
   - Llama 3: Good balance
   - Mixtral: Cost-effective

2. **Limit conversation context**:
   - App uses last 10 messages (adjustable)
   - Clear chat when starting new topic

3. **Auto-pause SQL Warehouse**:
   - Configure in SQL Warehouse settings
   - Saves costs when not in use

---

## 🆚 Comparison: Databricks AI vs Claude

| Feature | Databricks AI | Claude (Anthropic) |
|---------|---------------|-------------------|
| **Data Security** | ✅ Stays in Databricks | ⚠️ External API |
| **Cost** | Databricks usage | Separate billing |
| **Setup** | Single auth (PAT) | Separate API key |
| **Models** | DBRX, Llama, Mixtral | Claude 3 family |
| **Speed** | Varies by model | Generally fast |
| **Capabilities** | Strong for SQL | Excellent reasoning |
| **Integration** | Native Databricks | External service |

---

## 🎓 Advanced Configuration

### Custom Model Endpoints

If you have custom model endpoints:

```toml
[databricks]
model_endpoint = "your-custom-endpoint"
```

### Adjusting Temperature

In `app_with_databricks_ai.py`, modify:

```python
response = client.serving_endpoints.query(
    name=model_endpoint,
    messages=messages,
    max_tokens=2000,
    temperature=0.1  # Lower = more consistent, Higher = more creative
)
```

### Changing Context Window

Modify conversation history limit:

```python
for msg in st.session_state.chat_history[-10:]:  # Change 10 to desired number
```

---

## 📚 Additional Resources

- [Databricks Foundation Model APIs Docs](https://docs.databricks.com/en/machine-learning/foundation-models/index.html)
- [Databricks SDK Python Docs](https://databricks-sdk-py.readthedocs.io/)
- [Model Serving Guide](https://docs.databricks.com/en/machine-learning/model-serving/index.html)

---

## 🎉 You're Ready!

Run the app:
```powershell
.\run_with_databricks_ai.ps1
```

Ask questions like:
- "How many invoices are on hold?"
- "Which vendor has the most pending invoices?"
- "Show me invoices over $50,000"

The AI will generate SQL, execute it, and show results—all within Databricks! 🚀

