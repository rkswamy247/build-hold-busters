@echo off
echo ========================================
echo  Deploying Hold Busters App to Databricks
echo ========================================
echo.

echo [1/2] Generating Databricks notebook...
python create_databricks_notebook.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate notebook
    pause
    exit /b 1
)
echo.

echo [2/2] Uploading to Databricks...
databricks workspace import -l PYTHON run_streamlit_app.py /Users/krr351@ftr.com/hold-busters-app/Run_Streamlit_App --overwrite
if %errorlevel% neq 0 (
    echo ERROR: Failed to upload to Databricks
    pause
    exit /b 1
)
echo.

echo ========================================
echo  SUCCESS! App deployed to Databricks
echo ========================================
echo.
echo Next steps:
echo 1. Go to your Databricks notebook
echo 2. Stop the current app (Cancel/Stop Cell 4)
echo 3. Refresh the page (F5)
echo 4. Run All cells
echo 5. Access your app via the proxy URL
echo.
pause

