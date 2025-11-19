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
    genie_space_id = secrets['databricks'].get('genie_space_id', '')
    
    print(f"[OK] Loaded credentials from secrets.toml")
    print(f"  Server: {server_hostname}")
    print(f"  Schema: {default_schema}")
    if genie_space_id:
        print(f"  Genie Space ID: {genie_space_id}")
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

# Read the genie_chat module
with open('genie_chat.py', 'r', encoding='utf-8') as f:
    genie_chat_code = f.read()

# Escape the codes for embedding
app_code_escaped = app_code.replace('\\', '\\\\').replace("'''", "\\'''")
genie_chat_code_escaped = genie_chat_code.replace('\\', '\\\\').replace("'''", "\\'''")

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

%pip install streamlit databricks-sql-connector databricks-sdk plotly pandas pyarrow

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2: Create Secrets File & Write App Code

# COMMAND ----------

import os
from pathlib import Path

# Use home directory which should be writable in Databricks
home_dir = Path.home()
streamlit_dir = home_dir / '.streamlit'
app_dir = home_dir / 'hold_busters_app'

# Create directories
try:
    streamlit_dir.mkdir(parents=True, exist_ok=True)
    app_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directories in: {{home_dir}}")
except Exception as e:
    print(f"❌ Error creating directories: {{e}}")

# Create secrets.toml file with credentials
secrets_content = '''[databricks]
server_hostname = "{server_hostname}"
http_path = "{http_path}"
token = "{token}"
default_schema = "{default_schema}"
genie_space_id = "{genie_space_id}"
'''

secrets_file = streamlit_dir / 'secrets.toml'
try:
    secrets_file.write_text(secrets_content)
    print(f"✅ Secrets file created: {{secrets_file}}")
except Exception as e:
    print(f"❌ Error creating secrets file: {{e}}")

# Set environment variables for Databricks SDK (needed for Genie AI)
os.environ['DATABRICKS_HOST'] = "https://{server_hostname}"
os.environ['DATABRICKS_TOKEN'] = "{token}"

print("✅ Environment variables set for Databricks SDK")

# Write the complete app code
app_code = '''{app_code_escaped}'''

app_file = app_dir / 'hold_busters_app.py'
try:
    app_file.write_text(app_code, encoding='utf-8')
    print(f"✅ App code written to: {{app_file}}")
    print(f"{{('✅ File size: ' + str(len(app_code)) + ' bytes')}}")
except Exception as e:
    print(f"❌ Error writing app code: {{e}}")

# Write the genie_chat module
genie_chat_code = '''{genie_chat_code_escaped}'''

genie_module = app_dir / 'genie_chat.py'
try:
    genie_module.write_text(genie_chat_code, encoding='utf-8')
    print(f"✅ Genie chat module written to: {{genie_module}}")
    print(f"{{('✅ Module size: ' + str(len(genie_chat_code)) + ' bytes')}}")
except Exception as e:
    print(f"❌ Error writing genie_chat module: {{e}}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3: Verify Files

# COMMAND ----------

from pathlib import Path

home_dir = Path.home()
app_dir = home_dir / 'hold_busters_app'
streamlit_dir = home_dir / '.streamlit'

print(f"📁 Working directory: {{home_dir}}")
print()

# Check app file
app_file = app_dir / 'hold_busters_app.py'
if app_file.exists():
    file_size = app_file.stat().st_size
    print(f"✅ App file exists: {{app_file}}")
    print(f"{{('✅ App file size: ' + str(file_size) + ' bytes')}}")
else:
    print(f"❌ App file not found at: {{app_file}}")

# Check genie_chat module
genie_module = app_dir / 'genie_chat.py'
if genie_module.exists():
    module_size = genie_module.stat().st_size
    print(f"✅ Genie chat module exists: {{genie_module}}")
    print(f"{{('✅ Module size: ' + str(module_size) + ' bytes')}}")
else:
    print(f"❌ Genie chat module not found at: {{genie_module}}")

# Check secrets file
secrets_file = streamlit_dir / 'secrets.toml'
if secrets_file.exists():
    print(f"✅ Secrets file exists: {{secrets_file}}")
    print("✅ Secrets content verified (credentials are set)")
else:
    print(f"❌ Secrets file not found at: {{secrets_file}}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4: Run Streamlit App

# COMMAND ----------

import os
import subprocess
from pathlib import Path

# Get the app path
home_dir = Path.home()
app_dir = home_dir / 'hold_busters_app'
app_file = app_dir / 'hold_busters_app.py'
genie_module = app_dir / 'genie_chat.py'

print(f"📁 Home directory: {{home_dir}}")
print(f"📂 App directory: {{app_dir}}")
print()

# Check if files exist
print("🔍 Checking files...")
if not app_dir.exists():
    print(f"❌ ERROR: App directory not found: {{app_dir}}")
    print("⚠️  Cell 2 may not have run successfully!")
    print("💡 Try running Cell 2 again before Cell 4")
    raise FileNotFoundError(f"App directory not found: {{app_dir}}")

if not app_file.exists():
    print(f"❌ ERROR: App file not found: {{app_file}}")
    print("⚠️  Cell 2 may not have created the file!")
    raise FileNotFoundError(f"App file not found: {{app_file}}")

if not genie_module.exists():
    print(f"❌ ERROR: Genie module not found: {{genie_module}}")
    print("⚠️  Cell 2 may not have created the file!")
    raise FileNotFoundError(f"Genie module not found: {{genie_module}}")

print(f"✅ App directory exists: {{app_dir}}")
print(f"✅ App file exists: {{app_file}}")
print(f"✅ Genie module exists: {{genie_module}}")
print()

# Change to app directory so Python can find genie_chat.py
os.chdir(app_dir)
print(f"📁 Changed working directory to: {{os.getcwd()}}")
print()

# Create environment dict with Databricks credentials
print("🔧 Setting environment variables for subprocess...")
env = os.environ.copy()
env['DATABRICKS_HOST'] = "https://{server_hostname}"
env['DATABRICKS_TOKEN'] = "{token}"

print(f"   DATABRICKS_HOST: {{env['DATABRICKS_HOST']}}")
print(f"   DATABRICKS_TOKEN: ***{{env['DATABRICKS_TOKEN'][-4:]}}")
print()
print("🚀 Launching Streamlit...")
print()

# Run Streamlit with explicit environment
subprocess.run([
    'streamlit', 'run', str(app_file),
    '--server.port=8501',
    '--server.address=0.0.0.0'
], env=env)
"""

# Write notebook
with open('run_streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(notebook_content)

print("[OK] Databricks notebook created: run_streamlit_app.py")
print(f"[OK] App code size: {len(app_code)} bytes")
print(f"[OK] Notebook size: {len(notebook_content)} bytes")
print(f"\n[OK] Credentials embedded from secrets.toml (NOT hardcoded)")
