"""
Hold Busters Dashboard with Claude AI Chat Agent
"""
import streamlit as st
from databricks import sql
import anthropic
import json
from datetime import datetime

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

# Database schema for Claude
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
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None
if 'feedback_mode' not in st.session_state:
    st.session_state.feedback_mode = {}
if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0

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

# Claude AI agent
def ask_claude(user_question, schema_name):
    try:
        client = anthropic.Anthropic(api_key=st.secrets.anthropic.api_key)
        
        system_prompt = f"""You are an intelligent business analyst assistant for the Hold Busters invoice analysis system.

{DATABASE_SCHEMA}

RESPONSE FORMAT:
1. Start with a clear, business-friendly answer or explanation
2. Then provide the SQL query wrapped in ```sql blocks
3. Keep explanations concise and non-technical for business users

Example response:
"To answer your question, we need to count invoices with 'Hold' status. Let me run a query to get that information.

```sql
SELECT COUNT(*) FROM {schema_name}.invoices WHERE sitetracker__Status__c = 'Hold'
```

This will give us the total number of invoices currently on hold."

CRITICAL SQL RULES:
1. ALL table references MUST include the full schema path: {schema_name}
2. NEVER use just the table name (e.g., "invoices")
3. ALWAYS use the full path (e.g., "{schema_name}.invoices")

Examples of CORRECT SQL:
- SELECT COUNT(*) FROM {schema_name}.invoices WHERE sitetracker__Status__c = 'Hold'
- SELECT * FROM {schema_name}.invoice_lines WHERE Invoice_Amount__c > 1000
- SELECT * FROM {schema_name}.projects WHERE Infinium_Status__c = 'Active'

Query Guidelines:
- ALWAYS prefix tables with: {schema_name}.
- Use proper Databricks/Spark SQL syntax
- Limit results to reasonable numbers (LIMIT 100 by default)
- Focus on clarity and business value

LEARNING FROM FEEDBACK:
- When you receive feedback (marked with ⚠️ FEEDBACK), acknowledge it and adjust your approach
- Learn from any mistakes pointed out in the feedback
- Apply the corrections to all future responses in this conversation
- If SQL was wrong, explain what you'll do differently next time

Current schema: {schema_name}
"""
        
        # Build conversation history
        messages = []
        for msg in st.session_state.chat_history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({
            "role": "user",
            "content": user_question
        })
        
        # Try models in order of preference
        models_to_try = [
            "claude-3-5-sonnet-20240620",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
        
        response = None
        for model in models_to_try:
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=2000,
                    system=system_prompt,
                    messages=messages
                )
                break  # Success! Use this model
            except anthropic.NotFoundError:
                continue  # Try next model
        
        if not response:
            return "Error: No available Claude models found. Please check your Anthropic account access."
        
        return response.content[0].text
        
    except Exception as e:
        return f"Error communicating with Claude: {str(e)}"

# Extract SQL from Claude's response
def extract_sql(text):
    if "```sql" in text:
        start = text.find("```sql") + 6
        end = text.find("```", start)
        return text[start:end].strip()
    return None

