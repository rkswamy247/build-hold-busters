# Upload Synthetic Data to Databricks Tables

This guide shows you how to add the generated CSV data to your existing Databricks tables.

## 📋 Prerequisites

- Generated CSV files in `synthetic_data/` folder
- Access to Databricks workspace: `dbc-4a93b454-f17b.cloud.databricks.com`
- Existing tables in schema: `hackathon/hackathon_build_hold_busters`
- Databricks SQL Warehouse running

---

## 🚀 Method 1: Using Databricks UI (Recommended)

### Step 1: Open Databricks SQL Editor

1. Go to your Databricks workspace: https://dbc-4a93b454-f17b.cloud.databricks.com/
2. Click **SQL Editor** in the left sidebar
3. Select your warehouse: `b1bcf72a9e8b65b8`

### Step 2: Upload Data Using SQL INSERT

For each CSV file, you'll load it as a temporary file and insert into the table.

#### **A. Upload Projects Data**

```sql
-- First, create a temporary view from the CSV
CREATE OR REPLACE TEMP VIEW temp_projects
USING CSV
OPTIONS (
  path 'dbfs:/FileStore/synthetic_data/projects.csv',
  header 'true',
  inferSchema 'true'
);

-- Insert into existing table
INSERT INTO hackathon.hackathon_build_hold_busters.projects
SELECT * FROM temp_projects;

-- Verify
SELECT COUNT(*) FROM hackathon.hackathon_build_hold_busters.projects;
```

#### **B. Upload Budget Lines Data**

```sql
CREATE OR REPLACE TEMP VIEW temp_budget_lines
USING CSV
OPTIONS (
  path 'dbfs:/FileStore/synthetic_data/budget_lines.csv',
  header 'true',
  inferSchema 'true'
);

INSERT INTO hackathon.hackathon_build_hold_busters.budget_lines
SELECT * FROM temp_budget_lines;
```

#### **C. Upload Invoices Data**

```sql
CREATE OR REPLACE TEMP VIEW temp_invoices
USING CSV
OPTIONS (
  path 'dbfs:/FileStore/synthetic_data/invoices.csv',
  header 'true',
  inferSchema 'true'
);

INSERT INTO hackathon.hackathon_build_hold_busters.invoices
SELECT * FROM temp_invoices;
```

#### **D. Upload Invoice Lines Data**

```sql
CREATE OR REPLACE TEMP VIEW temp_invoice_lines
USING CSV
OPTIONS (
  path 'dbfs:/FileStore/synthetic_data/invoice_lines.csv',
  header 'true',
  inferSchema 'true'
);

INSERT INTO hackathon.hackathon_build_hold_busters.invoice_lines
SELECT * FROM temp_invoice_lines;
```

#### **E. Upload Integration Responses Data**

```sql
CREATE OR REPLACE TEMP VIEW temp_integration_responses
USING CSV
OPTIONS (
  path 'dbfs:/FileStore/synthetic_data/integration_responses.csv',
  header 'true',
  inferSchema 'true'
);

INSERT INTO hackathon.hackathon_build_hold_busters.Integration_Responses
SELECT * FROM temp_integration_responses;
```

---

## 🚀 Method 2: Using Databricks Data Import UI

### Step 1: Upload Files to DBFS

1. Go to **Data** in the left sidebar
2. Click **Create Table**
3. Click **Upload File**
4. Select all CSV files from `synthetic_data/` folder
5. Upload to: `/FileStore/synthetic_data/`

### Step 2: Create Import Notebook

1. Go to **Workspace** in the left sidebar
2. Create a new **Python Notebook**
3. Paste this code:

