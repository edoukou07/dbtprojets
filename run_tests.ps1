# Script pour exécuter les tests dbt avec encodage UTF-8
# Usage: .\run_tests.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Exécution des Tests dbt - SIGETI DWH" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration de l'encodage UTF-8
Write-Host "[1/3] Configuration de l'encodage UTF-8..." -ForegroundColor Yellow
$env:PGCLIENTENCODING = "UTF8"

# Activer l'environnement virtuel
Write-Host "[2/3] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Exécuter les tests dbt
Write-Host "[3/3] Exécution des tests de qualité..." -ForegroundColor Yellow
Write-Host ""

dbt test

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host " ✅ Tous les tests ont réussi!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host " ❌ Certains tests ont échoué" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Vérifiez les erreurs ci-dessus" -ForegroundColor Yellow
}
