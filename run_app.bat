@echo off
REM Streamlit App Launcher
echo.
echo Starting Hold Busters Dashboard...
echo.

REM Add Streamlit to PATH
set PATH=%PATH%;C:\Users\krr351\AppData\Roaming\Python\Python314\Scripts

REM Run Streamlit
echo Dashboard will open at http://localhost:8501
echo Press Ctrl+C to stop the app
echo.

python -m streamlit run app.py

pause