```python
from pyspark.sql import SparkSession

# Initialize Spark
spark = SparkSession.builder.getOrCreate()

# Schema name
schema = "hackathon.hackathon_build_hold_busters"

# 1. Load and insert Projects
print("Loading projects...")
projects_df = spark.read.option("header", "true").csv("/FileStore/synthetic_data/projects.csv")
projects_df.write.mode("append").saveAsTable(f"{schema}.projects")
print(f"Inserted {projects_df.count()} projects")

# 2. Load and insert Budget Lines
print("Loading budget lines...")
budget_lines_df = spark.read.option("header", "true").csv("/FileStore/synthetic_data/budget_lines.csv")
budget_lines_df.write.mode("append").saveAsTable(f"{schema}.budget_lines")
print(f"Inserted {budget_lines_df.count()} budget lines")

# 3. Load and insert Invoices
print("Loading invoices...")
invoices_df = spark.read.option("header", "true").csv("/FileStore/synthetic_data/invoices.csv")
invoices_df.write.mode("append").saveAsTable(f"{schema}.invoices")
print(f"Inserted {invoices_df.count()} invoices")

# 4. Load and insert Invoice Lines
print("Loading invoice lines...")
invoice_lines_df = spark.read.option("header", "true").csv("/FileStore/synthetic_data/invoice_lines.csv")
invoice_lines_df.write.mode("append").saveAsTable(f"{schema}.invoice_lines")
print(f"Inserted {invoice_lines_df.count()} invoice lines")

# 5. Load and insert Integration Responses
print("Loading integration responses...")
integration_responses_df = spark.read.option("header", "true").csv("/FileStore/synthetic_data/integration_responses.csv")
integration_responses_df.write.mode("append").saveAsTable(f"{schema}.Integration_Responses")
print(f"Inserted {integration_responses_df.count()} integration responses")

print("\nAll data uploaded successfully!")
```

4. Run the notebook (Shift+Enter or click Run All)

---

## 🚀 Method 3: Using Python Script (From Your Local Machine)

Create a file called `upload_to_databricks.py`:

```python
"""
Upload synthetic CSV data to Databricks tables
"""

from databricks import sql
import pandas as pd
import os

# Databricks connection details
DATABRICKS_SERVER_HOSTNAME = "dbc-4a93b454-f17b.cloud.databricks.com"
DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/b1bcf72a9e8b65b8"
DATABRICKS_TOKEN = "your-token-here"  # Replace with your actual token

# Schema name
SCHEMA = "hackathon.hackathon_build_hold_busters"

# CSV files to upload
FILES_TO_UPLOAD = {
    'projects': 'synthetic_data/projects.csv',
    'budget_lines': 'synthetic_data/budget_lines.csv',
    'invoices': 'synthetic_data/invoices.csv',
    'invoice_lines': 'synthetic_data/invoice_lines.csv',
    'Integration_Responses': 'synthetic_data/integration_responses.csv'
}

def upload_csv_to_table(connection, csv_file, table_name, schema):
    """Upload CSV data to Databricks table"""
    
    print(f"\nUploading {csv_file} to {schema}.{table_name}...")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    print(f"  Read {len(df)} rows from CSV")
    
    # Get cursor
    cursor = connection.cursor()
    
    try:
        # Insert each row
        for idx, row in df.iterrows():
            # Build column names and values
            columns = ', '.join([f"`{col}`" for col in df.columns])
            
            # Handle None/NaN values
            values = []
            for val in row:
                if pd.isna(val):
                    values.append('NULL')
                elif isinstance(val, str):
                    # Escape single quotes
                    escaped_val = val.replace("'", "''")
                    values.append(f"'{escaped_val}'")
                else:
                    values.append(f"'{val}'")
            
            values_str = ', '.join(values)
            
            # Build INSERT statement
            insert_query = f"""
            INSERT INTO {schema}.{table_name} ({columns})
            VALUES ({values_str})
            """
            
            cursor.execute(insert_query)
            
            # Progress indicator
            if (idx + 1) % 10 == 0:
                print(f"  Inserted {idx + 1}/{len(df)} rows...")
        
        print(f"  SUCCESS: Inserted all {len(df)} rows")
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        raise
    finally:
        cursor.close()

def main():
    print("=" * 60)
    print("Uploading Synthetic Data to Databricks")
    print("=" * 60)
    
    # Connect to Databricks
    print("\nConnecting to Databricks...")
    connection = sql.connect(
        server_hostname=DATABRICKS_SERVER_HOSTNAME,
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_TOKEN
    )
    print("Connected successfully!")
    
    try:
        # Upload each file
        for table_name, csv_file in FILES_TO_UPLOAD.items():
            if os.path.exists(csv_file):
                upload_csv_to_table(connection, csv_file, table_name, SCHEMA)
            else:
                print(f"\nWARNING: File not found: {csv_file}")
        
        print("\n" + "=" * 60)
        print("All data uploaded successfully!")
        print("=" * 60)
        
    finally:
        connection.close()
        print("\nConnection closed")

if __name__ == "__main__":
    main()
```

