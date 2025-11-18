# 🚀 Deploy Streamlit App to Databricks

This guide shows you how to deploy your Hold Busters Streamlit app to Databricks using **Databricks Apps**.

---

## 📋 Prerequisites

- ✅ Databricks workspace (you have: `dbc-4a93b454-f17b.cloud.databricks.com`)
- ✅ SQL Warehouse running
- ✅ Tables loaded in schema: `hackathon.hackathon_build_hold_busters`
- ✅ Databricks workspace admin or app deployment permissions

---

## 🎯 Deployment Options

### **Option 1: Databricks Apps (Recommended)** ⭐
Best for production deployments - Fully managed and scalable

### **Option 2: Databricks Notebooks**
Best for quick prototyping and sharing with team

---

## 🚀 Option 1: Deploy as Databricks App

Databricks Apps allows you to deploy Streamlit apps directly in your Databricks workspace.

### Step 1: Prepare Your App Files

1. Create a new file `app_databricks.py` (already created for you!)
2. Create a `requirements.txt` with dependencies
3. Optional: Create `databricks_app.yml` for configuration

### Step 2: Create the Databricks App Configuration

Create a file named `databricks_app.yml`:

```yaml
# Databricks App Configuration
name: hold-busters-dashboard
display_name: "Hold Busters - Invoice Analysis"
description: "Interactive dashboard for analyzing invoice holds and approvals"

# Compute configuration
compute:
  size: small  # Options: small, medium, large
  
# SQL Warehouse connection
sql_warehouse:
  id: "b1bcf72a9e8b65b8"  # Your warehouse ID

# Environment variables
env:
  DATABRICKS_SERVER_HOSTNAME: "dbc-4a93b454-f17b.cloud.databricks.com"
  DATABRICKS_HTTP_PATH: "/sql/1.0/warehouses/b1bcf72a9e8b65b8"
  
# Entry point
entrypoint: "streamlit run app_databricks.py"
```

### Step 3: Deploy Using Databricks CLI

#### Install Databricks CLI

```bash
pip install databricks-cli
```

#### Configure Authentication

```bash
databricks configure --token
```

Enter:
- **Host**: `https://dbc-4a93b454-f17b.cloud.databricks.com`
- **Token**: Your personal access token

#### Create the App

```bash
# Navigate to your project directory
cd C:\Users\krr351\code\hackaithon\build-hold-busters

# Create the app
databricks apps create hold-busters \
  --description "Invoice Hold Analysis Dashboard" \
  --source-code-path .
```

#### Deploy the App

```bash
databricks apps deploy hold-busters
```

### Step 4: Access Your App

Once deployed, you'll get a URL like:
```
https://dbc-4a93b454-f17b.cloud.databricks.com/apps/hold-busters
```

---

## 🚀 Option 2: Deploy in Databricks Notebook

This is a quicker method for sharing with your team.

### Step 1: Create a New Databricks Notebook

1. Go to your Databricks workspace
2. Click **Workspace** → **Create** → **Notebook**
3. Name it: `Hold Busters Dashboard`
4. Choose Python as the language

### Step 2: Install Dependencies (Cell 1)

```python
%pip install streamlit plotly databricks-sql-connector
dbutils.library.restartPython()
```

### Step 3: Create the App File (Cell 2)

```python
# Write the Streamlit app to a file
dbutils.fs.put("/tmp/hold_busters_app.py", """
import streamlit as st
import pandas as pd
from pyspark.sql import SparkSession
import plotly.express as px

# Your app code here...
# (Copy the content from app_databricks.py)
""", overwrite=True)
```

### Step 4: Run Streamlit (Cell 3)

```python
# Run Streamlit in the notebook
import subprocess
import os

os.environ['DATABRICKS_HOST'] = 'dbc-4a93b454-f17b.cloud.databricks.com'
os.environ['DATABRICKS_TOKEN'] = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# Run streamlit
!streamlit run /dbfs/tmp/hold_busters_app.py --server.port 8501 --server.enableCORS false
```

---

## 🚀 Option 3: Deploy Using Databricks Web Terminal

If you have access to Databricks Web Terminal:

### Step 1: Upload Your Files

1. In Databricks, go to **Workspace**
2. Create a new folder: `apps/hold-busters`
3. Upload these files:
   - `app_databricks.py`
   - `requirements.txt`

### Step 2: Open Web Terminal

1. Click the **Terminal** button in Databricks
2. Navigate to your app folder:
   ```bash
   cd /Workspace/apps/hold-busters
   ```

