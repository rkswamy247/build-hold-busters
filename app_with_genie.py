"""
Hold Busters Dashboard with Databricks Genie AI Agent
"""
import streamlit as st
from databricks import sql
import json
from datetime import datetime
import time
import os
from pathlib import Path

# Import Genie chat module
import genie_chat

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

# Initialize Genie session state
genie_chat.initialize_genie_session_state()

# Initialize other session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None
if 'feedback_mode' not in st.session_state:
    st.session_state.feedback_mode = {}
if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0

# Databricks SQL connection
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

# Extract SQL from response
def extract_sql_from_genie(genie_response):
    """Extract SQL from Genie response"""
    if genie_response and "sql" in genie_response:
        return genie_response["sql"]
    return None

# Main app
def main():
    st.title("🔍 Hold Busters - Invoice Analysis with Genie AI")
    st.markdown("### Powered by Databricks + Genie")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    schema_name = st.sidebar.text_input(
        "Schema Name",
        value="hackathon.hackathon_build_hold_busters"
    )
    
    # Genie Space ID configuration
    genie_space_id = st.secrets.get("databricks", {}).get("genie_space_id", "")
    
    if not genie_space_id:
        st.sidebar.error("⚠️ Genie Space ID not configured!")
        st.sidebar.info("Add to .streamlit/secrets.toml:\n\n[databricks]\ngenie_space_id = \"YOUR_SPACE_ID\"")
    else:
        st.sidebar.success(f"✅ Genie Space: {genie_space_id[:8]}...")
    
    # Show feedback memory
    st.sidebar.markdown("---")
    st.sidebar.subheader("📝 Feedback Memory")
    
    feedback_memory = genie_chat.load_feedback_memory()
    if feedback_memory:
        st.sidebar.success(f"💾 {len(feedback_memory)} corrections saved")
        
        with st.sidebar.expander("View Saved Feedback"):
            recent = feedback_memory[-5:]  # Show last 5
            for item in reversed(recent):
                st.markdown(f"**Q:** {item['question'][:50]}...")
                st.markdown(f"**Feedback:** {item['feedback']}")
                st.markdown(f"*{item['timestamp'][:10]}*")
                st.markdown("---")
        
        if st.sidebar.button("🗑️ Clear All Feedback"):
            if genie_chat.clear_feedback_memory():
                st.session_state.feedback_memory = []
                st.sidebar.success("Cleared!")
                st.rerun()
            else:
                st.sidebar.error("Failed to clear feedback")
    else:
        st.sidebar.info("No feedback saved yet. Use 👎 to provide feedback!")
    
    # Check connections
    conn = get_databricks_connection()
    if not conn:
        st.error("❌ Not connected to Databricks")
        return
    
    st.success("✅ Connected to Databricks!")
    
    # Check Databricks Genie client
    client = genie_chat.get_databricks_client()
    if not client:
        st.warning("⚠️ Databricks client not available")
    
    if not genie_space_id:
        st.error("❌ Genie Space ID required. Please configure in secrets.toml")
        st.info("""
        **How to find your Genie Space ID:**
        1. Go to Databricks Console
        2. Navigate to **AI/BI** → **Genie Spaces**
        3. Open your Genie Space
        4. Look in the URL: `/genie/spaces/<SPACE_ID>`
        5. Add to `.streamlit/secrets.toml`:
        
        ```toml
        [databricks]
        genie_space_id = "YOUR_SPACE_ID"
        ```
        """)
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Genie AI Assistant", "📊 Dashboard", "📋 Data Explorer"])
    
    with tab1:
        st.subheader("🧞 Ask Genie About Your Invoices")
        st.markdown("**Powered by Databricks Genie** - AI that understands your data!")
        st.markdown("Genie already knows your schema and table structure. Just ask questions naturally!")
        
        # Show feedback status for first question
        feedback_memory = genie_chat.load_feedback_memory()
        if feedback_memory and not st.session_state.genie_conversation_id:
            st.info(f"📝 **{len(feedback_memory)} saved corrections** will be applied to this conversation")
        
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
        
        # Conversation controls
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔄 New Conversation"):
                genie_chat.reset_genie_conversation()
                st.session_state.chat_history = []
                
                # Show feedback memory status
                feedback_count = len(genie_chat.load_feedback_memory())
                if feedback_count > 0:
                    st.success(f"Started new conversation! (📝 {feedback_count} saved corrections will be applied)")
                else:
                    st.success("Started new conversation!")
                st.rerun()
        
        # Chat interface
        st.markdown("---")
        
        # Display chat history
        for idx, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                # Skip feedback messages in display
                if msg.get("is_feedback"):
                    st.markdown(f'<div class="chat-message user-message"><b>📝 Feedback:</b> {msg["content"].replace("⚠️ FEEDBACK ON PREVIOUS RESPONSE: ", "").split("Please acknowledge")[0].strip()}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message user-message"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                # Get message ID for tracking
                msg_id = msg.get("message_id", idx)
                
                # Extract text response
                response_text = msg.get("content", "")
                
                # Display explanation
                st.markdown(f'<div class="chat-message assistant-message"><b>Genie:</b> {response_text}</div>', unsafe_allow_html=True)
                
                # Show SQL query in expander (hidden by default)
                if msg.get("sql_query"):
                    with st.expander("🔍 View SQL Query", expanded=False):
                        st.code(msg["sql_query"], language="sql")
                
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
                    st.markdown("**📝 Help Genie Improve:**")
                    
                    feedback_text = st.text_area(
                        "What was wrong with this response?",
                        key=f"feedback_text_{msg_id}",
                        placeholder="Example: The SQL query didn't give the right results, or the interpretation was incorrect.",
                        height=100
                    )
                    
                    col_submit, col_cancel = st.columns([1, 4])
                    
                    with col_submit:
                        if st.button("Submit Feedback", key=f"submit_feedback_{msg_id}"):
                            if feedback_text:
                                # Find the original question for this response
                                original_question = "Unknown question"
                                for i in range(idx - 1, -1, -1):
                                    if st.session_state.chat_history[i]["role"] == "user":
                                        original_question = st.session_state.chat_history[i]["content"]
                                        break
                                
                                # Save feedback to persistent memory
                                memory, success = genie_chat.add_feedback_to_memory(
                                    feedback_text=feedback_text,
                                    question=original_question,
                                    genie_response=response_text
                                )
                                
                                if not success:
                                    st.error("❌ Failed to save feedback to memory file!")
                                    st.info(f"Attempted to save to: {FEEDBACK_FILE.absolute()}")
                                else:
                                    st.info(f"💾 Feedback #{len(memory)} saved to: {FEEDBACK_FILE.name}")
                                
                                # Update session state
                                st.session_state.feedback_memory = load_feedback_memory()
                                
                                # Add feedback as a user message
                                feedback_message = f"That answer wasn't quite right. {feedback_text}. Can you try again?"
                                
                                st.session_state.chat_history.append({
                                    "role": "user",
                                    "content": feedback_message,
                                    "is_feedback": True
                                })
                                
                                # Get Genie's improved response
                                with st.spinner("🧞 Genie is learning from your feedback..."):
                                    response, error = genie_chat.ask_genie(feedback_message, genie_space_id)
                                
                                if error:
                                    st.error(f"Error: {error}")
                                else:
                                    st.session_state.chat_history.append({
                                        "role": "assistant",
                                        "content": response["text"],
                                        "sql_query": response.get("sql"),
                                        "message_id": st.session_state.message_counter
                                    })
                                    st.session_state.message_counter += 1
                                
                                # Clear feedback mode
                                st.session_state.feedback_mode[msg_id] = False
                                st.success("✅ Feedback saved! Genie will remember this in future conversations.")
                                st.rerun()
                            else:
                                st.warning("Please provide feedback before submitting.")
                    
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_feedback_{msg_id}"):
                            st.session_state.feedback_mode[msg_id] = False
                            st.rerun()
                
                st.markdown("---")
        
        # Chat input
        user_input = st.chat_input("Ask Genie about your invoices...")
        
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
            
            # Get Genie's response
            with st.spinner("🧞 Genie is analyzing your data..."):
                genie_response, error = genie_chat.ask_genie(user_input, genie_space_id)
            
            if error:
                # Add error to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"⚠️ {error}",
                    "message_id": st.session_state.message_counter
                })
                st.session_state.message_counter += 1
            else:
                # Extract SQL and text
                sql_query = genie_response.get("sql")
                response_text = genie_response.get("text", "")
                
                assistant_msg = {
                    "role": "assistant",
                    "content": response_text,
                    "sql_query": sql_query,
                    "message_id": st.session_state.message_counter
                }
                st.session_state.message_counter += 1
                
                # If Genie generated SQL, execute it to get results
                if sql_query:
                    with st.spinner("🔍 Executing query..."):
                        results, exec_error = execute_query(sql_query, schema_name)
                    
                    if exec_error:
                        assistant_msg["content"] += f"\n\n⚠️ Query execution error: {exec_error}"
                    elif results:
                        assistant_msg["query_results"] = results
                        assistant_msg["content"] += f"\n\n✅ Found {len(results)} results."
                
                # Add assistant response to history
                st.session_state.chat_history.append(assistant_msg)
            
            # Rerun to show new messages
            st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            genie_chat.reset_genie_conversation()
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