**To run:**

1. Install databricks-sql-connector:
```bash
pip install databricks-sql-connector
```

2. Update the token in the script (line 11)

3. Run:
```bash
python upload_to_databricks.py
```

---

## 🚀 Method 4: Using Databricks CLI (Fastest)

### Step 1: Install and Configure Databricks CLI

```bash
# Install
pip install databricks-cli

# Configure
databricks configure --token
```

When prompted, enter:
- **Host**: `https://dbc-4a93b454-f17b.cloud.databricks.com`
- **Token**: Your personal access token

### Step 2: Upload Files to DBFS

```bash
# Upload all CSV files
databricks fs cp synthetic_data/projects.csv dbfs:/FileStore/synthetic_data/projects.csv
databricks fs cp synthetic_data/budget_lines.csv dbfs:/FileStore/synthetic_data/budget_lines.csv
databricks fs cp synthetic_data/invoices.csv dbfs:/FileStore/synthetic_data/invoices.csv
databricks fs cp synthetic_data/invoice_lines.csv dbfs:/FileStore/synthetic_data/invoice_lines.csv
databricks fs cp synthetic_data/integration_responses.csv dbfs:/FileStore/synthetic_data/integration_responses.csv
```

Or upload entire folder:
```bash
databricks fs cp -r synthetic_data/ dbfs:/FileStore/synthetic_data/
```

### Step 3: Run SQL to Load Data

Create a file `load_data.sql`:

```sql
-- Load Projects
CREATE OR REPLACE TEMP VIEW temp_projects USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/projects.csv', header 'true');
INSERT INTO hackathon.hackathon_build_hold_busters.projects SELECT * FROM temp_projects;

-- Load Budget Lines
CREATE OR REPLACE TEMP VIEW temp_budget_lines USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/budget_lines.csv', header 'true');
INSERT INTO hackathon.hackathon_build_hold_busters.budget_lines SELECT * FROM temp_budget_lines;

-- Load Invoices
CREATE OR REPLACE TEMP VIEW temp_invoices USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/invoices.csv', header 'true');
INSERT INTO hackathon.hackathon_build_hold_busters.invoices SELECT * FROM temp_invoices;

-- Load Invoice Lines
CREATE OR REPLACE TEMP VIEW temp_invoice_lines USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/invoice_lines.csv', header 'true');
INSERT INTO hackathon.hackathon_build_hold_busters.invoice_lines SELECT * FROM temp_invoice_lines;

-- Load Integration Responses
CREATE OR REPLACE TEMP VIEW temp_integration_responses USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/integration_responses.csv', header 'true');
INSERT INTO hackathon.hackathon_build_hold_busters.Integration_Responses SELECT * FROM temp_integration_responses;
```

Then run it in Databricks SQL Editor.

---

## ✅ Verify Data Upload

After uploading, verify the data:

