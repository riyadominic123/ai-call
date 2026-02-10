# Check if virtual environment exists
if (Test-Path ".venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & .venv\Scripts\activate.ps1
} else {
    Write-Host "Warning: .venv not found. Running without virtual environment activation." -ForegroundColor Yellow
}

# Start the FastAPI application
Write-Host "Starting FastAPI server on http://0.0.0.0:8000" -ForegroundColor Cyan
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
