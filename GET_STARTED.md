# 🚀 Get Started with Your Streamlit Dashboard

Congratulations! Your Streamlit app structure is ready. Now let's connect it to your Databricks workspace.

## ✅ What's Already Done

- ✅ Streamlit app created (`app.py`)
- ✅ All dependencies installed
- ✅ Workspace URL configured: `https://dbc-4a93b454-f17b.cloud.databricks.com/`

---

## 📝 Next Steps: Get Your Databricks Credentials

You need **3 pieces of information** to connect:

### 1. Server Hostname ✅ (Already Configured!)
```
dbc-4a93b454-f17b.cloud.databricks.com
```

### 2. SQL Warehouse HTTP Path ⚠️ (Need to get)

**How to find it:**
1. Go to your Databricks workspace: https://dbc-4a93b454-f17b.cloud.databricks.com/
2. Click **"SQL Warehouses"** in the left sidebar
3. Select your SQL Warehouse (or create one if needed)
   - Click "New" → "SQL Warehouse" if you don't have one
   - Use default settings, click "Create"
4. Click the **"Connection details"** tab
5. Copy the **"HTTP Path"**
   - It looks like: `/sql/1.0/warehouses/abc123def456789`

### 3. Personal Access Token ⚠️ (Need to generate)

**How to generate:**
1. In Databricks, click your **username** (top-right corner)
2. Select **"User Settings"**
3. Go to **"Access tokens"** tab (or "Developer" → "Access tokens")
4. Click **"Generate new token"**
5. Settings:
   - **Comment**: `Streamlit App`
   - **Lifetime**: 90 days (recommended)
6. Click **"Generate"**
7. **⚠️ IMPORTANT: Copy the token immediately!** You won't see it again.

---

## ⚙️ Configure Your App

### Create the secrets file:

1. Copy the template:
```powershell
Copy-Item .streamlit\secrets.toml.template .streamlit\secrets.toml
```

2. Open `.streamlit\secrets.toml` in a text editor

3. Fill in your credentials:
```toml
[databricks]
server_hostname = "dbc-4a93b454-f17b.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/YOUR_ACTUAL_HTTP_PATH"
token = "dapi_YOUR_ACTUAL_TOKEN_HERE"
default_schema = "default"
```

4. **Save the file**

---

## 📊 Prepare Your Data (If Not Already Done)

Your app expects these tables in Databricks:
- `invoices` - Main invoice data
- `invoice_lines` - Invoice line items  
- `projects` - Project information

**To upload your CSV files to Databricks:**

1. In Databricks, click **"Data"** in the left sidebar
2. Select **"Create Table"**
3. Click **"Upload File"**
4. Upload your CSV files:
   - `Invoices.csv`
   - `Invoice_Lines.csv`
   - `Projects.csv`
5. Choose your schema/database (e.g., `default`)
6. Follow the prompts to create the tables

**Or use Databricks SQL:**

```sql
-- Create and load invoices table
CREATE TABLE IF NOT EXISTS default.invoices
USING CSV
OPTIONS (path 'dbfs:/FileStore/Invoices.csv', header 'true', inferSchema 'true');

-- Create and load invoice_lines table
CREATE TABLE IF NOT EXISTS default.invoice_lines
USING CSV
OPTIONS (path 'dbfs:/FileStore/Invoice_Lines.csv', header 'true', inferSchema 'true');

-- Create and load projects table
CREATE TABLE IF NOT EXISTS default.projects
USING CSV
OPTIONS (path 'dbfs:/FileStore/Projects.csv', header 'true', inferSchema 'true');
```

---

## 🏃 Run the App

Once you've configured your credentials:

```powershell
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🔍 Testing Your Connection

When you first run the app:

1. **If connected successfully:** You'll see "✅ Connected to Databricks!" and your dashboard will load
2. **If connection fails:** The app will show helpful error messages and setup instructions
3. **If tables not found:** Check the schema name in the sidebar and verify your tables exist

---

## 🛠️ Troubleshooting

### "Failed to connect to Databricks"
- ✅ Check your credentials in `.streamlit/secrets.toml`
- ✅ Ensure your SQL Warehouse is **running** (not stopped)
- ✅ Verify your token hasn't expired

### "No data found in schema"
- ✅ Verify the schema name in the app sidebar
- ✅ Check that tables exist: Run `SHOW TABLES IN your_schema;` in Databricks SQL
- ✅ Ensure table names match: `invoices`, `invoice_lines`, `projects`

### Scripts not on PATH
- This is just a warning - the app will still work
- To fix (optional): Add `C:\Users\krr351\AppData\Roaming\Python\Python314\Scripts` to your PATH

---

## 📚 What Your App Can Do

### 📈 Overview Tab
- View invoice status distribution (pie chart)
- See top 10 vendors by amount
- Track invoice amounts over time

### 📋 Invoice Details Tab
- Search and filter invoices
- View detailed invoice information
- Export filtered data to CSV

### 🔍 Deep Analysis Tab
- Analyze days pending approval distribution
- View amount distributions by status
- State-by-state summaries
- Integration status tracking

### 💾 Custom Query Tab
- Run custom SQL queries against your tables
- Export query results to CSV
- Use sample queries as templates

---

## 🔒 Security Reminders

- ⚠️ **NEVER commit** `.streamlit/secrets.toml` to git (it's already in `.gitignore`)
- ⚠️ **NEVER share** your Personal Access Token
- ✅ Set token expiration dates (90 days recommended)
- ✅ Rotate tokens regularly
- ✅ Use separate tokens for dev/prod

---

## 🎯 Quick Command Reference

```powershell
# Run the app
streamlit run app.py

# Stop the app
# Press Ctrl+C in the terminal

# Update packages (if needed)
pip install --upgrade streamlit databricks-sql-connector plotly

# Check installed packages
pip list | Select-String "streamlit|databricks|plotly"
```

---

## 📞 Need Help?

1. Check the app's built-in help (expand "Setup Instructions" when not connected)
2. Review `README_SETUP.md` for detailed troubleshooting
3. Verify your SQL Warehouse is running in Databricks
4. Check the terminal output for detailed error messages

---

**Ready to go!** Once you have your HTTP path and token, update `.streamlit/secrets.toml` and run `streamlit run app.py` 🚀

