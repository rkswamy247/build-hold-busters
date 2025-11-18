"""
Simple test version of Hold Busters app for debugging Databricks deployment
"""
import streamlit as st
import os
import sys

st.set_page_config(page_title="Hold Busters Test", page_icon="🔍", layout="wide")

st.title("🔍 Hold Busters - Connection Test")
st.markdown("### Testing Databricks Environment")
st.markdown("---")

# Show Python version
st.subheader("Python Environment")
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")

# Show environment variables
st.subheader("Environment Variables")
env_vars = {
    "DATABRICKS_SERVER_HOSTNAME": os.environ.get("DATABRICKS_SERVER_HOSTNAME", "NOT SET"),
    "DATABRICKS_HTTP_PATH": os.environ.get("DATABRICKS_HTTP_PATH", "NOT SET"),
    "DATABRICKS_TOKEN": "***HIDDEN***" if os.environ.get("DATABRICKS_TOKEN") else "NOT SET",
}

for key, value in env_vars.items():
    if value == "NOT SET":
        st.error(f"❌ {key}: {value}")
    else:
        st.success(f"✅ {key}: {value}")

# Test imports
st.subheader("Package Imports")
packages = [
    ("pandas", "pd"),
    ("plotly.express", "px"),
    ("databricks.sql", "sql"),
]

for package_name, alias in packages:
    try:
        __import__(package_name)
        st.success(f"✅ {package_name} imported successfully")
    except ImportError as e:
        st.error(f"❌ {package_name} import failed: {str(e)}")

# Test Databricks connection (without crashing)
st.subheader("Databricks SQL Connection Test")

try:
    from databricks import sql
    
    server_hostname = os.environ.get("DATABRICKS_SERVER_HOSTNAME")
    http_path = os.environ.get("DATABRICKS_HTTP_PATH")
    token = os.environ.get("DATABRICKS_TOKEN")
    
    if not all([server_hostname, http_path]):
        st.warning("⚠️ Missing required environment variables for connection")
    else:
        with st.spinner("Testing connection..."):
            try:
                # Attempt connection
                if token:
                    conn = sql.connect(
                        server_hostname=server_hostname,
                        http_path=http_path,
                        access_token=token
                    )
                else:
                    st.warning("⚠️ No token found, trying without token...")
                    conn = sql.connect(
                        server_hostname=server_hostname,
                        http_path=http_path
                    )
                
                st.success("✅ Successfully connected to Databricks!")
                
                # Test a simple query
                with st.spinner("Testing query..."):
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchall()
                    st.success(f"✅ Test query successful: {result}")
                    cursor.close()
                
                conn.close()
                
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
                st.code(str(e))
                
except Exception as e:
    st.error(f"❌ Error during connection test: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")
st.info("If all tests pass above, the full app should work!")

