# 🧞 Genie Chat Module

**Reusable Databricks Genie AI chat functionality with persistent feedback memory**

---

## 📦 What's Included

The `genie_chat.py` module provides:

1. **Databricks Client Management** - Authenticated connection to Databricks
2. **Genie AI Interface** - Ask questions, get responses with SQL
3. **Persistent Feedback Memory** - Train Genie across sessions
4. **Session State Management** - Conversation and chat history handling
5. **Error Handling** - Robust error messages and recovery

---

## 🚀 Quick Start

### **1. Import the Module**

```python
import streamlit as st
import genie_chat
```

### **2. Initialize Session State**

```python
# Do this at the top of your app
genie_chat.initialize_genie_session_state()
```

### **3. Ask Genie a Question**

```python
# Get Genie Space ID from secrets
genie_space_id = st.secrets.databricks.genie_space_id

# Ask a question
response, error = genie_chat.ask_genie(
    user_question="How many invoices are on hold?",
    genie_space_id=genie_space_id
)

if error:
    st.error(f"Error: {error}")
else:
    st.write(response["text"])        # Genie's response
    st.code(response["sql"])           # Generated SQL
    # response["genie_result"]         # Query results (if available)
```

---

## 📚 API Reference

### **Core Functions**

#### `initialize_genie_session_state()`
Initialize required session state variables.

```python
genie_chat.initialize_genie_session_state()
```

Initializes:
- `genie_conversation_id`
- `genie_message_id`  
- `feedback_memory`
- `chat_history`

---

#### `ask_genie(user_question, genie_space_id)`
Ask Databricks Genie a question.

**Parameters:**
- `user_question` (str): The question to ask
- `genie_space_id` (str): Your Genie Space ID

**Returns:**
- `(response_dict, None)` on success
- `(None, error_message)` on failure

**Response Dict:**
```python
{
    "text": "Genie's response text",
    "sql": "SELECT ... generated SQL",
    "genie_result": {...},  # Query results (if available)
    "conversation_id": "...",
    "message_id": "..."
}
```

**Example:**
```python
response, error = genie_chat.ask_genie(
    "What are the top 5 vendors?",
    "YOUR_GENIE_SPACE_ID"
)

if not error:
    st.write(response["text"])
    if response["sql"]:
        st.code(response["sql"], language="sql")
```

---

#### `reset_genie_conversation()`
Reset conversation to start fresh.

```python
genie_chat.reset_genie_conversation()
```

Use when clicking "New Conversation" button.

---

### **Feedback Memory Functions**

#### `load_feedback_memory()`
Load saved feedback corrections.

```python
feedback_list = genie_chat.load_feedback_memory()
# Returns: List of feedback dictionaries
```

---

#### `add_feedback_to_memory(feedback_text, question, genie_response)`
Save user feedback for future sessions.

**Parameters:**
- `feedback_text` (str): What should be corrected
- `question` (str): Original question asked
- `genie_response` (str): Genie's response that needs correction

**Returns:**
- `(updated_memory, True)` on success
- `(updated_memory, False)` on failure

**Example:**
```python
memory, success = genie_chat.add_feedback_to_memory(
    feedback_text="Always use full schema path: hackathon.table_name",
    question="How many invoices?",
    genie_response="SELECT COUNT(*) FROM invoices"
)

if success:
    st.success(f"Saved! {len(memory)} corrections total")
```

---

#### `clear_feedback_memory()`
Clear all saved feedback.

```python
if genie_chat.clear_feedback_memory():
    st.success("Feedback cleared!")
```

---

### **Utility Functions**

#### `get_feedback_context()`
Get feedback context string to inject into conversations.

```python
context = genie_chat.get_feedback_context()
# Returns string with last 10 corrections
```

This is called automatically by `ask_genie()` for new conversations.

---

#### `get_databricks_client()`
Get authenticated Databricks workspace client.

```python
client = genie_chat.get_databricks_client()
if client:
    # Use client.genie methods
```

---

## 🎯 Integration Examples

### **Example 1: Minimal Integration**

```python
import streamlit as st
import genie_chat

# Initialize
genie_chat.initialize_genie_session_state()

st.title("My Dashboard")

# User input
question = st.text_input("Ask Genie:")

if st.button("Send"):
    response, error = genie_chat.ask_genie(
        question,
        st.secrets.databricks.genie_space_id
    )
    
    if error:
        st.error(error)
    else:
        st.write(response["text"])
```

---

### **Example 2: With Chat History**

```python
import streamlit as st
import genie_chat

genie_chat.initialize_genie_session_state()

st.title("Genie Chat")

# Display chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Genie:** {msg['content']}")
        if "sql" in msg:
            st.code(msg["sql"], language="sql")

# User input
question = st.text_input("Your question:")

if st.button("Send") and question:
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    
    # Get Genie response
    response, error = genie_chat.ask_genie(
        question,
        st.secrets.databricks.genie_space_id
    )
    
    if not error:
        # Add assistant message
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["text"],
            "sql": response["sql"]
        })
    
    st.rerun()
```

