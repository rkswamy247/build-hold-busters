# Send to Linus Feature

## Overview
The "Send to Linus" feature allows users to automatically request PO supplemental amount approvals for invoices that exceed available PO balance.

## When Does This Feature Appear?
The "Send to Linus" tab appears **only** for invoices with the error pattern:
> "The invoice amount is greater than the amount available on the PO"

## How It Works

### 1. Navigate to Error Analysis Dashboard
- Open the Hold Busters dashboard
- Go to the **"🚨 Error Analysis"** tab
- Find the error pattern for PO amount issues

### 2. Select an Invoice
- Click to expand the error pattern
- Select an invoice from the dropdown
- You'll see **3 tabs** (instead of 2):
  - 📋 Invoice Line Items
  - 🔗 Integration Response
  - **📨 Send to Linus** *(NEW)*

### 3. Review Calculated Fields
The "Send to Linus" tab displays:

| Field | Description | Calculation |
|-------|-------------|-------------|
| **Months into Year** | Remaining months in current year (1 decimal) | `(Days until Dec 31) / 30` |
| **Total Approved PO** | Original PO amount | From `Purchase_Orders.PO_Amount` |
| **Invoiced YTD** | All invoices for this PO | Sum of `Total_Amount__c` for all invoices with same `PO_Name` |
| **Remaining Balance** | Available PO balance | `Total Approved PO - Sum(Paid & Committed invoices)` |
| **Total Pending** | Pending invoice amounts | Sum of invoices with status: Draft, Submitted, Approved, Hold |
| **Expected Additional** | Anticipated extra costs | `10% of Total Pending` |
| **Supplemental Amount** | Amount needed for PO supplement | `(Total Pending + Expected Additional) - Remaining Balance` |

### 4. Send Request to Linus
- Review the calculated supplemental amount
- Click **"📨 Send to Linus"** button
- A success message appears with the Request ID
- Data is inserted into `Linus_Requests` table

## Database Setup

### Step 1: Create the Linus_Requests Table
Execute the following SQL in Databricks:

```sql
-- Run this in Databricks SQL Editor
CREATE TABLE IF NOT EXISTS hackathon.hackathon_build_hold_busters.Linus_Requests (
    Request_Id STRING NOT NULL,
    Invoice_Id STRING NOT NULL,
    Invoice_Name STRING,
    PO_Name STRING,
    Vendor_Name STRING,
    Invoice_Amount DOUBLE,
    Months_Into_Year DOUBLE,
    Total_Approved_PO DOUBLE,
    Invoiced_Year_To_Date DOUBLE,
    Remaining_Balance DOUBLE,
    Total_Pending DOUBLE,
    Expected_Additional DOUBLE,
    Supplemental_Amount DOUBLE,
    Request_Date TIMESTAMP,
    Created_By STRING,
    Status STRING DEFAULT 'Pending',
    LastModifiedDate TIMESTAMP
)
USING DELTA
COMMENT 'Table to store Linus requests for PO supplemental amount approvals';
```

**OR** simply run the provided SQL file:
```bash
# In Databricks SQL Editor, copy and paste contents of:
create_linus_requests_table.sql
```

### Step 2: Verify Purchase_Orders Table
Ensure your `Purchase_Orders` table has these columns:
- `PO_Name` (STRING)
- `PO_Amount` (DOUBLE)
- `Vendor__Name` (STRING)
- `Status__c` (STRING)

### Step 3: Verify Invoices Have PO_Name
Ensure your `invoices` table includes the `PO_Name` column to link invoices to POs.

## Querying Linus Requests

### View All Requests
```sql
SELECT 
    Request_Id,
    Invoice_Name,
    PO_Name,
    Vendor_Name,
    Supplemental_Amount,
    Status,
    Request_Date
FROM hackathon.hackathon_build_hold_busters.Linus_Requests
ORDER BY Request_Date DESC;
```

### View Pending Requests
```sql
SELECT *
FROM hackathon.hackathon_build_hold_busters.Linus_Requests
WHERE Status = 'Pending'
ORDER BY Supplemental_Amount DESC;
```

### Approve/Reject Requests
```sql
-- Approve a request
UPDATE hackathon.hackathon_build_hold_busters.Linus_Requests
SET Status = 'Approved', LastModifiedDate = CURRENT_TIMESTAMP()
WHERE Request_Id = 'REQ-XXXXXXXXXXXX';

-- Reject a request
UPDATE hackathon.hackathon_build_hold_busters.Linus_Requests
SET Status = 'Rejected', LastModifiedDate = CURRENT_TIMESTAMP()
WHERE Request_Id = 'REQ-XXXXXXXXXXXX';
```

## Troubleshooting

### "PO Name not available or Purchase Orders data not loaded"
**Cause:** Either the invoice doesn't have a PO_Name, or Purchase_Orders table couldn't be loaded.

**Solution:**
1. Check if `PO_Name` column exists in invoices table
2. Verify `Purchase_Orders` table exists in your schema
3. Check table permissions

### "PO [NAME] not found in Purchase Orders"
**Cause:** The PO referenced by the invoice doesn't exist in Purchase_Orders table.

**Solution:**
1. Verify the PO_Name value in the invoice
2. Check if the PO exists in Purchase_Orders table
3. Ensure PO_Name values match exactly (case-sensitive)

### Button Click Does Nothing
**Cause:** Database insert failed (check Databricks SQL Warehouse status).

**Solution:**
1. Verify `Linus_Requests` table exists
2. Check SQL Warehouse is running
3. Verify user has INSERT permissions on the table

## Feature Architecture

### Data Flow
```
1. User selects invoice with PO amount error
2. App fetches PO details from Purchase_Orders
3. App calculates all invoices for same PO_Name
4. App computes pending, paid, and supplemental amounts
5. User reviews calculations
6. User clicks "Send to Linus"
7. App generates unique Request_Id
8. App inserts record into Linus_Requests table
9. Success confirmation displayed
```

### Key Functions
- `get_purchase_orders()` - Fetches PO data
- `insert_linus_request()` - Inserts request into database
- Calculation logic in Error Analysis tab (col3)

## Future Enhancements
- Email notification to Linus on new requests
- Approval workflow within dashboard
- Request history view
- Bulk request submission
- PO supplement tracking after approval

## Support
For issues or questions, please check:
1. Table creation script ran successfully
2. Purchase_Orders table is populated
3. Invoices have PO_Name values
4. SQL Warehouse is active
5. User has appropriate permissions