```sql
-- Check counts
SELECT 'projects' as table_name, COUNT(*) as row_count FROM hackathon.hackathon_build_hold_busters.projects
UNION ALL
SELECT 'budget_lines', COUNT(*) FROM hackathon.hackathon_build_hold_busters.budget_lines
UNION ALL
SELECT 'invoices', COUNT(*) FROM hackathon.hackathon_build_hold_busters.invoices
UNION ALL
SELECT 'invoice_lines', COUNT(*) FROM hackathon.hackathon_build_hold_busters.invoice_lines
UNION ALL
SELECT 'Integration_Responses', COUNT(*) FROM hackathon.hackathon_build_hold_busters.Integration_Responses;

-- Check synthetic invoices
SELECT 
    Invoice_Name,
    Vendor__Name,
    sitetracker__Status__c,
    Total_Amount__c,
    Integration_Error_Message__c
FROM hackathon.hackathon_build_hold_busters.invoices
WHERE Vendor__Name = 'Synthetic Tech Partners 11'
ORDER BY Total_Amount__c DESC;
```

Expected results:
- **projects**: +1 row
- **budget_lines**: +5 rows
- **invoices**: +10 rows (2 per status)
- **invoice_lines**: +52 rows
- **Integration_Responses**: +8 rows

---

## 🔄 Refresh Dashboard

After uploading data:

1. Go to your Streamlit dashboard
2. Click the **Refresh Data** button in the sidebar
3. Or restart the app:
   ```bash
   python -m streamlit run app.py
   ```

4. Navigate to the **Error Analysis** tab
5. You should see:
   - 2 new invoices with "Hold" status
   - Vendor: "Synthetic Tech Partners 11"
   - PO: "Synthetic_PO_15"
   - Complete drill-down data

---

## 💡 Troubleshooting

### Issue: "Table not found"
- Verify schema and table names exactly match
- Check your access permissions

### Issue: "Column mismatch"
- Ensure CSV columns match table schema
- Check for extra/missing columns

### Issue: "Permission denied"
- Verify you have INSERT permissions on the tables
- Check with your Databricks admin

### Issue: "Token expired"
- Generate a new personal access token
- Update in secrets.toml or environment variables

---

## 🎯 Quick Start (Recommended Method)

**Easiest approach for most users:**

1. **Upload files to DBFS using UI**:
   - Go to Databricks > Data > Create Table > Upload File
   - Upload all 5 CSV files to `/FileStore/synthetic_data/`

2. **Run this in SQL Editor**:
   ```sql
   -- Quick load script (run each block)
   
   CREATE OR REPLACE TEMP VIEW temp_projects USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/projects.csv', header 'true');
   INSERT INTO hackathon.hackathon_build_hold_busters.projects SELECT * FROM temp_projects;
   
   CREATE OR REPLACE TEMP VIEW temp_budget_lines USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/budget_lines.csv', header 'true');
   INSERT INTO hackathon.hackathon_build_hold_busters.budget_lines SELECT * FROM temp_budget_lines;
   
   CREATE OR REPLACE TEMP VIEW temp_invoices USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/invoices.csv', header 'true');
   INSERT INTO hackathon.hackathon_build_hold_busters.invoices SELECT * FROM temp_invoices;
   
   CREATE OR REPLACE TEMP VIEW temp_invoice_lines USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/invoice_lines.csv', header 'true');
   INSERT INTO hackathon.hackathon_build_hold_busters.invoice_lines SELECT * FROM temp_invoice_lines;
   
   CREATE OR REPLACE TEMP VIEW temp_integration_responses USING CSV OPTIONS (path 'dbfs:/FileStore/synthetic_data/integration_responses.csv', header 'true');
   INSERT INTO hackathon.hackathon_build_hold_busters.Integration_Responses SELECT * FROM temp_integration_responses;
   ```

3. **Verify**:
   ```sql
   SELECT COUNT(*) FROM hackathon.hackathon_build_hold_busters.invoices WHERE Vendor__Name = 'Synthetic Tech Partners 11';
   ```

4. **Refresh your dashboard** and check Error Analysis tab!

---

## 📚 Additional Resources

- [Databricks Data Import Documentation](https://docs.databricks.com/data/data-sources/index.html)
- [Databricks SQL Reference](https://docs.databricks.com/sql/language-manual/index.html)
- [Databricks CLI Guide](https://docs.databricks.com/dev-tools/cli/index.html)

