# Script PowerShell pour déployer le pipeline avec Prefect 3.x
# Utilise la nouvelle API de déploiement

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Déploiement Pipeline SIGETI DWH - Prefect 3.x" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
Write-Host "[1/4] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Configurer l'encodage
Write-Host "[2/4] Configuration de l'encodage UTF-8..." -ForegroundColor Yellow
$env:PGCLIENTENCODING = "UTF8"

# Déployer avec prefect deploy
Write-Host "[3/4] Déploiement du flow..." -ForegroundColor Yellow
Write-Host ""

prefect deploy --name sigeti-dwh-daily `
    --pool default-agent-pool `
    --cron "0 2 * * *" `
    --timezone "Africa/Abidjan" `
    --tag production `
    --tag dwh `
    --tag daily `
    prefect/flows/sigeti_dwh_flow.py:sigeti_dwh_full_refresh

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host " ✅ Déploiement créé avec succès!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Informations du déploiement:" -ForegroundColor Cyan
    Write-Host "   Nom: sigeti-dwh-daily" -ForegroundColor White
    Write-Host "   Planification: Quotidienne à 2h00 (Africa/Abidjan)" -ForegroundColor White
    Write-Host "   Tags: production, dwh, daily" -ForegroundColor White
    Write-Host ""
    Write-Host "📌 Prochaines étapes:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Option 1: Démarrer un worker Prefect" -ForegroundColor White
    Write-Host "   -----------------------------------------" -ForegroundColor DarkGray
    Write-Host "   prefect worker start --pool default-agent-pool" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Option 2: Utiliser Prefect Cloud" -ForegroundColor White
    Write-Host "   -----------------------------------------" -ForegroundColor DarkGray
    Write-Host "   1. Se connecter: prefect cloud login" -ForegroundColor Green
    Write-Host "   2. Le worker cloud gérera l'exécution" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Interface web:" -ForegroundColor Yellow
    Write-Host "   Local: http://127.0.0.1:4200" -ForegroundColor Cyan
    Write-Host "   Cloud: https://app.prefect.cloud" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors du déploiement" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Solution alternative: Utiliser flow.serve()" -ForegroundColor Yellow
    Write-Host "   python prefect\deployments\deploy_scheduled.py" -ForegroundColor Green
}
