# TodoKanban Application Startup Script for Windows
# Run this with: .\run.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   TodoKanban Application Startup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-Not (Test-Path .env)) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Create virtual environment if it doesn't exist
if (-Not (Test-Path venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path uploads | Out-Null
New-Item -ItemType Directory -Force -Path data | Out-Null

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "   Starting FastAPI Application" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Application will be available at:" -ForegroundColor White
Write-Host "  - Main App: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
