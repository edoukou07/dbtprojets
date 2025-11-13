# SIGETI BI - Start Script
# This script starts both Django backend and React frontend

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  SIGETI BI - Démarrage de l'application" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if dependencies are installed
if (-not (Test-Path "..\venv")) {
    Write-Host "ERREUR: Environnement virtuel non trouve!" -ForegroundColor Red
    Write-Host "Veuillez d'abord executer: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "ERREUR: node_modules non trouvé!" -ForegroundColor Red
    Write-Host "Veuillez d'abord exécuter: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
& "..\venv\Scripts\Activate.ps1"

# Set environment variable for encoding
$env:PGCLIENTENCODING = "UTF8"

Write-Host "[INFO] Démarrage du backend Django..." -ForegroundColor Yellow
Write-Host "       URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# Start Django backend in a new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PWD\backend'; `
     & '..\..\venv\Scripts\Activate.ps1'; `
     `$env:PGCLIENTENCODING='UTF8'; `
     Write-Host '=== Django Backend ===' -ForegroundColor Green; `
     Write-Host 'API disponible sur: http://localhost:8000/api/' -ForegroundColor Cyan; `
     Write-Host 'Admin disponible sur: http://localhost:8000/admin/' -ForegroundColor Cyan; `
     Write-Host ''; `
     python manage.py runserver"

# Wait a bit for Django to start
Start-Sleep -Seconds 3

Write-Host "[INFO] Démarrage du frontend React..." -ForegroundColor Yellow
Write-Host "       URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

# Start React frontend in a new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PWD\frontend'; `
     Write-Host '=== React Frontend ===' -ForegroundColor Green; `
     Write-Host 'Application disponible sur: http://localhost:5173' -ForegroundColor Cyan; `
     Write-Host ''; `
     npm run dev"

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  Application demarree avec succes!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend (React):  http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend (Django):  http://localhost:8000/api/" -ForegroundColor Cyan
Write-Host "Admin Django:      http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour arreter l'application, fermez les deux fenetres PowerShell." -ForegroundColor Yellow
Write-Host ""
