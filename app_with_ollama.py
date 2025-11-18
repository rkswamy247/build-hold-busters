"""
Hold Busters Dashboard with Ollama AI Chat Agent (Local & Free!)
"""
import streamlit as st
from databricks import sql
import ollama
import json
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Hold Busters Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    .stMetric {background-color: #f0f2f6; padding: 15px; border-radius: 5px;}
    .chat-message {padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 3px solid;}
    .user-message {background-color: #e3f2fd; border-left-color: #2196F3;}
    .assistant-message {background-color: #f5f5f5; border-left-color: #4CAF50;}
    </style>
""", unsafe_allow_html=True)

# Database schema for AI
DATABASE_SCHEMA = """
Database Schema: hackathon.hackathon_build_hold_busters

Table: invoices
- Invoice_Id (STRING): Unique invoice identifier
- Invoice_Name (STRING): Invoice name/number
- Vendor__Name (STRING): Vendor name
- Invoice_Date__c (DATE): Invoice date
- Total_Amount__c (DECIMAL): Total invoice amount
- sitetracker__Status__c (STRING): Status (e.g., 'Hold', 'Approved', 'Pending')
- Days_Pending_Approval__c (INTEGER): Days invoice has been pending
- Integration_Status__c (STRING): Integration status
- Reason__c (STRING): Reason for hold/status
- State__c (STRING): US State
- Approval_Date__c (DATE): Date approved
- Due_Date_Formula__c (DATE): Due date

Table: invoice_lines
- Invoice_Line_Id (STRING): Unique line item ID
- Invoice_Id (STRING): Foreign key to invoices
- Project_Id (STRING): Associated project
- Invoice_Amount__c (DECIMAL): Line item amount
- Invoice_Status__c (STRING): Line status
- Infinium_Project_Number__c (STRING): Project number
- Company_Code__c (STRING): Company code
- Cost_Category_Name__c (STRING): Cost category

Table: projects
- Project_Id (STRING): Unique project ID
- Infinium_Project_Number__c (STRING): Project number
- Company__c (STRING): Company
- Infinium_Status__c (STRING): Project status
- Approval_Status__c (STRING): Approval status
"""

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'ollama_available' not in st.session_state:
    st.session_state.ollama_available = None

# Check if Ollama is running
@st.cache_resource
def check_ollama():
    try:
        models = ollama.list()
        return True, models
    except Exception as e:
        return False, str(e)

# Databricks connection
@st.cache_resource
def get_databricks_connection():
    try:
        return sql.connect(
            server_hostname=st.secrets.databricks.server_hostname,
            http_path=st.secrets.databricks.http_path,
            access_token=st.secrets.databricks.token
        )
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        return None

# Execute SQL query
def execute_query(query, schema_name):
    try:
        conn = get_databricks_connection()
        if not conn:
            return None, "Database connection failed"
        
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        
        # Convert to list of dicts
        data = [dict(zip(columns, row)) for row in results]
        return data, None
    except Exception as e:
        return None, str(e)

# Ollama AI agent
def ask_ollama(user_question, schema_name, model="llama3.2"):
    try:
        system_prompt = f"""You are an intelligent SQL assistant for the Hold Busters invoice analysis system.

{DATABASE_SCHEMA}

Your capabilities:
1. Answer questions about invoice data
2. Generate SQL queries when needed
3. Provide insights and analysis
4. Explain results in business terms

Guidelines:
- When writing SQL, use the schema: {schema_name}
- Always use proper SQL syntax for Databricks/Spark SQL
- For queries, return ONLY the SQL wrapped in ```sql blocks
- For analysis, provide clear, business-friendly explanations
- If you need to run a query, say so and provide the SQL
- Limit results to reasonable numbers (e.g., TOP 10, LIMIT 100)
- Be concise but informative

Current schema: {schema_name}
"""
        
        # Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in st.session_state.chat_history[-6:]:  # Last 6 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({
            "role": "user",
            "content": user_question
        })
        
        # Call Ollama
        response = ollama.chat(
            model=model,
            messages=messages
        )
        
        return response['message']['content']
        
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}\n\nMake sure Ollama is running and you have a model installed (ollama pull llama3.2)"

# Extract SQL from AI response
def extract_sql(text):
    # Look for SQL code blocks
    if "```sql" in text:
        start = text.find("```sql") + 6
        end = text.find("```", start)
        if end > start:
            return text[start:end].strip()
    
    # Try to find SELECT statements
    sql_pattern = r'(SELECT\s+.*?(?:FROM|;).*?)(?:\n\n|$)'
    matches = re.findall(sql_pattern, text, re.IGNORECASE | re.DOTALL)
    if matches:
        return matches[0].strip()
    
    return None

# Main app
def main():
    st.title("🔍 Hold Busters - Invoice Analysis with AI")
    st.markdown("### 🦙 Powered by Databricks + Ollama (Local & Free!)")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    schema_name = st.sidebar.text_input(
        "Schema Name",
        value="hackathon.hackathon_build_hold_busters"
    )
    
    # Check Ollama status
    ollama_status, ollama_info = check_ollama()
    
    st.sidebar.markdown("---")
    st.sidebar.header("🤖 AI Status")
    
    if ollama_status:
        st.sidebar.success("✅ Ollama is running!")
        
        # Model selector
        try:
            models = ollama.list()
            model_names = [m['name'] for m in models['models']]
            
            if model_names:
                selected_model = st.sidebar.selectbox(
                    "AI Model",
                    model_names,
                    index=0 if 'llama3.2' in str(model_names) else 0
                )
            else:
                st.sidebar.warning("⚠️ No models installed")
                st.sidebar.info("Run: ollama pull llama3.2")
                selected_model = "llama3.2"
        except:
            selected_model = "llama3.2"
            st.sidebar.info(f"Using: {selected_model}")
    else:
        st.sidebar.error("❌ Ollama not running")
        st.sidebar.info("Install from: ollama.com")
        selected_model = "llama3.2"
    
    # Check DB connection
    conn = get_databricks_connection()
    if not conn:
        st.error("❌ Not connected to Databricks")
        return
    
    st.success("✅ Connected to Databricks!")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 AI Chat Assistant", "📊 Dashboard", "📋 Data Explorer"])
    
    with tab1:
        st.subheader("🤖 Ask About Your Invoices")
        st.markdown("Ask questions in natural language. The AI will help you analyze invoice data!")
        
        if not ollama_status:
            st.warning("⚠️ Ollama is not running. Install it from https://ollama.com/ and run 'ollama pull llama3.2'")
        
        # Suggested questions
        with st.expander("💡 Suggested Questions"):
            suggestions = [
                "How many invoices are currently on hold?",
                "Which vendor has the most pending invoices?",
                "Show me invoices over $50,000 that are on hold",
                "What's the average days pending for held invoices?",
                "Which states have the most invoice holds?",
                "Show me the top 5 vendors by total invoice amount",
                "What are the most common hold reasons?",
                "Analyze invoice trends by state"
            ]
            for suggestion in suggestions:
                if st.button(suggestion, key=suggestion):
                    st.session_state.current_question = suggestion
        
        # Chat interface
        st.markdown("---")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><b>🦙 AI:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                
                # If there are query results, display them
                if "query_results" in msg:
                    with st.expander("📊 Query Results", expanded=True):
                        st.dataframe(msg["query_results"], use_container_width=True)
        
        # Chat input
        user_input = st.chat_input("Ask a question about your invoices...")
        
        # Handle suggestion button clicks
        if hasattr(st.session_state, 'current_question'):
            user_input = st.session_state.current_question
            del st.session_state.current_question
        
        if user_input:
            if not ollama_status:
                st.error("❌ Ollama is not running. Please start Ollama first.")
                return
            
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get AI response
            with st.spinner("🤔 AI is thinking..."):
                response = ask_ollama(user_input, schema_name, selected_model)
            
            # Check if response contains SQL
            sql_query = extract_sql(response)
            
            assistant_msg = {
                "role": "assistant",
                "content": response
            }
            
            if sql_query:
                # Execute the query
                with st.spinner("🔍 Executing query..."):
                    results, error = execute_query(sql_query, schema_name)
                
                if error:
                    assistant_msg["content"] += f"\n\n⚠️ Query execution error: {error}"
                elif results:
                    assistant_msg["query_results"] = results
                    assistant_msg["content"] += f"\n\n✅ Query executed successfully! Found {len(results)} results."
            
            # Add assistant response to history
            st.session_state.chat_history.append(assistant_msg)
            
            # Rerun to show new messages
            st.rerun()
        
        # Clear chat button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
    
    with tab2:
        st.subheader("📊 Invoice Overview")
        
        # Load summary data
        with st.spinner("Loading data..."):
            summary_query = f"""
            SELECT 
                COUNT(*) as total_invoices,
                SUM(CASE WHEN sitetracker__Status__c = 'Hold' THEN 1 ELSE 0 END) as on_hold,
                SUM(Total_Amount__c) as total_amount,
                AVG(Days_Pending_Approval__c) as avg_days_pending
            FROM {schema_name}.invoices
            """
            
            results, error = execute_query(summary_query, schema_name)
            
            if results and len(results) > 0:
                data = results[0]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Invoices", f"{data.get('total_invoices', 0):,}")
                
                with col2:
                    on_hold = data.get('on_hold', 0)
                    total = data.get('total_invoices', 1)
                    pct = (on_hold / total * 100) if total > 0 else 0
                    st.metric("On Hold", f"{on_hold:,}", f"{pct:.1f}%")
                
                with col3:
                    st.metric("Total Amount", f"${data.get('total_amount', 0):,.2f}")
                
                with col4:
                    st.metric("Avg Days Pending", f"{data.get('avg_days_pending', 0):.1f}")
            else:
                st.warning("No data available")
    
    with tab3:
        st.subheader("📋 Invoice Data Explorer")
        
        # Query builder
        st.markdown("**Quick Filters:**")
        col1, col2 = st.columns(2)
        
        with col1:
            status_filter = st.selectbox("Status", ["All", "Hold", "Approved", "Pending"])
        
        with col2:
            limit = st.number_input("Rows to display", min_value=10, max_value=1000, value=100, step=10)
        
        # Build query
        where_clause = ""
        if status_filter != "All":
            where_clause = f"WHERE sitetracker__Status__c = '{status_filter}'"
        
        query = f"""
        SELECT 
            Invoice_Name,
            Vendor__Name,
            Invoice_Date__c,
            Total_Amount__c,
            sitetracker__Status__c as Status,
            Days_Pending_Approval__c,
            State__c
        FROM {schema_name}.invoices
        {where_clause}
        ORDER BY Invoice_Date__c DESC
        LIMIT {limit}
        """
        
        if st.button("🔍 Load Data"):
            with st.spinner("Loading..."):
                results, error = execute_query(query, schema_name)
                
                if error:
                    st.error(f"Error: {error}")
                elif results:
                    st.success(f"✅ Loaded {len(results)} invoices")
                    st.dataframe(results, use_container_width=True, height=400)
                    
                    # Download button
                    json_str = json.dumps(results, indent=2, default=str)
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json_str,
                        file_name=f"invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

