# 🦙 Ollama AI Setup for Hold Busters

Run AI-powered invoice analysis **100% locally** - No API keys, No costs, Complete privacy!

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Install Ollama** (2 minutes)

1. Go to: https://ollama.com/download
2. Download **Ollama for Windows**
3. Run the installer
4. Ollama will start automatically

### **Step 2: Install AI Model** (3 minutes)

Open PowerShell and run:

```powershell
# Install Llama 3.2 (recommended - good balance of speed and quality)
ollama pull llama3.2

# This downloads ~2-4GB and takes a few minutes
```

### **Step 3: Run the App**

```powershell
# Navigate to your project
cd "C:\Users\tgg550\OneDrive - Frontier Communications\Documents\Hach-AI-Thon - Hack The Hold\build-hold-busters-1"

# Run with Ollama
.\run_with_ollama.ps1

# OR manually
.\venv\Scripts\Activate.ps1
pip install ollama
streamlit run app_with_ollama.py
```

---

## ✅ **Why Ollama?**

### **Advantages:**

✅ **100% Free** - No API costs ever
✅ **Completely Private** - Data never leaves your machine
✅ **No API Keys** - No setup hassle
✅ **Offline Capable** - Works without internet
✅ **No Rate Limits** - Use as much as you want
✅ **Enterprise Ready** - Perfect for corporate environments

### **Trade-offs:**

⚠️ **Slower** - Runs on your CPU/GPU (10-30 seconds per response)
⚠️ **Requires Download** - Initial model download is 2-4GB
⚠️ **Uses Local Resources** - Uses your computer's RAM and CPU

---

## 🤖 Available Models

### **Recommended:**

```powershell
# Llama 3.2 (3B parameters) - Best balance
ollama pull llama3.2              # ~2GB, fast, good quality

# Llama 3.2 1B - Faster, smaller
ollama pull llama3.2:1b           # ~1GB, very fast, decent quality
```

### **More Powerful (if you have resources):**

```powershell
# Llama 3.1 (8B parameters) - Better quality, slower
ollama pull llama3.1              # ~4.7GB

# Mistral (7B parameters) - Good for SQL
ollama pull mistral               # ~4.1GB
```

### **Check Installed Models:**

```powershell
ollama list
```

---

## 💬 What You Can Ask

### **Simple Questions:**
- "How many invoices are on hold?"
- "Which vendor has the most invoices?"
- "What's the total amount of pending invoices?"

### **Complex Analysis:**
- "Show me invoices over $50,000 that have been pending more than 30 days"
- "Which states have the highest average days pending?"
- "Compare vendor performance by hold rate"

### **Business Insights:**
- "What are the most common hold reasons?"
- "Identify bottlenecks in the approval process"
- "Analyze invoice trends by state and vendor"

---

## ⚡ Performance Tips

### **Speed Up Responses:**

1. **Use Smaller Models:**
   ```powershell
   ollama pull llama3.2:1b  # Much faster!
   ```

2. **Close Other Apps:**
   - Free up RAM and CPU
   - Close browser tabs, other programs

3. **Upgrade Hardware:**
   - More RAM = better performance
   - GPU acceleration (if available)

### **Improve Quality:**

1. **Use Larger Models:**
   ```powershell
   ollama pull llama3.1:8b  # Better quality
   ```

2. **Be Specific:**
   - Provide clear context
   - Ask follow-up questions
   - Use examples

---

## 🔧 Troubleshooting

### **"Ollama not found"**

**Solution:**
1. Install from: https://ollama.com/download
2. Restart PowerShell
3. Verify: `ollama --version`

---

### **"Model not found"**

**Solution:**
```powershell
# List installed models
ollama list

# Install a model
ollama pull llama3.2
```

---

### **"Connection failed" or "Ollama not running"**

**Solution:**
1. Open Task Manager
2. Look for "ollama" process
3. If not running, run: `ollama serve`
4. Or reinstall Ollama

---

### **Slow Performance**

**Solutions:**
1. Use smaller model: `ollama pull llama3.2:1b`
2. Close other applications
3. Reduce conversation history (app keeps last 6 messages)
4. Check RAM usage (need at least 4GB free)

---

### **AI Gives Wrong SQL**

**Solutions:**
1. Be more specific in your question
2. Provide examples: "Like this: SELECT * FROM invoices WHERE..."
3. Try rephrasing the question
4. Use the Data Explorer tab for manual queries

---

## 📊 System Requirements

### **Minimum:**
- **RAM:** 8GB (4GB free)
- **Storage:** 5GB free space
- **CPU:** Modern x64 processor
- **OS:** Windows 10/11

### **Recommended:**
- **RAM:** 16GB+ (8GB free)
- **Storage:** 10GB+ free space
- **CPU:** Multi-core processor
- **GPU:** NVIDIA GPU with CUDA (optional, for acceleration)

---

## 🔄 Updating Models

```powershell
# Check for updates
ollama list

# Update a model
ollama pull llama3.2

# Remove old models
ollama rm old-model-name
```

---

## 🎮 Advanced Usage

### **Switch Models in the App:**

The app detects all installed models and lets you choose which one to use from the sidebar!

### **Run Multiple Models:**

```powershell
# Install multiple models
ollama pull llama3.2
ollama pull mistral
ollama pull codellama  # Great for SQL!

# Switch between them in the app UI
```

### **Model-Specific Features:**

- **llama3.2** - Best all-rounder
- **mistral** - Good for analysis
- **codellama** - Best for SQL generation
- **llama3.2:1b** - Fastest option

---

## 💡 Tips & Tricks

### **1. Start Simple**
Begin with basic questions to understand the AI's capabilities.

### **2. Provide Context**
"Show me invoices from California" works better than just "Show invoices"

### **3. Iterate**
Ask follow-up questions to refine results

### **4. Use Suggested Questions**
Click the suggested questions to see examples

### **5. Check Query Results**
Always review the generated SQL before trusting results

---

## 🆚 Ollama vs Cloud AI

| Feature | Ollama (Local) | Cloud AI (Anthropic/OpenAI) |
|---------|----------------|----------------------------|
| **Cost** | Free | $0.003-0.03 per query |
| **Speed** | 10-30 seconds | 2-5 seconds |
| **Privacy** | 100% Private | Data sent to cloud |
| **Quality** | Good | Excellent |
| **Setup** | Download model | Get API key |
| **Internet** | Not required | Required |
| **Rate Limits** | None | Yes (varies) |

---

## 🎉 You're Ready!

Your AI-powered invoice analysis is now:
- ✅ Running 100% locally
- ✅ Completely free
- ✅ Totally private
- ✅ Ready to answer questions!

---

## 📞 Resources

- **Ollama Website**: https://ollama.com/
- **Model Library**: https://ollama.com/library
- **GitHub**: https://github.com/ollama/ollama
- **Discord Community**: https://discord.gg/ollama

---

**Happy analyzing with local AI!** 🦙🚀

