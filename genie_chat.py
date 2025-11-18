"""
Databricks Genie Chat Module
Reusable Genie AI chat functionality with persistent feedback memory
"""
import streamlit as st
from databricks.sdk import WorkspaceClient
import json
from datetime import datetime
import time
from pathlib import Path

# Persistent feedback file
FEEDBACK_FILE = Path(".genie_feedback_memory.json")


# ============================================================================
# Databricks Client
# ============================================================================

def get_databricks_client():
    """Get authenticated Databricks workspace client"""
    try:
        # Try to use default authentication (works in Databricks Apps and with configured CLI)
        client = WorkspaceClient()
        return client
    except Exception as e:
        st.error(f"❌ Could not connect to Databricks: {str(e)}")
        st.info("""
        **Setup Required:**
        
        Make sure you have Databricks CLI configured:
        ```
        databricks configure --token
        ```
        
        Or set environment variables:
        - `DATABRICKS_HOST`
        - `DATABRICKS_TOKEN`
        """)
        return None


# ============================================================================
# Feedback Memory Management
# ============================================================================

def load_feedback_memory():
    """Load feedback memory from persistent file"""
    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_feedback_memory(feedback_list):
    """Save feedback memory to file"""
    try:
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        return True
    except Exception as e:
        st.error(f"⚠️ Could not save feedback memory: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False


def add_feedback_to_memory(feedback_text, question, genie_response):
    """Add new feedback to persistent memory"""
    memory = load_feedback_memory()
    
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question[:100],  # Truncate for storage
        "genie_response": genie_response[:200],  # Truncate for storage
        "feedback": feedback_text,
        "correction": f"When asked '{question[:100]}', remember: {feedback_text}"
    }
    
    memory.append(feedback_entry)
    
    # Keep only last 50 feedback entries
    if len(memory) > 50:
        memory = memory[-50:]
    
    success = save_feedback_memory(memory)
    return memory, success


def get_feedback_context():
    """Get feedback context to inject into new conversations"""
    memory = load_feedback_memory()
    if not memory:
        return ""
    
    # Use last 10 feedback items
    recent_feedback = memory[-10:]
    
    context = "\n\n📝 IMPORTANT: Learn from these previous corrections:\n"
    for idx, item in enumerate(recent_feedback, 1):
        context += f"{idx}. {item['correction']}\n"
    
    return context


def clear_feedback_memory():
    """Clear all saved feedback"""
    try:
        if FEEDBACK_FILE.exists():
            FEEDBACK_FILE.unlink()
        return True
    except Exception as e:
        st.error(f"Could not clear feedback: {str(e)}")
        return False


# ============================================================================
# Genie Chat Interface
# ============================================================================

def ask_genie(user_question, genie_space_id):
    """
    Ask Databricks Genie a question
    
    Args:
        user_question (str): The question to ask
        genie_space_id (str): The Genie Space ID
        
    Returns:
        tuple: (response_dict, error_message)
            response_dict contains: text, sql, genie_result, conversation_id, message_id
            error_message is None if successful
    """
    try:
        client = get_databricks_client()
        if not client:
            return None, "Error: Could not connect to Databricks workspace"
        
        # Start a new conversation or continue existing one
        if not st.session_state.genie_conversation_id:
            # Create new conversation with feedback context
            feedback_context = get_feedback_context()
            
            # Inject feedback context into first question
            enhanced_question = user_question
            feedback_applied = False
            if feedback_context:
                enhanced_question = f"{user_question}{feedback_context}"
                feedback_applied = True
            
            response = client.genie.start_conversation(
                space_id=genie_space_id,
                content=enhanced_question
            )
            st.session_state.genie_conversation_id = response.conversation_id
            st.session_state.genie_message_id = response.message_id
            st.session_state.feedback_applied = feedback_applied
        else:
            # Continue existing conversation
            response = client.genie.create_message(
                space_id=genie_space_id,
                conversation_id=st.session_state.genie_conversation_id,
                content=user_question
            )
            st.session_state.genie_message_id = response.message_id
        
        # Wait for response (poll for completion)
        max_attempts = 120  # 120 seconds for complex queries
        attempt = 0
        
        # Show simple progress indicator
        progress_placeholder = st.empty()
        progress_placeholder.info("⏳ Genie is thinking...")
        
        while attempt < max_attempts:
            try:
                message = client.genie.get_message(
                    space_id=genie_space_id,
                    conversation_id=st.session_state.genie_conversation_id,
                    message_id=st.session_state.genie_message_id
                )
            except Exception as poll_error:
                # Log polling error but continue retrying (silently)
                time.sleep(1)
                attempt += 1
                continue
            
            # Convert status to string for comparison (handles both string and enum)
            status_str = str(message.status).split('.')[-1]  # Extract "COMPLETED" from "MessageStatus.COMPLETED"
            
            if status_str == "COMPLETED":
                progress_placeholder.empty()  # Clear progress message
                
                # Extract response content
                response_text = ""
                sql_query = None
                query_result = None
                
                # Get attachments (SQL queries, results)
                if hasattr(message, 'attachments') and message.attachments:
                    for attachment in message.attachments:
                        if hasattr(attachment, 'query') and attachment.query:
                            if hasattr(attachment.query, 'query'):
                                sql_query = attachment.query.query
                            if hasattr(attachment.query, 'result') and attachment.query.result:
                                # Genie includes query results
                                query_result = attachment.query.result
                
                # Get text content
                if hasattr(message, 'content') and message.content:
                    response_text = message.content
                
                return {
                    "text": response_text or "Response received (no text content)",
                    "sql": sql_query,
                    "genie_result": query_result,
                    "conversation_id": st.session_state.genie_conversation_id,
                    "message_id": st.session_state.genie_message_id
                }, None
            
            elif status_str == "FAILED":
                progress_placeholder.empty()
                error_msg = "Genie query failed"
                if hasattr(message, 'error') and message.error:
                    error_msg = f"Genie error: {message.error}"
                return None, error_msg
            
            elif status_str in ["CANCELLED", "TIMEOUT"]:
                progress_placeholder.empty()
                return None, f"Genie request {status_str.lower()}"
            
            # Still processing, wait and retry
            time.sleep(1)
            attempt += 1
        
        # Timeout reached
        progress_placeholder.empty()
        return None, f"""⏱️ Timeout after {max_attempts} seconds.

This can happen if:
- Very complex query requiring extensive data analysis
- Network connectivity issues
- Genie Space initialization problems

Suggestions:
1. Try a simpler question
2. Check Genie Space status in Databricks UI
3. Try again in a moment"""
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "space" in error_msg.lower() and "not found" in error_msg.lower():
            return None, f"""Error: Genie Space not found.

Please check your Genie Space ID in .streamlit/secrets.toml

To find your Genie Space ID:
1. Go to Databricks workspace
2. Navigate to Genie Spaces
3. Select your space
4. Copy the space ID from the URL or settings"""
        
        return None, f"Error communicating with Genie: {error_msg}"


def reset_genie_conversation():
    """Reset the Genie conversation to start fresh"""
    st.session_state.genie_conversation_id = None
    st.session_state.genie_message_id = None


# ============================================================================
# Session State Initialization
# ============================================================================

def initialize_genie_session_state():
    """Initialize session state variables for Genie chat"""
    if "genie_conversation_id" not in st.session_state:
        st.session_state.genie_conversation_id = None
    if "genie_message_id" not in st.session_state:
        st.session_state.genie_message_id = None
    if "feedback_memory" not in st.session_state:
        st.session_state.feedback_memory = load_feedback_memory()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

