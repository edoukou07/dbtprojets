# =====================================================================
# Script d'installation automatique - SIGETI DWH
# Compatible PowerShell 5.1+
# =====================================================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Installation SIGETI Data Warehouse" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Etape 1: Environnement virtuel Python
Write-Host "`n[1/6] Creation de l'environnement virtuel Python..." -ForegroundColor Cyan

if (Test-Path "venv") {
    Write-Host "  Environnement virtuel existe deja" -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Environnement virtuel cree" -ForegroundColor Green
    } else {
        Write-Host "  ERREUR: Impossible de creer l'environnement virtuel" -ForegroundColor Red
        Write-Host "  Verifiez que Python 3.9+ est installe" -ForegroundColor Yellow
        exit 1
    }
}

# Etape 2: Activation et installation des dependances
Write-Host "`n[2/6] Installation des dependances Python..." -ForegroundColor Cyan

$activateScript = Join-Path $projectRoot "venv\Scripts\Activate.ps1"
& $activateScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERREUR: Impossible d'activer l'environnement virtuel" -ForegroundColor Red
    exit 1
}

Write-Host "  Installation de dbt, Prefect, psycopg2..." -ForegroundColor Gray
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Dependances installees" -ForegroundColor Green
} else {
    Write-Host "  ERREUR lors de l'installation" -ForegroundColor Red
    exit 1
}

# Etape 3: Installation des packages dbt
Write-Host "`n[3/6] Installation des packages dbt..." -ForegroundColor Cyan

dbt deps
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Packages dbt installes (dbt-utils)" -ForegroundColor Green
} else {
    Write-Host "  ERREUR lors de l'installation des packages dbt" -ForegroundColor Red
    exit 1
}

# Etape 4: Configuration .env
Write-Host "`n[4/6] Configuration du fichier .env..." -ForegroundColor Cyan

if (Test-Path ".env") {
    Write-Host "  Fichier .env existe deja" -ForegroundColor Yellow
    Write-Host "  Conserve la configuration existante" -ForegroundColor Gray
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "  Fichier .env cree depuis .env.example" -ForegroundColor Green
    Write-Host "  IMPORTANT: Editez .env avec vos vrais mots de passe!" -ForegroundColor Yellow
}

# Etape 5: Verification de la connexion dbt
Write-Host "`n[5/6] Verification de la configuration dbt..." -ForegroundColor Cyan

dbt debug --profiles-dir . 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Configuration dbt valide" -ForegroundColor Green
} else {
    Write-Host "  Configuration dbt incomplete (normal si DB pas encore creee)" -ForegroundColor Yellow
}

# Etape 6: Configuration Prefect
Write-Host "`n[6/6] Configuration de Prefect..." -ForegroundColor Cyan

$prefectHome = $env:PREFECT_HOME
if (-not $prefectHome) {
    $prefectHome = "$env:USERPROFILE\.prefect"
}

if (-not (Test-Path $prefectHome)) {
    New-Item -ItemType Directory -Path $prefectHome -Force | Out-Null
    Write-Host "  Repertoire Prefect cree: $prefectHome" -ForegroundColor Green
} else {
    Write-Host "  Repertoire Prefect existe: $prefectHome" -ForegroundColor Yellow
}

# Resume
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Installation terminee!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nProchaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Editez le fichier .env avec vos mots de passe" -ForegroundColor White
Write-Host "     notepad .env" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Importez la base source (si pas deja fait)" -ForegroundColor White
Write-Host "     .\scripts\import_source_db.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Demarrez Prefect (dans un terminal)" -ForegroundColor White
Write-Host "     .\scripts\start_prefect.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Lancez le pipeline complet (dans un autre terminal)" -ForegroundColor White
Write-Host "     .\scripts\run_flow.ps1 -FlowType full" -ForegroundColor Gray
Write-Host ""
