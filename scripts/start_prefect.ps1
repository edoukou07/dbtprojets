# Script pour démarrer le serveur Prefect en local

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du serveur Prefect" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_DIR = "C:\Users\hynco\Desktop\DWH_SIG"
$VENV_DIR = "$PROJECT_DIR\venv"

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "$VENV_DIR\Scripts\Activate.ps1"

# Définir PREFECT_HOME
$env:PREFECT_HOME = "C:\Users\hynco\.prefect"
Write-Host "PREFECT_HOME: $env:PREFECT_HOME" -ForegroundColor Cyan
Write-Host ""

# Démarrer le serveur Prefect
Write-Host "🚀 Démarrage du serveur Prefect..." -ForegroundColor Green
Write-Host ""
Write-Host "Interface UI disponible sur: http://127.0.0.1:4200" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

prefect server start
