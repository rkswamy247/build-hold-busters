# Running Hold Busters Dashboard Locally

This guide explains how to run the Hold Busters Dashboard on your local machine.

## Prerequisites

- **Python 3.9 or higher**
- **Databricks credentials** (hostname, HTTP path, access token)

## Quick Start

### Option 1: Using Python Script (Recommended)

```bash
python start_local.py
```

This script will:
- ✅ Check Python version
- ✅ Verify all dependencies are installed
- ✅ Check if secrets.toml is configured
- ✅ Auto-install missing packages if needed
- ✅ Start the Streamlit app

### Option 2: Using Batch File (Windows)

```bash
run_app.bat
```

### Option 3: Manual Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure secrets (first time only)
# Copy .streamlit/secrets.toml.template to .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Databricks credentials

# 3. Start the app
streamlit run app.py
```

## Configuration

### First-Time Setup

1. **Copy the secrets template:**
   ```bash
   copy .streamlit\secrets.toml.template .streamlit\secrets.toml
   ```

2. **Edit `.streamlit/secrets.toml`** with your Databricks credentials:

   ```toml
   [databricks]
   server_hostname = "your-workspace.cloud.databricks.com"
   http_path = "/sql/1.0/warehouses/your-warehouse-id"
   token = "dapi..."
   default_schema = "your_schema.your_database"
   genie_space_id = "your-genie-space-id"  # Optional for Genie AI
   ```

3. **Get your credentials from Databricks:**
   - **Server Hostname**: Your Databricks workspace URL (without https://)
   - **HTTP Path**: Go to SQL Warehouses → Select your warehouse → Connection Details
   - **Token**: User Settings → Developer → Access Tokens → Generate New Token
   - **Genie Space ID**: (Optional) For Genie AI feature

## Accessing the Dashboard

Once started, the dashboard will be available at:

**🌐 http://localhost:8501**

The browser should open automatically. If not, manually navigate to the URL above.

## Features

### 📊 Dashboard Tabs

1. **📈 Overview** - High-level metrics and visualizations
2. **📋 Invoice Details** - Detailed invoice table with filters
3. **🔍 Deep Analysis** - Advanced analytics with drill-downs
4. **🚨 Error Analysis** - Error pattern analysis and resolution tools
5. **💾 Custom Query** - Run custom SQL queries
6. **🧞 Genie AI** - AI-powered Q&A about your data

### 🧞 Genie AI Feature

To use Genie AI:
1. Make sure `genie_space_id` is configured in `secrets.toml`
2. Go to the "🧞 Genie AI" tab
3. Ask questions in natural language, like:
   - "How many invoices are on hold?"
   - "What's the total value of approved invoices?"
   - "Show me invoices with errors"

## Troubleshooting

### Port Already in Use

If port 8501 is already in use:

```bash
# Kill the process on Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Or use a different port
streamlit run app.py --server.port 8502
```

### Missing Dependencies

If you see import errors:

```bash
pip install -r requirements.txt --upgrade
```

### Genie AI Not Working

1. Verify `genie_space_id` in `secrets.toml`
2. Check your Databricks token has Genie access
3. Ensure you're connected to the internet
4. Check the error message at the top of the Genie AI tab

### Connection Errors

If you can't connect to Databricks:
1. Verify your credentials in `secrets.toml`
2. Test your token: It should start with `dapi`
3. Check your network/VPN connection
4. Ensure the SQL Warehouse is running

## Stopping the App

Press **Ctrl+C** in the terminal to stop the Streamlit server.

## Need Help?

- Check the error messages in the terminal
- Review the configuration in `.streamlit/secrets.toml`
- Verify your Databricks credentials are correct
- Ensure all dependencies are installed

---

**Happy Analyzing! 📊✨**