# Main app
def main():
    st.title("🔍 Hold Busters - Invoice Analysis with AI")
    st.markdown("### Powered by Databricks + Claude AI")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    schema_name = st.sidebar.text_input(
        "Schema Name",
        value="hackathon.hackathon_build_hold_busters"
    )
    
    # Check connections
    conn = get_databricks_connection()
    if not conn:
        st.error("❌ Not connected to Databricks")
        return
    
    st.success("✅ Connected to Databricks!")
    
    # Check Claude API key
    if not st.secrets.get("anthropic", {}).get("api_key") or st.secrets.anthropic.api_key == "YOUR_ANTHROPIC_API_KEY_HERE":
        st.warning("⚠️ Anthropic API key not configured. Chat agent will not work.")
        st.info("Add your API key to `.streamlit/secrets.toml`")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 AI Chat Assistant", "📊 Dashboard", "📋 Data Explorer"])
    
    with tab1:
        st.subheader("🤖 Ask Claude About Your Invoices")
        st.markdown("Ask questions in natural language. Claude will help you analyze invoice data!")
        
        # Suggested questions
        with st.expander("💡 Suggested Questions"):
            suggestions = [
                "How many invoices are currently on hold?",
                "Which vendor has the most pending invoices?",
                "Show me invoices over $50,000 that are on hold",
                "What's the average days pending for held invoices?",
                "Which states have the most invoice holds?",
                "Show me the top 5 vendors by total invoice amount",
                "How many invoices were approved last month?",
                "What are the most common hold reasons?"
            ]
            for suggestion in suggestions:
                if st.button(suggestion, key=suggestion):
                    st.session_state.current_question = suggestion
        
        # Chat interface
        st.markdown("---")
        
        # Display chat history
        for idx, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                # Get message ID for tracking
                msg_id = msg.get("message_id", idx)
                
                # Extract SQL from response if present
                response_text = msg["content"]
                sql_query = None
                
                if "```sql" in response_text:
                    # Split the response to separate explanation from SQL
                    sql_start = response_text.find("```sql")
                    sql_end = response_text.find("```", sql_start + 6) + 3
                    
                    sql_query = response_text[sql_start:sql_end]
                    
                    # Get text before and after SQL
                    before_sql = response_text[:sql_start].strip()
                    after_sql = response_text[sql_end:].strip()
                    
                    # Combine explanation without SQL
                    explanation = (before_sql + "\n\n" + after_sql).strip()
                else:
                    explanation = response_text
                
                # Display explanation (without SQL)
                st.markdown(f'<div class="chat-message assistant-message"><b>Claude:</b> {explanation}</div>', unsafe_allow_html=True)
                
                # Show SQL query in expander (hidden by default)
                if sql_query:
                    with st.expander("🔍 View SQL Query", expanded=False):
                        st.code(sql_query.replace("```sql", "").replace("```", "").strip(), language="sql")
                
                # If there are query results, display them
                if "query_results" in msg:
                    with st.expander("📊 Query Results", expanded=True):
                        st.dataframe(msg["query_results"], use_container_width=True)
                
                # Feedback section
                feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 8])
                
                with feedback_col1:
                    if st.button("👍", key=f"thumbs_up_{msg_id}", help="This response was helpful"):
                        st.success("✅ Thanks for the positive feedback!")
                
                with feedback_col2:
                    if st.button("👎", key=f"thumbs_down_{msg_id}", help="This response needs improvement"):
                        st.session_state.feedback_mode[msg_id] = True
                        st.rerun()
                
                # Show feedback form if user clicked thumbs down
                if st.session_state.feedback_mode.get(msg_id, False):
                    st.markdown("---")
                    st.markdown("**📝 Help Claude Improve:**")
                    
                    feedback_text = st.text_area(
                        "What was wrong with this response?",
                        key=f"feedback_text_{msg_id}",
                        placeholder="Example: The SQL query didn't include the schema name, or the wrong table was used, etc.",
                        height=100
                    )
                    
                    col_submit, col_cancel = st.columns([1, 4])
                    
                    with col_submit:
                        if st.button("Submit Feedback", key=f"submit_feedback_{msg_id}"):
                            if feedback_text:
                                # Add feedback as a user message
                                feedback_message = f"⚠️ FEEDBACK ON PREVIOUS RESPONSE: {feedback_text}\n\nPlease acknowledge this feedback and adjust your future responses accordingly."
                                
                                st.session_state.chat_history.append({
                                    "role": "user",
                                    "content": feedback_message,
                                    "is_feedback": True
                                })
                                
                                # Get Claude's acknowledgment
                                with st.spinner("🤔 Claude is learning from your feedback..."):
                                    response = ask_claude(feedback_message, schema_name)
                                
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": response,
                                    "message_id": st.session_state.message_counter
                                })
                                st.session_state.message_counter += 1
                                
                                # Clear feedback mode
                                st.session_state.feedback_mode[msg_id] = False
                                st.success("✅ Feedback submitted! Claude will improve.")
                                st.rerun()
                            else:
                                st.warning("Please provide feedback before submitting.")
                    
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_feedback_{msg_id}"):
                            st.session_state.feedback_mode[msg_id] = False
                            st.rerun()
                
                st.markdown("---")
        
        # Chat input
        user_input = st.chat_input("Ask a question about your invoices...")
        
        # Handle suggestion button clicks
        if hasattr(st.session_state, 'current_question'):
            user_input = st.session_state.current_question
            del st.session_state.current_question
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get Claude's response
            with st.spinner("🤔 Claude is thinking..."):
                response = ask_claude(user_input, schema_name)
            
            # Check if response contains SQL
            sql_query = extract_sql(response)
            
            assistant_msg = {
                "role": "assistant",
                "content": response,
                "message_id": st.session_state.message_counter
            }
            st.session_state.message_counter += 1
            
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
        if st.button("🗑️ Clear Chat History"):
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
                    import json
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

