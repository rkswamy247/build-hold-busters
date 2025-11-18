"""
Check the schema of existing Databricks tables
"""

from databricks import sql
import toml

# Read credentials
secrets = toml.load('.streamlit/secrets.toml')
hostname = secrets['databricks']['server_hostname']
http_path = secrets['databricks']['http_path']
token = secrets['databricks']['token']
schema = secrets['databricks'].get('default_schema', 'hackathon.hackathon_build_hold_busters')

# Connect
connection = sql.connect(
    server_hostname=hostname,
    http_path=http_path,
    access_token=token
)

cursor = connection.cursor()

# Check invoice_lines table
print("Table schema for invoice_lines:")
print("=" * 80)
cursor.execute(f"DESCRIBE {schema}.invoice_lines")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

cursor.close()
connection.close()

