# Script pour exécuter les flows Prefect
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("full", "incremental", "marts")]
    [string]$FlowType
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Exécution du flow SIGETI DWH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_DIR = "C:\Users\hynco\Desktop\DWH_SIG"
$VENV_DIR = "$PROJECT_DIR\venv"

# Activer l'environnement virtuel
& "$VENV_DIR\Scripts\Activate.ps1"

# Définir PREFECT_HOME
$env:PREFECT_HOME = "C:\Users\hynco\.prefect"

# Charger les variables d'environnement depuis .env
if (Test-Path "$PROJECT_DIR\.env") {
    Get-Content "$PROJECT_DIR\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Exécuter le flow approprié
Set-Location $PROJECT_DIR

switch ($FlowType) {
    "full" {
        Write-Host "🚀 Exécution du Full Refresh..." -ForegroundColor Green
        Write-Host ""
        python -c "from prefect.flows.sigeti_dwh_flow import sigeti_dwh_full_refresh; sigeti_dwh_full_refresh()"
    }
    "incremental" {
        Write-Host "🔄 Exécution du Refresh Incrémental..." -ForegroundColor Green
        Write-Host ""
        python -c "from prefect.flows.sigeti_dwh_flow import sigeti_dwh_incremental; sigeti_dwh_incremental()"
    }
    "marts" {
        Write-Host "🎯 Reconstruction des Data Marts..." -ForegroundColor Green
        Write-Host ""
        python -c "from prefect.flows.sigeti_dwh_flow import sigeti_dwh_rebuild_marts_only; sigeti_dwh_rebuild_marts_only()"
    }
}

Write-Host ""
Write-Host "✅ Exécution terminée" -ForegroundColor Green
