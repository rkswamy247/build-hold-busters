# Streamlit App Launcher
# This script adds Streamlit to PATH and launches the app

Write-Host "Starting Hold Busters Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Add Streamlit to PATH for this session
#$env:Path += ";C:\Users\krr351\AppData\Roaming\Python\Python314\Scripts"
$env:Path += ";C:\Users\tgg550\AppData\Roaming\Python\Python312\Scripts"
$env:Path += ";C:\Users\tgg550\AppData\Roaming\Python\Python313\Scripts"
$env:Path += ";C:\Users\tgg550\AppData\Roaming\Python\Python314\Scripts"
$env:Path += ";C:\Users\tgg550\AppData\Local\Programs\Python\Python312\Scripts"
$env:Path += ";C:\Users\tgg550\AppData\Local\Programs\Python\Python313\Scripts"

# Navigate to the app directory
Set-Location $PSScriptRoot

# Check if secrets are configured
if (-not (Test-Path ".\.streamlit\secrets.toml")) {
    Write-Host "Error: secrets.toml not found!" -ForegroundColor Red
    Write-Host "Please copy .streamlit\secrets.toml.template to .streamlit\secrets.toml" -ForegroundColor Yellow
    Write-Host "and configure your Databricks credentials." -ForegroundColor Yellow
    pause
    exit 1
}

# Run Streamlit
Write-Host "Launching dashboard at http://localhost:8501" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the app" -ForegroundColor Yellow
Write-Host ""

streamlit run app.py

