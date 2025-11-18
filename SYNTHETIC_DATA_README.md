# Synthetic Data Generator for Hold Busters Dashboard

This script generates realistic synthetic test data for all tables in the Hold Busters invoice analysis system.

## 📊 What It Generates

The script creates complete mock data for:

1. **Projects** - Base project information
2. **Budget Lines** - Budget allocations by cost category
3. **Invoices** - Invoices with different statuses:
   - Draft
   - Submitted
   - Approved
   - Paid
   - Hold (with realistic error messages)
4. **Invoice Lines** - Line item details for each invoice
5. **Integration Responses** - Mock Infinium request/response data

## 🎯 Key Features

- **Realistic Data**: Proper relationships between all tables
- **Multiple Statuses**: Creates invoices for all workflow states
- **Error Scenarios**: Includes realistic integration error messages for "Hold" status
- **JSON Responses**: Properly formatted Infinium request/response objects
- **Configurable**: Easy to adjust vendor, PO, and data volume

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas
```

### 2. Run the Generator

```python
python generate_synthetic_data.py
```

This will:
- Generate synthetic data for all tables
- Save CSV files to `synthetic_data/` directory
- Display a summary of created records

### 3. Upload to Databricks

#### Option A: Using Databricks UI (Recommended)

1. Go to your Databricks workspace
2. Navigate to **Data** > **Add Data**
3. Upload each CSV file from `synthetic_data/` folder:
   - `projects.csv` → `projects` table
   - `budget_lines.csv` → `budget_lines` table
   - `invoices.csv` → `invoices` table
   - `invoice_lines.csv` → `invoice_lines` table
   - `integration_responses.csv` → `Integration_Responses` table

#### Option B: Using Python Script

Uncomment the last line in `generate_synthetic_data.py`:

```python
# Uncomment this line:
save_to_databricks(data, 'your_schema_name')
```

Set environment variables:
```bash
export DATABRICKS_SERVER_HOSTNAME="your-workspace.cloud.databricks.com"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/your-warehouse-id"
export DATABRICKS_TOKEN="your-token"
```

Then run:
```bash
python generate_synthetic_data.py
```

## 📝 Generated Data Details

### Invoices Created

For each status (Draft, Submitted, Approved, Paid, Hold), the script creates 2 invoices:

| Status | Integration Status | Error Message | Days Pending |
|--------|-------------------|---------------|--------------|
| Draft | Not Submitted | None | 1-5 days |
| Submitted | Pending | None | 5-15 days |
| Approved | Success | None | Calculated |
| Paid | Success | None | Calculated |
| Hold | Error | Realistic error | 30-90 days |

### Sample Hold Error Messages

- "Vendor validation failed: Vendor ID not found in Infinium system"
- "Budget line not found for cost category in project"
- "PO number mismatch: Expected PO-12345, received Synthetic_PO_15"
- "Approval limit exceeded: Invoice amount requires director approval"
- "Duplicate invoice detected: Similar invoice found with same amount"

### Invoice Lines

Each invoice has 2-8 line items with:
- Random cost categories (Labor, Materials, Services)
- Quantities and unit prices
- Total amounts that sum to invoice total

### Integration Responses

For non-Draft invoices:
- **Request**: JSON with vendor, PO, amount details
- **Response**: Success or error JSON with appropriate codes
- **Operation**: CREATE, UPDATE, or VALIDATE
- **Error details**: Only for Hold status invoices

## ⚙️ Customization

Edit the configuration section in `generate_synthetic_data.py`:

```python
# Configuration
VENDOR_NAME = "Your Vendor Name"
PO_NAME = "Your_PO_Number"
PROJECT_NAME = "Your Project Name"
PROJECT_NUMBER = "PROJ-001"
COMPANY = "Your Company"

# Generate more or fewer invoices per status
data = generate_all_data(num_invoices_per_status=5)
```

## 📁 Output Files

After running, you'll find these files in `synthetic_data/`:

```
synthetic_data/
├── projects.csv (1 row)
├── budget_lines.csv (5 rows)
├── invoices.csv (10 rows - 2 per status)
├── invoice_lines.csv (20-80 rows depending on random split)
└── integration_responses.csv (8 rows - excludes Draft invoices)
```

## 🔍 Testing Your Dashboard

After uploading the data:

1. Refresh your Streamlit dashboard
2. Navigate to the **Error Analysis** tab
3. You should see:
   - 2 invoices with "Hold" status
   - Realistic error patterns grouped
   - Complete drill-down with line items
   - Integration request/response details

## 💡 Tips

- **Multiple Runs**: The script generates unique IDs each time, so you can run it multiple times to add more data
- **Testing Scenarios**: Adjust the status list to focus on specific scenarios
- **Data Volume**: Increase `num_invoices_per_status` for stress testing
- **Timestamps**: Uses current date with random historical offsets

## 🐛 Troubleshooting

### "Module not found: pandas"
```bash
pip install pandas
```

### "Databricks credentials not found"
Make sure environment variables are set:
```bash
echo $DATABRICKS_SERVER_HOSTNAME
echo $DATABRICKS_HTTP_PATH
echo $DATABRICKS_TOKEN
```

### "Table not found" when uploading
Ensure your Databricks schema and tables exist before uploading data.

## 📚 Additional Resources

- [Databricks Data Import Guide](https://docs.databricks.com/data/data-sources/index.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Hold Busters Dashboard README](README.md)

