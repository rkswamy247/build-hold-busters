# Hold Busters - Streamlit Dashboard Setup Guide

This guide will help you connect your Streamlit app to Databricks and get it running.

## 📋 Prerequisites

- Python 3.8 or higher
- Access to Databricks workspace: `https://dbc-4a93b454-f17b.cloud.databricks.com/`
- SQL Warehouse running in Databricks
- Personal Access Token from Databricks

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get Databricks Credentials

You need three pieces of information:

#### 1. **Server Hostname** ✅ (Already configured!)
```
dbc-4a93b454-f17b.cloud.databricks.com
```

#### 2. **HTTP Path** (Get from Databricks)

1. Go to your Databricks workspace
2. Click **"SQL Warehouses"** in the left sidebar
3. Select your SQL Warehouse (or create one if needed)
4. Click the **"Connection details"** tab
5. Copy the **"HTTP Path"** 
   - It looks like: `/sql/1.0/warehouses/abc123def456789`

#### 3. **Personal Access Token** (Generate in Databricks)

1. In Databricks, click your **username** in the top-right corner
2. Select **"User Settings"**
3. Go to **"Access tokens"** tab
4. Click **"Generate new token"**
5. Give it a name: `Streamlit App`
6. Set expiration (optional, recommended: 90 days)
7. Click **"Generate"**
8. **Copy the token immediately** (you won't see it again!)

---

### Step 3: Configure Secrets

1. Copy the template file:
```bash
# On Windows (PowerShell)
Copy-Item .streamlit/secrets.toml.template .streamlit/secrets.toml

# On Mac/Linux
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

2. Edit `.streamlit/secrets.toml` and fill in your credentials:

```toml
[databricks]
server_hostname = "dbc-4a93b454-f17b.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/YOUR_ACTUAL_WAREHOUSE_ID"
token = "dapi_YOUR_ACTUAL_TOKEN_HERE"
default_schema = "default"
```

**⚠️ IMPORTANT:** Never commit `secrets.toml` to git! It's already in `.gitignore`.

---

### Step 4: Verify Your Data Tables

Make sure your data is loaded into Databricks tables. The app expects these tables:

- `invoices` - Main invoice data
- `invoice_lines` - Invoice line items
- `projects` - Project information

**Check your schema name:**
- If your tables are in a specific schema (e.g., `invoices_db`), note the schema name
- You can change the schema in the app's sidebar

**To upload your CSV data to Databricks:**

1. In Databricks, go to **Data** → **Create Table**
2. Upload your CSV files (`Invoices.csv`, `Invoice_Lines.csv`, `Projects.csv`)
3. Choose your schema/database
4. Create the tables

---

### Step 5: Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🔧 Troubleshooting

### Connection Issues

**Error: "Failed to connect to Databricks"**
- Verify your credentials in `.streamlit/secrets.toml`
- Make sure your SQL Warehouse is running (Start it in Databricks if stopped)
- Check that your token hasn't expired

**Error: "No data found in schema"**
- Verify the schema name in the sidebar
- Make sure tables are loaded in Databricks
- Check table names match: `invoices`, `invoice_lines`, `projects`

### Data Issues

**Tables not found:**
```sql
-- Run this in Databricks SQL to verify your tables:
SHOW TABLES IN default;

-- Or check a specific schema:
SHOW TABLES IN your_schema_name;
```

**Column mismatch:**
The app expects these columns in the `invoices` table:
- `Invoice_Id`
- `Invoice_Name`
- `Vendor__Name`
- `Invoice_Date__c`
- `Total_Amount__c`
- `sitetracker__Status__c`
- `Days_Pending_Approval__c`

If your column names differ, modify the SQL queries in `app.py`.

---

## 📊 Using the Dashboard

### Overview Tab
- View status distribution
- See top vendors
- Track invoice amounts over time

### Invoice Details Tab
- Search and filter invoices
- Export filtered data to CSV
- View detailed invoice information

### Deep Analysis Tab
- Analyze days pending approval
- View amount distributions
- State-by-state summaries
- Integration status tracking

### Custom Query Tab
- Run custom SQL queries
- Export query results
- Use sample queries as templates

---

## 🔒 Security Best Practices

1. **Never share your Personal Access Token**
2. **Never commit `secrets.toml` to version control**
3. **Set token expiration dates** (90 days recommended)
4. **Rotate tokens regularly**
5. **Use separate tokens for dev/prod environments**

---

## 📚 Additional Resources

- [Databricks SQL Connector Documentation](https://docs.databricks.com/dev-tools/python-sql-connector.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Databricks SQL Warehouses Guide](https://docs.databricks.com/sql/admin/sql-endpoints.html)

---

## 🆘 Need Help?

If you encounter issues:

1. Check the app's built-in help (click "Setup Instructions" when not connected)
2. Review the troubleshooting section above
3. Verify your Databricks SQL Warehouse is running
4. Check the Streamlit terminal output for detailed error messages

---

## 📝 Next Steps

Once connected, you can:
- Customize the dashboard layout
- Add more visualizations
- Create custom queries
- Schedule data refreshes
- Deploy to Streamlit Cloud or other hosting services

