# SIGETI BI - Django + React Setup Script
# Run this script to install and start the application

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  SIGETI BI - Installation et Démarrage" -ForegroundColor Cyan
Write-Host "  Django Backend + React Frontend" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "[1/6] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "..\venv\Scripts\Activate.ps1"

# Install backend dependencies
Write-Host "[2/6] Installation des dépendances backend (Django)..." -ForegroundColor Yellow
Set-Location "backend"
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "[3/6] Installation des dépendances frontend (React)..." -ForegroundColor Yellow
Set-Location "..\frontend"
npm install

# Return to bi_app folder
Set-Location ".."

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  Installation terminée!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour démarrer l'application, utilisez:" -ForegroundColor Cyan
Write-Host "  .\start.ps1" -ForegroundColor White
Write-Host ""
