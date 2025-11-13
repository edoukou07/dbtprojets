# Script pour créer une tâche planifiée Windows
# Exécute le pipeline tous les jours à 2h du matin

$TaskName = "SIGETI_DWH_Daily_Refresh"
$TaskDescription = "Rafraîchissement quotidien de l'entrepôt de données SIGETI"
$ScriptPath = "C:\Users\hynco\Desktop\DWH_SIG\run_pipeline.ps1"
$WorkingDirectory = "C:\Users\hynco\Desktop\DWH_SIG"

# Vérifier si la tâche existe déjà
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "⚠️  La tâche '$TaskName' existe déjà. Suppression..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Créer l'action (exécuter le script PowerShell)
$Action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`"" `
    -WorkingDirectory $WorkingDirectory

# Créer le déclencheur (tous les jours à 2h00)
$Trigger = New-ScheduledTaskTrigger -Daily -At 02:00AM

# Créer les paramètres de la tâche
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Créer le principal (utilisateur actuel)
$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

# Enregistrer la tâche
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal

Write-Host ""
Write-Host "✅ Tâche planifiée créée avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Détails de la tâche:" -ForegroundColor Cyan
Write-Host "  Nom: $TaskName"
Write-Host "  Planification: Tous les jours à 2h00"
Write-Host "  Script: $ScriptPath"
Write-Host ""
Write-Host "🔧 Commandes utiles:" -ForegroundColor Yellow
Write-Host "  Voir la tâche: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Exécuter maintenant: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Désactiver: Disable-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Supprimer: Unregister-ScheduledTask -TaskName '$TaskName'"
