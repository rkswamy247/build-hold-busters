"""
Upload synthetic CSV data to Databricks tables
"""

from databricks import sql
import pandas as pd
import os

# Read credentials from secrets.toml
def get_credentials():
    """Try to read credentials from .streamlit/secrets.toml"""
    try:
        import toml
        secrets_path = '.streamlit/secrets.toml'
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            return {
                'hostname': secrets['databricks']['server_hostname'],
                'http_path': secrets['databricks']['http_path'],
                'token': secrets['databricks']['token'],
                'schema': secrets['databricks'].get('default_schema', 'hackathon.hackathon_build_hold_busters')
            }
    except Exception as e:
        print(f"Could not read secrets.toml: {e}")
    
    # Fallback to manual entry
    print("\nPlease enter your Databricks credentials:")
    return {
        'hostname': input("Server Hostname: "),
        'http_path': input("HTTP Path: "),
        'token': input("Token: "),
        'schema': input("Schema (default: hackathon.hackathon_build_hold_busters): ") or 'hackathon.hackathon_build_hold_busters'
    }

# CSV files to upload
FILES_TO_UPLOAD = {
    'projects': 'synthetic_data/projects.csv',
    'budget_lines': 'synthetic_data/budget_lines.csv',
    'invoices': 'synthetic_data/invoices.csv',
    'invoice_lines': 'synthetic_data/invoice_lines.csv',
    'Integration_Responses': 'synthetic_data/integration_responses.csv'
}

def upload_csv_to_table(connection, csv_file, table_name, schema):
    """Upload CSV data to Databricks table using batch insert"""
    
    print(f"\nUploading {csv_file} to {schema}.{table_name}...")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    print(f"  Read {len(df)} rows from CSV")
    
    if len(df) == 0:
        print("  Skipping - no data to upload")
        return
    
    # Get cursor
    cursor = connection.cursor()
    
    try:
        # Build column names
        columns = ', '.join([f"`{col}`" for col in df.columns])
        
        # Insert rows in batches
        batch_size = 100
        total_rows = len(df)
        
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            batch = df.iloc[start_idx:end_idx]
            
            # Build VALUES for multiple rows
            value_groups = []
            for _, row in batch.iterrows():
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append('NULL')
                    elif isinstance(val, (int, float)) and not pd.isna(val):
                        values.append(str(val))
                    else:
                        # Escape single quotes
                        escaped_val = str(val).replace("'", "''")
                        values.append(f"'{escaped_val}'")
                
                value_groups.append(f"({', '.join(values)})")
            
            # Build INSERT statement
            values_str = ',\n    '.join(value_groups)
            insert_query = f"""
            INSERT INTO {schema}.{table_name} ({columns})
            VALUES
                {values_str}
            """
            
            cursor.execute(insert_query)
            print(f"  Inserted {end_idx}/{total_rows} rows...")
        
        print(f"  SUCCESS: Inserted all {len(df)} rows")
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        raise
    finally:
        cursor.close()

def verify_upload(connection, schema, vendor_name="Synthetic Tech Partners 11"):
    """Verify the uploaded data"""
    print(f"\n{'=' * 60}")
    print("Verifying uploaded data...")
    print('=' * 60)
    
    cursor = connection.cursor()
    
    try:
        # Count synthetic invoices
        query = f"""
        SELECT COUNT(*) as count
        FROM {schema}.invoices
        WHERE Vendor__Name = '{vendor_name}'
        """
        cursor.execute(query)
        result = cursor.fetchone()
        invoice_count = result[0] if result else 0
        
        print(f"\nFound {invoice_count} invoices for vendor: {vendor_name}")
        
        if invoice_count > 0:
            # Show invoice details
            query = f"""
            SELECT 
                Invoice_Name,
                sitetracker__Status__c as Status,
                Total_Amount__c as Amount,
                Integration_Error_Message__c as Error
            FROM {schema}.invoices
            WHERE Vendor__Name = '{vendor_name}'
            ORDER BY Total_Amount__c DESC
            LIMIT 10
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            print("\nSynthetic Invoices:")
            print("-" * 60)
            for row in results:
                print(f"  {row[0]:<40} | {row[1]:<10} | ${row[2]:>10,.2f}")
                if row[3]:
                    print(f"    Error: {row[3][:60]}...")
            
            print("\nSUCCESS: Data uploaded and verified!")
        else:
            print("\nWARNING: No synthetic invoices found. Upload may have failed.")
        
    except Exception as e:
        print(f"\nERROR verifying data: {str(e)}")
    finally:
        cursor.close()

def main():
    print("=" * 60)
    print("Upload Synthetic Data to Databricks")
    print("=" * 60)
    
    # Check if files exist
    print("\nChecking for CSV files...")
    missing_files = []
    for table_name, csv_file in FILES_TO_UPLOAD.items():
        if os.path.exists(csv_file):
            file_size = os.path.getsize(csv_file)
            print(f"  + {csv_file} ({file_size:,} bytes)")
        else:
            print(f"  - {csv_file} (NOT FOUND)")
            missing_files.append(csv_file)
    
    if missing_files:
        print(f"\nERROR: Missing {len(missing_files)} file(s). Please run generate_synthetic_data.py first.")
        return
    
    # Get credentials
    creds = get_credentials()
    
    # Connect to Databricks
    print("\nConnecting to Databricks...")
    print(f"  Host: {creds['hostname']}")
    print(f"  Schema: {creds['schema']}")
    
    try:
        connection = sql.connect(
            server_hostname=creds['hostname'],
            http_path=creds['http_path'],
            access_token=creds['token']
        )
        print("  Connected successfully!")
    except Exception as e:
        print(f"  ERROR: Could not connect to Databricks: {str(e)}")
        print("\nPlease check your credentials in .streamlit/secrets.toml")
        return
    
    try:
        # Upload each file
        for table_name, csv_file in FILES_TO_UPLOAD.items():
            upload_csv_to_table(connection, csv_file, table_name, creds['schema'])
        
        # Verify upload
        verify_upload(connection, creds['schema'])
        
        print("\n" + "=" * 60)
        print("All data uploaded successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Refresh your Hold Busters dashboard")
        print("2. Go to the 'Error Analysis' tab")
        print("3. You should see the new synthetic invoices!")
        
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()
        print("\nConnection closed")

if __name__ == "__main__":
    # Try to install toml if not present
    try:
        import toml
    except ImportError:
        print("Installing required package: toml")
        os.system("pip install toml")
        import toml
    
    main()

