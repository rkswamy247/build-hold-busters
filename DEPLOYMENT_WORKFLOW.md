# 🚀 Deployment Workflow for Hold Busters App

This guide explains how to make changes to your Streamlit app and redeploy it to Databricks.

---

## 📋 Quick Reference

### First Time Setup ✅
You've already completed this:
- ✅ App code created (`app_databricks.py`)
- ✅ Deployment scripts created (`create_databricks_notebook.py`, `deploy.bat`)
- ✅ Databricks CLI configured
- ✅ App deployed and running in Databricks

### Current App URL
```
https://dbc-4a93b454-f17b.cloud.databricks.com/driver-proxy/o/1978110925405963/<CLUSTER_ID>/8501/
```

---

## 🔄 Making Changes & Redeploying

### Option 1: Using the Automated Script (Recommended) ⭐

**Step 1:** Make your changes to `app_databricks.py`

**Step 2:** Run the deployment script:
```bash
deploy.bat
```

**Step 3:** In Databricks:
1. Go to your notebook
2. Stop Cell 4 (running Streamlit)
3. Refresh the page (F5)
4. Click "Run All"
5. Access your app via the proxy URL

---

### Option 2: Manual Deployment

**Step 1:** Make your changes to `app_databricks.py`

**Step 2:** Regenerate the notebook:
```bash
python create_databricks_notebook.py
```

**Step 3:** Upload to Databricks:
```bash
databricks workspace import -l PYTHON run_streamlit_app.py /Users/krr351@ftr.com/hold-busters-app/Run_Streamlit_App --overwrite
```

**Step 4:** In Databricks (same as Option 1):
1. Stop Cell 4
2. Refresh page
3. Run All
4. Access app

---

## 💻 Local Development Workflow

### Testing Locally (Recommended Before Deploying)

```bash
# Run the app locally
streamlit run app_databricks.py

# Or use the launcher script
run_app.bat
```

**Benefits:**
- ✅ Instant feedback
- ✅ No upload/restart needed
- ✅ Faster iteration
- ✅ Test before deploying

**When ready:**
- Deploy to Databricks using `deploy.bat`

---

## 🎯 Complete Development Cycle

```
1. Local Development
   ├─ Edit: app_databricks.py
   ├─ Test: streamlit run app_databricks.py
   └─ Iterate until satisfied

2. Deploy to Databricks
   ├─ Run: deploy.bat
   └─ Wait for upload confirmation

3. Restart in Databricks
   ├─ Stop Cell 4
   ├─ Refresh page
   ├─ Run All cells
   └─ Access via proxy URL

4. Verify & Test
   └─ Test all features in Databricks environment
```

---

## 📂 Project Structure

```
build-hold-busters/
├── app_databricks.py              # Main app (edit this!)
├── create_databricks_notebook.py  # Notebook generator
├── deploy.bat                     # Automated deployment
├── run_streamlit_app.py          # Generated notebook (don't edit!)
├── requirements.txt              # Dependencies
├── .streamlit/
│   └── secrets.toml              # Local credentials
└── DEPLOYMENT_WORKFLOW.md        # This file
```

---

## 🐛 Troubleshooting

### App not reflecting changes?
- Make sure you ran `deploy.bat` or the manual steps
- Refresh the Databricks notebook page (F5)
- Clear Streamlit cache using the "🔄 Refresh Data" button in the app

### Can't access the proxy URL?
- Make sure Cell 4 is running (you should see the Streamlit output)
- Verify you're logged into Databricks in the same browser
- Check that your cluster is running

### Secrets not found error?
- The notebook creates secrets automatically in Cell 2
- Make sure you run Cell 2 before Cell 4
- Or just click "Run All" to run all cells in order

### Need to update credentials?
- Edit `create_databricks_notebook.py` (line with `secrets_content`)
- Update the token, http_path, or schema
- Run `deploy.bat` to redeploy with new credentials

---

## 📝 Best Practices

1. **Always test locally first** before deploying to Databricks
2. **Commit your changes to git** before deploying
3. **Use meaningful commit messages** for tracking changes
4. **Keep credentials secure** - never commit secrets.toml to git
5. **Document major changes** in commit messages or this file

---

## 🔒 Security Notes

- `secrets.toml` is gitignored (never committed)
- Credentials are embedded in the notebook (only visible to you in Databricks)
- Access token is user-specific (expires based on your settings)

---

## 📞 Need Help?

- **Local testing issues:** Check `GET_STARTED.md` and `README_SETUP.md`
- **Databricks issues:** See `DEPLOY_TO_DATABRICKS.md`
- **Data issues:** Check `UPLOAD_DATA_TO_DATABRICKS.md`
- **Feature docs:** See `SEND_TO_LINUS_FEATURE.md`

---

**Last Updated:** 2025-01-18  
**Current Branch:** hacking  
**App Status:** ✅ Deployed and Running

