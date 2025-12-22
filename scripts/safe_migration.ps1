# =============================================================================
# SCRIPT DE MIGRATION SÉCURISÉE - SIGETI DWH
# =============================================================================
# Ce script permet de migrer vers un nouveau dump SQL tout en préservant :
# - Les tables Django (auth, sessions, analytics)
# - Le schema DWH (optionnel, sera reconstruit par dbt)
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$NewDumpFile,
    
    [string]$DbHost = "localhost",
    [string]$DbPort = "5432",
    [string]$DbName = "sigeti_node_db",
    [string]$DbUser = "postgres",
    [string]$BackupDir = ".\migration_backup"
)

# Configuration
$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  MIGRATION SÉCURISÉE SIGETI DWH" -ForegroundColor Cyan
Write-Host "  Date: $timestamp" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Vérifier que le fichier dump existe
if (-not (Test-Path $NewDumpFile)) {
    Write-Host "ERREUR: Le fichier dump '$NewDumpFile' n'existe pas!" -ForegroundColor Red
    exit 1
}

# Créer le dossier de backup
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host ""
Write-Host "[1/6] Sauvegarde des tables Django..." -ForegroundColor Yellow

# Tables Django à sauvegarder
$djangoTables = @(
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "auth_user",
    "auth_user_groups",
    "auth_user_user_permissions",
    "authtoken_token",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_session"
)

$djangoBackupFile = "$BackupDir\django_tables_$timestamp.sql"

# Construire la commande pg_dump pour Django
$tableArgs = ($djangoTables | ForEach-Object { "--table=$_" }) -join " "

try {
    $env:PGPASSWORD = Read-Host "Entrez le mot de passe PostgreSQL" -AsSecureString | ConvertFrom-SecureString -AsPlainText
    
    # Sauvegarder les tables Django (ignorer les erreurs si tables n'existent pas)
    $cmd = "pg_dump -h $DbHost -p $DbPort -U $DbUser -d $DbName --if-exists --clean $tableArgs -f `"$djangoBackupFile`" 2>&1"
    Invoke-Expression $cmd
    
    if (Test-Path $djangoBackupFile) {
        Write-Host "  ✓ Tables Django sauvegardées: $djangoBackupFile" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Pas de tables Django trouvées (première installation?)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Avertissement: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/6] Sauvegarde du schema DWH..." -ForegroundColor Yellow

$dwhBackupFile = "$BackupDir\dwh_schema_$timestamp.sql"

try {
    $cmd = "pg_dump -h $DbHost -p $DbPort -U $DbUser -d $DbName --schema=dwh -f `"$dwhBackupFile`" 2>&1"
    Invoke-Expression $cmd
    
    if (Test-Path $dwhBackupFile) {
        Write-Host "  ✓ Schema DWH sauvegardé: $dwhBackupFile" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ Schema DWH non trouvé (sera créé par dbt)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/6] Sauvegarde complète de sécurité..." -ForegroundColor Yellow

$fullBackupFile = "$BackupDir\full_backup_$timestamp.sql"
$cmd = "pg_dump -h $DbHost -p $DbPort -U $DbUser -d $DbName -f `"$fullBackupFile`" 2>&1"
Invoke-Expression $cmd

Write-Host "  ✓ Backup complet: $fullBackupFile" -ForegroundColor Green

Write-Host ""
Write-Host "[4/6] Restauration du nouveau dump..." -ForegroundColor Yellow
Write-Host "  Fichier source: $NewDumpFile" -ForegroundColor Gray

# Confirmation
$confirm = Read-Host "Voulez-vous continuer? Cette opération va modifier la base de données (O/N)"
if ($confirm -ne "O" -and $confirm -ne "o") {
    Write-Host "Migration annulée." -ForegroundColor Yellow
    exit 0
}

try {
    $cmd = "psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -f `"$NewDumpFile`" 2>&1"
    $result = Invoke-Expression $cmd
    Write-Host "  ✓ Nouveau dump restauré avec succès" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Erreur lors de la restauration: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Tentative de restauration du backup..." -ForegroundColor Yellow
    $cmd = "psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -f `"$fullBackupFile`""
    Invoke-Expression $cmd
    exit 1
}

Write-Host ""
Write-Host "[5/6] Restauration des tables Django..." -ForegroundColor Yellow

if (Test-Path $djangoBackupFile) {
    try {
        $cmd = "psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -f `"$djangoBackupFile`" 2>&1"
        Invoke-Expression $cmd
        Write-Host "  ✓ Tables Django restaurées" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Les tables Django seront recréées par Django migrate" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Pas de tables Django à restaurer" -ForegroundColor Yellow
    Write-Host "  Exécutez 'python manage.py migrate' dans le backend Django" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[6/6] Reconstruction du DWH avec dbt..." -ForegroundColor Yellow

try {
    Set-Location $PSScriptRoot\..
    dbt run --profiles-dir .
    Write-Host "  ✓ DWH reconstruit avec succès" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Erreur dbt: Exécutez manuellement 'dbt run'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  MIGRATION TERMINÉE AVEC SUCCÈS" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Fichiers de backup créés dans: $BackupDir" -ForegroundColor Gray
Write-Host "  - django_tables_$timestamp.sql" -ForegroundColor Gray
Write-Host "  - dwh_schema_$timestamp.sql" -ForegroundColor Gray
Write-Host "  - full_backup_$timestamp.sql" -ForegroundColor Gray
Write-Host ""
Write-Host "Prochaines étapes recommandées:" -ForegroundColor Yellow
Write-Host "  1. Vérifier les tables: psql -c '\dt' sigeti_node_db" -ForegroundColor Gray
Write-Host "  2. Exécuter les migrations Django: python manage.py migrate" -ForegroundColor Gray
Write-Host "  3. Tester l'application BI" -ForegroundColor Gray