### Step 3: Install and Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app_databricks.py --server.port 8501
```

### Step 4: Access via Proxy

Databricks will provide a proxy URL to access your running Streamlit app.

---

## 📁 Required Files for Deployment

### 1. `app_databricks.py`
Already created! This is the Databricks-optimized version that:
- Uses environment variables for authentication
- Works with Databricks SQL Warehouses
- Optimized for Databricks Apps environment

### 2. `requirements.txt`
```txt
streamlit>=1.28.0
databricks-sql-connector>=3.0.0
plotly>=5.18.0
pandas>=2.0.0
```

### 3. `databricks_app.yml` (Optional but recommended)
```yaml
name: hold-busters-dashboard
display_name: "Hold Busters Dashboard"
entrypoint: "streamlit run app_databricks.py"
compute:
  size: small
```

---

## 🔐 Security Considerations

### Authentication

In Databricks Apps:
- ✅ Authentication is handled automatically
- ✅ Uses the user's Databricks credentials
- ✅ No need to store tokens in the app

### Data Access

- ✅ Users can only see data they have permissions to access
- ✅ SQL Warehouse permissions apply
- ✅ Schema and table permissions are enforced

---

## 🎯 Best Practices

### 1. Use Delta Tables
Convert your CSV data to Delta format for better performance:

```sql
-- Create Delta tables from CSVs
CREATE TABLE hackathon.hackathon_build_hold_busters.invoices
USING DELTA
AS SELECT * FROM csv.`/FileStore/Invoices.csv`;

CREATE TABLE hackathon.hackathon_build_hold_busters.invoice_lines
USING DELTA
AS SELECT * FROM csv.`/FileStore/Invoice_Lines.csv`;

CREATE TABLE hackathon.hackathon_build_hold_busters.projects
USING DELTA
AS SELECT * FROM csv.`/FileStore/Projects.csv`;
```

### 2. Optimize Queries
Add caching and indexing:

```sql
-- Optimize tables
OPTIMIZE hackathon.hackathon_build_hold_busters.invoices;
OPTIMIZE hackathon.hackathon_build_hold_busters.invoice_lines;
OPTIMIZE hackathon.hackathon_build_hold_busters.projects;
```

### 3. Set Up Monitoring
Enable logging and monitoring in Databricks Apps to track:
- App usage
- Query performance
- Error rates

---

## 🐛 Troubleshooting

### Issue: "App fails to start"
**Solution**: Check the logs in Databricks Apps → Your App → Logs

### Issue: "Cannot connect to SQL Warehouse"
**Solution**: 
- Ensure SQL Warehouse is running
- Verify warehouse ID in configuration
- Check user has access permissions

### Issue: "No data found"
**Solution**:
- Verify schema name: `hackathon.hackathon_build_hold_busters`
- Check tables exist: `SHOW TABLES IN hackathon.hackathon_build_hold_busters`
- Ensure user has SELECT permissions

### Issue: "Import errors"
**Solution**:
- Check `requirements.txt` has all dependencies
- Try rebuilding the app environment

---

## 📚 Quick Commands Reference

```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# Create app
databricks apps create hold-busters --source-code-path .

# Deploy app
databricks apps deploy hold-busters

# View app status
databricks apps get hold-busters

# View app logs
databricks apps logs hold-busters

# Update app
databricks apps update hold-busters

# Delete app
databricks apps delete hold-busters
```

---

## 🎉 Next Steps

After deploying:

1. **Share the URL** with your team
2. **Set up permissions** in Databricks
3. **Monitor usage** via Databricks monitoring
4. **Optimize performance** based on usage patterns
5. **Add more features** as needed

---

## 📞 Need Help?

- **Databricks Apps Documentation**: [Databricks Apps Guide](https://docs.databricks.com/apps/index.html)
- **Streamlit on Databricks**: [Streamlit Integration](https://docs.databricks.com/integrations/streamlit.html)
- **Your workspace**: https://dbc-4a93b454-f17b.cloud.databricks.com/

---

## 🎯 Quick Start Commands

For the fastest deployment:

```powershell
# 1. Install Databricks CLI
pip install databricks-cli

# 2. Configure (enter your workspace URL and token when prompted)
databricks configure --token

# 3. Deploy
cd C:\Users\krr351\code\hackaithon\build-hold-busters
databricks apps create hold-busters --source-code-path .
databricks apps deploy hold-busters

# 4. Access your app at:
# https://dbc-4a93b454-f17b.cloud.databricks.com/apps/hold-busters
```

That's it! Your app is now running in Databricks and accessible to your team! 🚀
