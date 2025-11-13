# =====================================================================
# Script d'import de la base source SIGETI
# Compatible PowerShell 5.1+
# =====================================================================

param(
    [string]$BackupFile = "local_backup_sigeti_node_db_12112025.sql",
    [string]$DbName = "sigeti_node_db",
    [string]$DbUser = "postgres",
    [string]$DbPassword = "postgres",
    [string]$DbHost = "localhost"
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Import de la base source SIGETI" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Determiner le chemin du projet
$scriptDir = $PSScriptRoot
$projectRoot = Split-Path -Parent $scriptDir
$backupPath = Join-Path $projectRoot $BackupFile
$filteredFile = Join-Path $projectRoot "filtered_backup.sql"

Write-Host "`nConfiguration:" -ForegroundColor Yellow
Write-Host "  Fichier backup: $BackupFile" -ForegroundColor Gray
Write-Host "  Base de donnees: $DbName" -ForegroundColor Gray
Write-Host "  Utilisateur: $DbUser" -ForegroundColor Gray
Write-Host "  Hote: $DbHost" -ForegroundColor Gray

# Verifier que le fichier existe
if (-not (Test-Path $backupPath)) {
    Write-Host "`nERREUR: Fichier de backup introuvable!" -ForegroundColor Red
    Write-Host "Chemin recherche: $backupPath" -ForegroundColor Red
    exit 1
}

Write-Host "`nFichier trouve: $backupPath" -ForegroundColor Green
$fileSize = (Get-Item $backupPath).Length / 1MB
Write-Host "Taille: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray

# Etape 1: Creer la base
Write-Host "`n[1/3] Creation de la base de donnees..." -ForegroundColor Cyan
$env:PGPASSWORD = $DbPassword
$createCmd = "CREATE DATABASE $DbName;"

try {
    psql -U $DbUser -h $DbHost -d postgres -c $createCmd 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Base creee avec succes" -ForegroundColor Green
    } else {
        Write-Host "  Base existe deja" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Base existe probablement deja" -ForegroundColor Yellow
}

# Etape 2: Filtrer le fichier SQL
Write-Host "`n[2/3] Filtrage du fichier SQL (exclusion SequelizeMeta)..." -ForegroundColor Cyan

$inSequelizeMeta = $false
$totalLines = 0
$skippedLines = 0
$outputLines = 0

$reader = [System.IO.StreamReader]::new($backupPath)
$writer = [System.IO.StreamWriter]::new($filteredFile, $false, [System.Text.Encoding]::UTF8)

try {
    while ($null -ne ($line = $reader.ReadLine())) {
        $totalLines++
        
        # Afficher progression tous les 1000 lignes
        if ($totalLines % 1000 -eq 0) {
            Write-Host "`r  Traitement: $totalLines lignes..." -NoNewline -ForegroundColor Gray
        }
        
        # Detecter debut bloc SequelizeMeta
        if ($line -match 'COPY public\."SequelizeMeta"') {
            $inSequelizeMeta = $true
            $skippedLines++
            continue
        }
        
        # Detecter fin bloc COPY
        if ($inSequelizeMeta -and $line -match '^\\.$') {
            $inSequelizeMeta = $false
            $skippedLines++
            continue
        }
        
        # Sauter lignes dans SequelizeMeta
        if ($inSequelizeMeta) {
            $skippedLines++
            continue
        }
        
        # Ecrire la ligne
        $writer.WriteLine($line)
        $outputLines++
    }
} finally {
    $reader.Close()
    $writer.Close()
}

Write-Host "`r  Filtrage termine: $totalLines lignes lues, $skippedLines ignorees" -ForegroundColor Green

# Etape 3: Import
Write-Host "`n[3/3] Import des donnees dans PostgreSQL..." -ForegroundColor Cyan
Write-Host "  Cela peut prendre plusieurs minutes..." -ForegroundColor Yellow

$env:PGPASSWORD = $DbPassword
psql -U $DbUser -h $DbHost -d $DbName -f $filteredFile 2>&1 | Out-File -FilePath (Join-Path $projectRoot "import.log") -Encoding UTF8

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  Import reussi!" -ForegroundColor Green
    
    # Nettoyer fichier temporaire
    Remove-Item $filteredFile -Force -ErrorAction SilentlyContinue
    
    # Verifier les tables
    Write-Host "`n=====================================" -ForegroundColor Cyan
    Write-Host "Verification des donnees importees" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    
    Write-Host "`nNombre d'enregistrements par table:" -ForegroundColor Yellow
    $env:PGPASSWORD = $DbPassword
    
    $countQuery = @"
SELECT 'entreprises' as table_name, COUNT(*)::text as count FROM entreprises
UNION ALL SELECT 'lots', COUNT(*)::text FROM lots
UNION ALL SELECT 'factures', COUNT(*)::text FROM factures
UNION ALL SELECT 'paiement_factures', COUNT(*)::text FROM paiement_factures
UNION ALL SELECT 'collectes', COUNT(*)::text FROM collectes
UNION ALL SELECT 'zones_industrielles', COUNT(*)::text FROM zones_industrielles
UNION ALL SELECT 'demandes_attribution', COUNT(*)::text FROM demandes_attribution
UNION ALL SELECT 'domaines_activites', COUNT(*)::text FROM domaines_activites
ORDER BY table_name;
"@
    
    psql -U $DbUser -h $DbHost -d $DbName -c $countQuery
    
    Write-Host "`nImport termine avec succes!" -ForegroundColor Green
    Write-Host "Vous pouvez maintenant executer le pipeline dbt." -ForegroundColor Cyan
    
} else {
    Write-Host "`n  ERREUR lors de l'import!" -ForegroundColor Red
    Write-Host "  Consultez le fichier de log: import.log" -ForegroundColor Yellow
    Write-Host "  Fichier filtre conserve: $filteredFile" -ForegroundColor Yellow
    exit 1
}