---

### **Example 3: With Feedback**

```python
import streamlit as st
import genie_chat

genie_chat.initialize_genie_session_state()

# ... display chat ...

# For each assistant message
for idx, msg in enumerate(st.session_state.chat_history):
    if msg["role"] == "assistant":
        st.write(msg["content"])
        
        # Feedback button
        if st.button("👎 Provide Feedback", key=f"feedback_{idx}"):
            st.session_state[f"show_feedback_{idx}"] = True
        
        # Feedback form
        if st.session_state.get(f"show_feedback_{idx}"):
            feedback = st.text_area("What should improve?", key=f"fb_text_{idx}")
            
            if st.button("Submit", key=f"submit_{idx}"):
                # Get original question
                question = st.session_state.chat_history[idx-1]["content"]
                
                # Save feedback
                memory, success = genie_chat.add_feedback_to_memory(
                    feedback,
                    question,
                    msg["content"]
                )
                
                if success:
                    st.success(f"Saved! {len(memory)} total corrections")
                    st.session_state[f"show_feedback_{idx}"] = False
                    st.rerun()
```

---

### **Example 4: Sidebar Feedback Display**

```python
import streamlit as st
import genie_chat

# Sidebar
st.sidebar.title("Feedback Memory")

feedback_memory = genie_chat.load_feedback_memory()

if feedback_memory:
    st.sidebar.write(f"💾 {len(feedback_memory)} corrections saved")
    
    with st.sidebar.expander("View Corrections"):
        for item in feedback_memory[-5:]:  # Last 5
            st.markdown(f"**Q:** {item['question'][:50]}...")
            st.markdown(f"**Fix:** {item['feedback']}")
            st.markdown("---")
    
    if st.sidebar.button("Clear All"):
        genie_chat.clear_feedback_memory()
        st.rerun()
else:
    st.sidebar.info("No feedback saved yet")
```

---

## 🔧 Configuration

### **Required Secrets**

Add to `.streamlit/secrets.toml`:

```toml
[databricks]
server_hostname = "your-workspace.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/your-warehouse-id"
token = "YOUR_TOKEN"
genie_space_id = "YOUR_GENIE_SPACE_ID"
```

### **Find Your Genie Space ID**

Run the helper script:
```bash
python find_genie_space_id.py
```

Or manually:
1. Go to Databricks workspace
2. Navigate to AI/BI → Genie Spaces
3. Open your space
4. Look in URL: `/genie/spaces/<SPACE_ID>`
5. Copy that ID

---

## 📁 Files

- **`genie_chat.py`** - Main module (reusable)
- **`genie_chat_integration_example.py`** - Integration examples
- **`GENIE_CHAT_MODULE.md`** - This documentation
- **`.genie_feedback_memory.json`** - Persistent feedback storage (auto-created)

---

## 🎯 Features

### **✅ Persistent Feedback**
- Feedback saved to `.genie_feedback_memory.json`
- Automatically applied to new conversations
- Survives app restarts
- Last 10 corrections used
- Up to 50 corrections stored

### **✅ Clean UI**
- Simple "Genie is thinking..." progress indicator
- 120-second timeout for complex queries
- Enum-safe status checking
- Robust error handling

### **✅ Conversation Management**
- Maintains conversation context
- Easy reset for new conversations
- Chat history support

### **✅ Easy Integration**
- Import and use in any Streamlit app
- Minimal setup required
- Works with existing dashboards

---

## 🐛 Troubleshooting

### **"Could not connect to Databricks"**
- Check `databricks` secrets in `.streamlit/secrets.toml`
- Verify token is valid
- Ensure network connectivity

### **"Genie Space not found"**
- Verify `genie_space_id` in secrets
- Run `find_genie_space_id.py` to get correct ID
- Check you have access to the space

### **"Timeout after 120 seconds"**
- First query can be slow (warming up)
- Try a simpler question first
- Check Genie Space status in Databricks UI
- Subsequent queries should be faster

### **Feedback not persisting**
- Check `.genie_feedback_memory.json` exists
- Verify file write permissions
- Look for error messages in UI

---

## 📝 Full Example App

See **`genie_chat_integration_example.py`** for a complete working example showing:
- Full chat interface
- Feedback system
- Sidebar display
- Conversation management
- Error handling

---

## 🎉 Benefits

- ✅ **Reusable** - Import into any Streamlit app
- ✅ **Persistent** - Feedback survives restarts
- ✅ **Clean** - Professional UI, no debug clutter
- ✅ **Robust** - Handles errors gracefully
- ✅ **Documented** - Clear examples and API docs
- ✅ **Tested** - Working in production (app_with_genie.py)

---

**Ready to use! Import and add Genie AI to your dashboard!** 🚀

