# Script de lancement du pipeline SIGETI DWH
# Configure l'encodage UTF-8 pour PostgreSQL et exécute le pipeline

Write-Host "================================" -ForegroundColor Cyan
Write-Host " SIGETI DWH - Pipeline Execution" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Configuration de l'encodage
$env:PGCLIENTENCODING = "UTF8"
Write-Host "[INFO] Encodage PostgreSQL configure: UTF-8" -ForegroundColor Green

# Activation de l'environnement virtuel
Write-Host "[INFO] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Exécution du pipeline
Write-Host "[INFO] Demarrage du pipeline..." -ForegroundColor Yellow
Write-Host ""
python prefect\flows\sigeti_dwh_flow.py

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Pipeline Termine" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
