"""
Synthetic Data Generator for Hold Busters Dashboard
Creates test invoices with related data for all statuses
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import json
import uuid

# Configuration
VENDOR_NAME = "Synthetic Tech Partners 11"
PO_NAME = "Synthetic_PO_15"
PROJECT_NAME = "Synthetic Project Alpha"
PROJECT_NUMBER = "PROJ-SYN-001"
COMPANY = "Frontier Communications"

# Status definitions
STATUSES = ["Draft", "Submitted", "Approved", "Paid", "Hold"]
STATES = ["CA", "NY", "TX", "FL", "WA"]
COST_CATEGORIES = [
    "Labor - Engineering",
    "Labor - Installation", 
    "Materials - Network Equipment",
    "Materials - Fiber Cable",
    "Materials - Hardware",
    "Services - Consulting",
    "Services - Project Management"
]

def generate_invoice_id():
    """Generate unique invoice ID"""
    return f"INV-SYN-{random.randint(10000, 99999)}"

def generate_project():
    """Generate project data"""
    project_id = f"a0F{uuid.uuid4().hex[:15]}"
    
    project = {
        'Project_Id': project_id,
        'Infinium_Project_Number__c': PROJECT_NUMBER,
        'Company__c': COMPANY,
        'Infinium_Status__c': 'Active',
        'Approval_Status__c': 'Approved'
    }
    
    return pd.DataFrame([project])

def generate_budget_lines(project_id, num_lines=5):
    """Generate budget lines for the project"""
    budget_lines = []
    
    for i in range(num_lines):
        budget_line = {
            'Budget_Line_Id': f"a0G{uuid.uuid4().hex[:15]}",
            'Project_Id': project_id,
            'Cost_Category__c': random.choice(COST_CATEGORIES),
            'Budget_Amount__c': round(random.uniform(50000, 200000), 2),
            'Spent_Amount__c': round(random.uniform(10000, 80000), 2),
            'Remaining_Amount__c': 0,  # Will calculate
            'Status__c': 'Active'
        }
        budget_line['Remaining_Amount__c'] = (
            budget_line['Budget_Amount__c'] - budget_line['Spent_Amount__c']
        )
        budget_lines.append(budget_line)
    
    return pd.DataFrame(budget_lines)

def generate_invoice(status, project_id, index):
    """Generate a single invoice"""
    invoice_id = generate_invoice_id()
    invoice_date = datetime.now() - timedelta(days=random.randint(1, 180))
    approval_date = None
    days_pending = 0
    integration_status = None
    error_message = None
    
    # Set dates and status based on invoice status
    if status == "Draft":
        days_pending = random.randint(1, 5)
        integration_status = "Not Submitted"
    elif status == "Submitted":
        days_pending = random.randint(5, 15)
        integration_status = "Pending"
    elif status == "Approved":
        approval_date = invoice_date + timedelta(days=random.randint(3, 10))
        days_pending = (datetime.now() - approval_date).days
        integration_status = "Success"
    elif status == "Paid":
        approval_date = invoice_date + timedelta(days=random.randint(3, 10))
        days_pending = (datetime.now() - approval_date).days
        integration_status = "Success"
    elif status == "Hold":
        days_pending = random.randint(30, 90)
        integration_status = "Error"
        error_message = random.choice([
            "Vendor validation failed: Vendor ID not found in Infinium system",
            "Budget line not found for cost category in project",
            "PO number mismatch: Expected PO-12345, received Synthetic_PO_15",
            "Approval limit exceeded: Invoice amount requires director approval",
            "Duplicate invoice detected: Similar invoice found with same amount"
        ])
    
    invoice = {
        'Invoice_Id': invoice_id,
        'Invoice_Name': f"{VENDOR_NAME}-{status}-{index:02d}",
        'Vendor__Name': VENDOR_NAME,
        'PO_Name__c': PO_NAME,
        'Project_Id': project_id,
        'Invoice_Date__c': invoice_date.strftime('%Y-%m-%d'),
        'Total_Amount__c': round(random.uniform(5000, 75000), 2),
        'sitetracker__Status__c': status,
        'Days_Pending_Approval__c': days_pending,
        'Integration_Status__c': integration_status,
        'Integration_Error_Message__c': error_message,
        'Reason__c': f"Work completed for {PO_NAME}",
        'State__c': random.choice(STATES),
        'Approval_Date__c': approval_date.strftime('%Y-%m-%d') if approval_date else None,
        'Due_Date_Formula__c': (invoice_date + timedelta(days=30)).strftime('%Y-%m-%d')
    }
    
    return invoice

def generate_invoice_lines(invoice_id, invoice_amount, num_lines=None):
    """Generate invoice lines for an invoice"""
    if num_lines is None:
        num_lines = random.randint(2, 8)
    
    lines = []
    remaining_amount = invoice_amount
    
    for i in range(num_lines):
        # Split amount across lines
        if i == num_lines - 1:
            line_amount = remaining_amount
        else:
            line_amount = round(remaining_amount * random.uniform(0.1, 0.4), 2)
            remaining_amount -= line_amount
        
        quantity = random.randint(1, 100)
        unit_price = round(line_amount / quantity, 2)
        
        line = {
            'Invoice_Line_Id': f"a0H{uuid.uuid4().hex[:15]}",
            'Invoice_Id': invoice_id,
            'Invoice_Line_Number__c': i + 1,
            'Invoice_Amount__c': line_amount,
            'Invoice_Status__c': random.choice(['Approved', 'Pending', 'Review Required']),
            'Cost_Category_Name__c': random.choice(COST_CATEGORIES),
            'sitetracker__Quantity__c': quantity,
            'sitetracker__Unit_Price__c': unit_price,
            'Description__c': f"Line item {i+1} for {PO_NAME}"
        }
        lines.append(line)
    
    return pd.DataFrame(lines)

def generate_integration_response(invoice_id, invoice_status, error_message):
    """Generate integration response for an invoice"""
    
    # Determine operation based on status
    operation = "CREATE"
    if invoice_status == "Paid":
        operation = "UPDATE"
    elif invoice_status == "Hold":
        operation = "VALIDATE"
    
    # Create request
    infinium_request = {
        "vendor_id": "VEND-12345",
        "vendor_name": VENDOR_NAME,
        "po_number": PO_NAME,
        "invoice_id": invoice_id,
        "amount": round(random.uniform(5000, 75000), 2),
        "currency": "USD",
        "invoice_date": datetime.now().strftime('%Y-%m-%d'),
        "operation": operation
    }
    
    # Create response based on status
    if invoice_status == "Hold":
        infinium_response = {
            "status": "error",
            "code": random.choice([400, 404, 422, 500]),
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "invoice_id": invoice_id
        }
        error_msg = error_message
    else:
        infinium_response = {
            "status": "success",
            "code": 200,
            "message": "Invoice processed successfully",
            "infinium_invoice_number": f"INF-{random.randint(100000, 999999)}",
            "timestamp": datetime.now().isoformat(),
            "invoice_id": invoice_id
        }
        error_msg = None
    
    response = {
        'Intg_Resp_Id': f"a0I{uuid.uuid4().hex[:15]}",
        'Invoice_Id': invoice_id,
        'Infinium_Request__c': json.dumps(infinium_request, indent=2),
        'Infinium_Response__c': json.dumps(infinium_response, indent=2),
        'Error_Message__c': error_msg,
        'Operation__c': operation
    }
    
    return response

def generate_all_data(num_invoices_per_status=2):
    """Generate complete synthetic dataset"""
    
    print("Generating Synthetic Data for Hold Busters Dashboard")
    print("=" * 60)
    
    # Generate project
    print("\nGenerating Project...")
    project_df = generate_project()
    project_id = project_df['Project_Id'].iloc[0]
    print(f"   + Project: {PROJECT_NAME} (ID: {project_id})")
    
    # Generate budget lines
    print("\nGenerating Budget Lines...")
    budget_lines_df = generate_budget_lines(project_id)
    print(f"   + Created {len(budget_lines_df)} budget lines")
    
    # Generate invoices, lines, and responses
    print("\nGenerating Invoices...")
    all_invoices = []
    all_invoice_lines = []
    all_integration_responses = []
    
    for status in STATUSES:
        print(f"\n   Status: {status}")
        for i in range(num_invoices_per_status):
            # Generate invoice
            invoice = generate_invoice(status, project_id, i + 1)
            all_invoices.append(invoice)
            
            # Generate invoice lines
            lines_df = generate_invoice_lines(
                invoice['Invoice_Id'], 
                invoice['Total_Amount__c']
            )
            all_invoice_lines.append(lines_df)
            
            # Generate integration response (not for Draft)
            if status != "Draft":
                response = generate_integration_response(
                    invoice['Invoice_Id'],
                    status,
                    invoice['Integration_Error_Message__c']
                )
                all_integration_responses.append(response)
            
            print(f"      + {invoice['Invoice_Name']} - ${invoice['Total_Amount__c']:,.2f}")
    
    # Create DataFrames
    invoices_df = pd.DataFrame(all_invoices)
    invoice_lines_df = pd.concat(all_invoice_lines, ignore_index=True)
    integration_responses_df = pd.DataFrame(all_integration_responses)
    
    print("\n" + "=" * 60)
    print("SUCCESS: Data Generation Complete!")
    print(f"\nSummary:")
    print(f"   - Projects: {len(project_df)}")
    print(f"   - Budget Lines: {len(budget_lines_df)}")
    print(f"   - Invoices: {len(invoices_df)}")
    print(f"   - Invoice Lines: {len(invoice_lines_df)}")
    print(f"   - Integration Responses: {len(integration_responses_df)}")
    
    return {
        'projects': project_df,
        'budget_lines': budget_lines_df,
        'invoices': invoices_df,
        'invoice_lines': invoice_lines_df,
        'integration_responses': integration_responses_df
    }

def save_to_csv(data_dict, output_dir='synthetic_data'):
    """Save all datasets to CSV files"""
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\nSaving to CSV files in '{output_dir}/'...")
    
    for name, df in data_dict.items():
        filepath = os.path.join(output_dir, f'{name}.csv')
        df.to_csv(filepath, index=False)
        print(f"   + {filepath} ({len(df)} rows)")
    
    print("\nAll files saved!")

def save_to_databricks(data_dict, schema_name):
    """
    Save data to Databricks tables
    NOTE: Requires databricks-sql-connector and proper credentials
    """
    from databricks import sql
    import os
    
    print(f"\nUploading to Databricks schema: {schema_name}")
    
    # Get credentials from environment or secrets
    hostname = os.getenv('DATABRICKS_SERVER_HOSTNAME')
    http_path = os.getenv('DATABRICKS_HTTP_PATH')
    token = os.getenv('DATABRICKS_TOKEN')
    
    if not all([hostname, http_path, token]):
        print("ERROR: Databricks credentials not found in environment variables")
        print("   Set: DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN")
        return
    
    # Connect to Databricks
    connection = sql.connect(
        server_hostname=hostname,
        http_path=http_path,
        access_token=token
    )
    
    cursor = connection.cursor()
    
    try:
        for table_name, df in data_dict.items():
            print(f"\n   Uploading to {schema_name}.{table_name}...")
            
            # Create temporary view from pandas DataFrame
            # Note: For production, use bulk insert methods
            for _, row in df.iterrows():
                columns = ', '.join(df.columns)
                values = ', '.join([f"'{str(v)}'" if pd.notna(v) else 'NULL' for v in row])
                
                insert_query = f"""
                INSERT INTO {schema_name}.{table_name} ({columns})
                VALUES ({values})
                """
                cursor.execute(insert_query)
            
            print(f"      + Inserted {len(df)} rows")
        
        print("\nAll data uploaded to Databricks!")
        
    except Exception as e:
        print(f"\nERROR uploading to Databricks: {str(e)}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Generate data
    data = generate_all_data(num_invoices_per_status=2)
    
    # Save to CSV
    save_to_csv(data)
    
    # Optionally save to Databricks (uncomment to use)
    # save_to_databricks(data, 'hackathon/hackathon_build_hold_busters')
    
    print("\n" + "=" * 60)
    print("SUCCESS: Synthetic Data Generation Complete!")
    print("\nNext steps:")
    print("1. Review CSV files in 'synthetic_data/' directory")
    print("2. Upload to Databricks using:")
    print("   - Databricks UI (Data Import)")
    print("   - Or uncomment save_to_databricks() function")
    print("3. Refresh your dashboard to see the new data!")

