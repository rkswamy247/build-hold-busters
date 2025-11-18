"""
Simple Hold Busters app - no pandas/plotly dependencies
Just to test Databricks connection
"""
import streamlit as st
from databricks import sql
import os

st.set_page_config(page_title="Hold Busters", page_icon="🔍", layout="wide")

st.title("🔍 Hold Busters - Simple Version")
st.markdown("### Testing Databricks Connection")
st.markdown("---")

# Get credentials from secrets
if hasattr(st, 'secrets') and 'databricks' in st.secrets:
    server_hostname = st.secrets.databricks.server_hostname
    http_path = st.secrets.databricks.http_path
    token = st.secrets.databricks.token
    default_schema = st.secrets.databricks.default_schema
else:
    st.error("❌ Secrets not configured!")
    st.stop()

# Schema input
schema_name = st.sidebar.text_input("Schema Name", value=default_schema)

# Try connection
try:
    st.info("🔌 Connecting to Databricks...")
    
    conn = sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=token
    )
    
    st.success("✅ Successfully connected to Databricks!")
    
    # Try a simple query
    st.subheader("📊 Invoice Data")
    
    with st.spinner("Loading data..."):
        cursor = conn.cursor()
        
        query = f"""
        SELECT 
            Invoice_Id,
            Invoice_Name,
            Vendor__Name,
            Total_Amount__c,
            sitetracker__Status__c as Status
        FROM {schema_name}.invoices
        LIMIT 100
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
    
    st.success(f"✅ Found {len(results)} invoices")
    
    # Display as simple table (no pandas needed)
    st.subheader("Sample Data")
    
    # Show column headers
    st.write("**Columns:**", ", ".join(columns))
    
    # Show first 10 rows
    st.write("**First 10 rows:**")
    for i, row in enumerate(results[:10]):
        st.text(f"Row {i+1}: {dict(zip(columns, row))}")
    
    # Show summary stats
    st.subheader("📈 Quick Stats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Invoices Loaded", len(results))
    
    with col2:
        # Count by status
        status_counts = {}
        for row in results:
            status = row[4]  # Status column
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.write("**Status Breakdown:**")
        for status, count in status_counts.items():
            st.write(f"- {status}: {count}")
    
    conn.close()
    
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.code(str(e))

st.markdown("---")
st.info("💡 This is a simplified version. Install full dependencies for charts and advanced features.")

