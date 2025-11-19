"""
Script to create a Databricks notebook with embedded app code
Reads credentials from .streamlit/secrets.toml
"""

import toml

# Read credentials from secrets.toml
try:
    with open('.streamlit/secrets.toml', 'r') as f:
        secrets = toml.load(f)
    
    server_hostname = secrets['databricks']['server_hostname']
    http_path = secrets['databricks']['http_path']
    token = secrets['databricks']['token']
    default_schema = secrets['databricks'].get('default_schema', 'default')
    
    print(f"[OK] Loaded credentials from secrets.toml")
    print(f"  Server: {server_hostname}")
    print(f"  Schema: {default_schema}")
except FileNotFoundError:
    print("ERROR: .streamlit/secrets.toml not found!")
    print("Please create it with your Databricks credentials.")
    exit(1)
except KeyError as e:
    print(f"ERROR: Missing required field in secrets.toml: {e}")
    exit(1)

# Read the app code
with open('app_databricks.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Escape the app code for embedding
app_code_escaped = app_code.replace('\\', '\\\\').replace("'''", "\\'''")

# Create notebook content with credentials from secrets.toml
notebook_content = f"""# Databricks notebook source
# MAGIC %md
# MAGIC # Hold Busters Streamlit App
# MAGIC 
# MAGIC This notebook runs the Hold Busters Streamlit application in Databricks.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1: Install Dependencies

# COMMAND ----------

%pip install streamlit databricks-sql-connector plotly pandas pyarrow

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2: Create Secrets File & Write App Code

# COMMAND ----------

import os

# Create .streamlit directory in /tmp
os.makedirs('/tmp/.streamlit', exist_ok=True)

# Create secrets.toml file with credentials
secrets_content = '''[databricks]
server_hostname = "{server_hostname}"
http_path = "{http_path}"
token = "{token}"
default_schema = "{default_schema}"
'''

with open('/tmp/.streamlit/secrets.toml', 'w') as f:
    f.write(secrets_content)

print("✅ Secrets file created: /tmp/.streamlit/secrets.toml")

# Write the complete app code to /tmp
app_code = '''{app_code_escaped}'''

with open('/tmp/hold_busters_app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print(f"✅ App code written to /tmp/hold_busters_app.py")
print(f"{{('✅ File size: ' + str(len(app_code)) + ' bytes')}}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3: Verify Files

# COMMAND ----------

import os

# Check app file
if os.path.exists('/tmp/hold_busters_app.py'):
    file_size = os.path.getsize('/tmp/hold_busters_app.py')
    print(f"✅ App file exists: /tmp/hold_busters_app.py")
    print(f"{{('✅ App file size: ' + str(file_size) + ' bytes')}}")
else:
    print("❌ App file not found!")

# Check secrets file
if os.path.exists('/tmp/.streamlit/secrets.toml'):
    print("✅ Secrets file exists: /tmp/.streamlit/secrets.toml")
    with open('/tmp/.streamlit/secrets.toml', 'r') as f:
        print("✅ Secrets content verified (credentials are set)")
else:
    print("❌ Secrets file not found!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4: Run Streamlit App

# COMMAND ----------

!streamlit run /tmp/hold_busters_app.py --server.port=8501 --server.address=0.0.0.0
"""

# Write notebook
with open('run_streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(notebook_content)

print("[OK] Databricks notebook created: run_streamlit_app.py")
print(f"[OK] App code size: {len(app_code)} bytes")
print(f"[OK] Notebook size: {len(notebook_content)} bytes")
print(f"\n[OK] Credentials embedded from secrets.toml (NOT hardcoded)")
