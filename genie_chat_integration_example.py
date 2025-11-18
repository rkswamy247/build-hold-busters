"""
Example: How to integrate Genie Chat into app_databricks.py
"""
import streamlit as st
import genie_chat

# ============================================================================
# 1. Initialize Genie Session State (add at the top of your app)
# ============================================================================

# Initialize Genie (do this before creating your UI)
genie_chat.initialize_genie_session_state()

# ============================================================================
# 2. Add Genie Chat Tab (add to your existing tabs)
# ============================================================================

def add_genie_chat_tab():
    """Add a Genie AI chat tab to your dashboard"""
    st.subheader("🧞 Ask Genie About Your Data")
    st.markdown("**Powered by Databricks Genie** - AI that understands your data schema!")
    
    # Get Genie Space ID from secrets
    genie_space_id = st.secrets.databricks.get("genie_space_id")
    
    if not genie_space_id:
        st.error("""
        **Genie Space ID not configured!**
        
        Add to `.streamlit/secrets.toml`:
        ```
        [databricks]
        genie_space_id = "YOUR_GENIE_SPACE_ID"
        ```
        
        To find your Genie Space ID, run:
        ```
        python find_genie_space_id.py
        ```
        """)
        return
    
    # Conversation controls
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 New Conversation"):
            genie_chat.reset_genie_conversation()
            st.session_state.chat_history = []
            
            # Show feedback status
            feedback_count = len(genie_chat.load_feedback_memory())
            if feedback_count > 0:
                st.success(f"Started new conversation! ({feedback_count} corrections applied)")
            else:
                st.success("Started new conversation!")
            st.rerun()
    
    # Chat interface
    user_input = st.text_input(
        "Ask a question about your data:",
        placeholder="Example: What are the top 5 vendors by invoice count?",
        key="genie_user_input"
    )
    
    if st.button("Send", key="genie_send"):
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get Genie's response
            with st.spinner("🧞 Genie is analyzing..."):
                genie_response, error = genie_chat.ask_genie(user_input, genie_space_id)
            
            if error:
                st.error(f"Genie: {error}")
            else:
                # Add assistant message
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": genie_response["text"],
                    "sql": genie_response.get("sql"),
                    "genie_result": genie_response.get("genie_result")
                })
            
            st.rerun()
    
    # Display chat history
    for idx, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Genie:** {message['content']}")
            
            # Show SQL if available
            if "sql" in message and message["sql"]:
                with st.expander("📝 View SQL"):
                    st.code(message["sql"], language="sql")
            
            # Feedback buttons
            col1, col2 = st.columns([1, 10])
            with col1:
                if st.button("👍", key=f"thumbs_up_{idx}"):
                    st.success("Thanks for the feedback!")
            with col2:
                if st.button("👎", key=f"thumbs_down_{idx}"):
                    st.session_state[f"feedback_mode_{idx}"] = True
                    st.rerun()
            
            # Feedback form
            if st.session_state.get(f"feedback_mode_{idx}"):
                feedback_text = st.text_area(
                    "What should Genie do better?",
                    key=f"feedback_text_{idx}"
                )
                if st.button("Submit Feedback", key=f"submit_feedback_{idx}"):
                    if feedback_text:
                        # Save feedback
                        memory, success = genie_chat.add_feedback_to_memory(
                            feedback_text=feedback_text,
                            question=st.session_state.chat_history[idx-1]["content"],
                            genie_response=message["content"]
                        )
                        
                        if success:
                            st.session_state.feedback_memory = genie_chat.load_feedback_memory()
                            st.success(f"✅ Feedback saved! ({len(memory)} corrections total)")
                            st.session_state[f"feedback_mode_{idx}"] = False
                            st.rerun()


# ============================================================================
# 3. Add Feedback Memory Sidebar (add to your sidebar)
# ============================================================================

def add_feedback_sidebar():
    """Add feedback memory info to sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📝 Feedback Memory")
    
    feedback_memory = genie_chat.load_feedback_memory()
    
    if feedback_memory:
        st.sidebar.write(f"💾 {len(feedback_memory)} corrections saved")
        
        with st.sidebar.expander("View Saved Feedback"):
            for idx, item in enumerate(reversed(feedback_memory[-5:]), 1):  # Show last 5
                st.markdown(f"**{idx}. {item['question'][:50]}...**")
                st.markdown(f"*{item['feedback']}*")
                st.markdown("---")
        
        if st.sidebar.button("🗑️ Clear All Feedback"):
            if genie_chat.clear_feedback_memory():
                st.session_state.feedback_memory = []
                st.sidebar.success("Cleared!")
                st.rerun()
    else:
        st.sidebar.info("No feedback saved yet")


# ============================================================================
# 4. Example: Full Integration into app_databricks.py
# ============================================================================

def main():
    st.set_page_config(
        page_title="Hold Busters Dashboard",
        layout="wide"
    )
    
    # Initialize Genie
    genie_chat.initialize_genie_session_state()
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar
    st.sidebar.title("Hold Busters")
    add_feedback_sidebar()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🧞 Genie AI", "📊 Dashboard", "📋 Data"])
    
    with tab1:
        add_genie_chat_tab()
    
    with tab2:
        st.header("📊 Invoice Dashboard")
        # Your existing dashboard code here
    
    with tab3:
        st.header("📋 Data Explorer")
        # Your existing data explorer code here


if __name__ == "__main__":
    main()

