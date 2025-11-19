@echo off
REM ============================================
REM Hold Busters Dashboard Launcher
REM ============================================

echo.
echo ====================================
echo   Hold Busters Dashboard
echo ====================================
echo.
echo Checking dependencies...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit is not installed
    echo.
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    echo.
)

REM Check if secrets.toml exists
if not exist ".streamlit\secrets.toml" (
    echo WARNING: .streamlit\secrets.toml not found!
    echo Please create it from secrets.toml.template
    echo.
    pause
    exit /b 1
)

echo.
echo Starting dashboard...
echo.
echo Dashboard URL: http://localhost:8501
echo.
echo Features:
echo   - Invoice Overview Dashboard
echo   - Invoice Details Analysis
echo   - Deep Analysis with Drill-downs
echo   - Error Analysis Dashboard
echo   - Custom SQL Query Tool
echo   - Genie AI Q^&A (requires Databricks credentials)
echo.
echo Press Ctrl+C to stop the app
echo.
echo ====================================
echo.

REM Run Streamlit
streamlit run app.py

echo.
echo Dashboard stopped.
pause

