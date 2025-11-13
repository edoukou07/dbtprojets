# =====================================================================
# Script: copy_source_to_dwh.ps1
# Description: Copie les tables sources de sigeti_node_db vers sigeti_dwh
# =====================================================================

$env:PGPASSWORD = "postgres"
$sourceDB = "sigeti_node_db"
$targetDB = "sigeti_dwh"
$pgUser = "postgres"

Write-Host "[INFO] Copie des tables sources vers $targetDB..." -ForegroundColor Cyan

# Liste des tables à copier
$tables = @(
    "entreprises",
    "lots", 
    "zones_industrielles",
    "factures",
    "paiement_factures",
    "collectes",
    "demandes_attribution",
    "domaines_activites"
)

foreach ($table in $tables) {
    Write-Host "[STEP] Copie de la table: $table" -ForegroundColor Yellow
    
    # Export depuis source
    $dumpFile = "$env:TEMP\$table.sql"
    
    pg_dump -U $pgUser -h localhost -d $sourceDB -t $table --data-only --column-inserts -f $dumpFile 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        # Import vers target
        psql -U $pgUser -h localhost -d $targetDB -f $dumpFile 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $table copiee avec succes" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Erreur import $table (peut-etre table existe deja)" -ForegroundColor Yellow
        }
        
        Remove-Item $dumpFile -Force
    } else {
        Write-Host "  [ERROR] Export de $table a echoue" -ForegroundColor Red
    }
}

Write-Host "`n[SUCCESS] Copie terminee!" -ForegroundColor Green
Write-Host "[INFO] Verification du nombre de lignes dans $targetDB..." -ForegroundColor Cyan

# Vérification
foreach ($table in $tables) {
    $count = psql -U $pgUser -h localhost -d $targetDB -t -c "SELECT COUNT(*) FROM $table;" 2>$null
    if ($count) {
        Write-Host "  - $table : $($count.Trim()) lignes" -ForegroundColor White
    }
}

$env:PGPASSWORD = ""
