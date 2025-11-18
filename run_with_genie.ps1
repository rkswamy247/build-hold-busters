# Run Hold Busters Dashboard with Databricks Genie
# This script sets up and runs the Streamlit app with Genie AI

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Hold Busters - Genie AI Edition " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (Test-Path "venv") {
    Write-Host "[OK] Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "[SETUP] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

Write-Host ""

# Activate venv
Write-Host "[SETUP] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""

# Install/update dependencies
Write-Host "[SETUP] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
pip install -r requirements_databricks_ai.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try manually:" -ForegroundColor Yellow
    Write-Host "  pip install streamlit databricks-sql-connector databricks-sdk plotly pandas pyarrow" -ForegroundColor White
    exit 1
}

Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check secrets
if (Test-Path ".streamlit\secrets.toml") {
    Write-Host "[OK] Secrets file found" -ForegroundColor Green
    
    # Check if genie_space_id is configured
    $secretsContent = Get-Content ".streamlit\secrets.toml" -Raw
    if ($secretsContent -notmatch "genie_space_id") {
        Write-Host "[WARNING] genie_space_id not found in secrets.toml" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "You need to add your Genie Space ID:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Go to Databricks Console" -ForegroundColor White
        Write-Host "2. Navigate to AI/BI -> Genie Spaces" -ForegroundColor White
        Write-Host "3. Open your Genie Space" -ForegroundColor White
        Write-Host "4. Copy the Space ID from the URL: /genie/spaces/<SPACE_ID>" -ForegroundColor White
        Write-Host ""
        Write-Host "5. Add to .streamlit\secrets.toml:" -ForegroundColor White
        Write-Host "   [databricks]" -ForegroundColor Gray
        Write-Host "   genie_space_id = `"YOUR_SPACE_ID`"" -ForegroundColor Gray
        Write-Host ""
        
        $continue = Read-Host "Do you want to continue anyway? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    }
} else {
    Write-Host "[WARNING] Secrets file not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Creating template .streamlit\secrets.toml..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path ".streamlit" | Out-Null
    @"
[databricks]
server_hostname = "YOUR_DATABRICKS_HOSTNAME"
http_path = "YOUR_HTTP_PATH"
token = "YOUR_DATABRICKS_TOKEN"

# Genie Space ID (find this in your Genie Space URL)
# Example: /genie/spaces/01ef1234abcd5678
genie_space_id = "YOUR_GENIE_SPACE_ID"
"@ | Out-File -FilePath ".streamlit\secrets.toml" -Encoding UTF8
    
    Write-Host "[CREATED] Template secrets file" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit .streamlit\secrets.toml with your Databricks credentials:" -ForegroundColor Red
    Write-Host "  1. server_hostname - Your Databricks workspace hostname" -ForegroundColor White
    Write-Host "  2. http_path - SQL warehouse HTTP path" -ForegroundColor White
    Write-Host "  3. token - Your Databricks personal access token" -ForegroundColor White
    Write-Host "  4. genie_space_id - Your Genie Space ID" -ForegroundColor White
    Write-Host ""
    Write-Host "To find your Genie Space ID:" -ForegroundColor Yellow
    Write-Host "  1. Go to Databricks Console" -ForegroundColor White
    Write-Host "  2. Navigate to AI/BI -> Genie Spaces" -ForegroundColor White
    Write-Host "  3. Open your Genie Space" -ForegroundColor White
    Write-Host "  4. Copy ID from URL: /genie/spaces/<SPACE_ID>" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting Genie AI Dashboard... " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  - Databricks Genie AI" -ForegroundColor White
Write-Host "  - Genie understands your data schema" -ForegroundColor White
Write-Host "  - Optimized SQL generation" -ForegroundColor White
Write-Host "  - Conversation memory" -ForegroundColor White
Write-Host "  - AI feedback & learning" -ForegroundColor White
Write-Host ""
Write-Host "The app will open in your browser..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Run Streamlit
#streamlit run app_with_genie.py
streamlit run app.py