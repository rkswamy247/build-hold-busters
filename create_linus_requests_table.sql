-- SQL Script to Create Linus_Requests Table
-- Execute this in Databricks SQL Editor

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

-- Add a comment to describe the table
COMMENT ON TABLE hackathon.hackathon_build_hold_busters.Linus_Requests IS 
'Stores requests sent to Linus for PO supplement approvals when invoice amounts exceed available PO balance';

