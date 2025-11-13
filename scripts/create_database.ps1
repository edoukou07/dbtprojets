# Script pour créer la base de données DWH si elle n'existe pas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Création base de données DWH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_DIR = "C:\Users\hynco\Desktop\DWH_SIG"

# Charger les variables d'environnement
if (-not (Test-Path "$PROJECT_DIR\.env")) {
    Write-Host "❌ Fichier .env non trouvé" -ForegroundColor Red
    Write-Host "   Copiez .env.example vers .env et configurez-le" -ForegroundColor Yellow
    exit 1
}

# Charger .env
Get-Content "$PROJECT_DIR\.env" | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Host: $env:DWH_DB_HOST" -ForegroundColor Cyan
Write-Host "  Port: $env:DWH_DB_PORT" -ForegroundColor Cyan
Write-Host "  User: $env:DWH_DB_USER" -ForegroundColor Cyan
Write-Host "  Database: sigeti_dwh" -ForegroundColor Cyan
Write-Host ""

# Définir le mot de passe pour psql
$env:PGPASSWORD = $env:DBT_PASSWORD

# Vérifier la connexion PostgreSQL
Write-Host "1. Test de connexion PostgreSQL..." -ForegroundColor Yellow
try {
    $version = psql -U $env:DWH_DB_USER -h $env:DWH_DB_HOST -p $env:DWH_DB_PORT -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Connexion échouée"
    }
    Write-Host "✅ Connexion PostgreSQL réussie" -ForegroundColor Green
} catch {
    Write-Host "❌ Impossible de se connecter à PostgreSQL" -ForegroundColor Red
    Write-Host "   Vérifiez :" -ForegroundColor Yellow
    Write-Host "   - PostgreSQL est démarré" -ForegroundColor White
    Write-Host "   - L'utilisateur '$env:DWH_DB_USER' existe" -ForegroundColor White
    Write-Host "   - Le mot de passe dans .env est correct" -ForegroundColor White
    Write-Host "   - pg_hba.conf autorise les connexions locales" -ForegroundColor White
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    exit 1
}
Write-Host ""

# Vérifier si la base existe
Write-Host "2. Vérification de la base 'sigeti_dwh'..." -ForegroundColor Yellow
$dbList = psql -U $env:DWH_DB_USER -h $env:DWH_DB_HOST -p $env:DWH_DB_PORT -lqt 2>&1

if ($dbList -match "sigeti_dwh") {
    Write-Host "ℹ️  La base de données 'sigeti_dwh' existe déjà" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Voulez-vous la SUPPRIMER et la RECRÉER ? (O/N)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "O" -or $response -eq "o") {
        Write-Host ""
        Write-Host "⚠️  ATTENTION: Toutes les données seront perdues!" -ForegroundColor Red
        Write-Host "Tapez 'OUI SUPPRIMER' pour confirmer:" -ForegroundColor Yellow
        $confirm = Read-Host
        
        if ($confirm -eq "OUI SUPPRIMER") {
            Write-Host ""
            Write-Host "Suppression de la base..." -ForegroundColor Yellow
            psql -U $env:DWH_DB_USER -h $env:DWH_DB_HOST -p $env:DWH_DB_PORT -c "DROP DATABASE IF EXISTS sigeti_dwh;" 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Base supprimée" -ForegroundColor Green
            } else {
                Write-Host "❌ Erreur lors de la suppression" -ForegroundColor Red
                Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
                exit 1
            }
        } else {
            Write-Host "❌ Suppression annulée" -ForegroundColor Red
            Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
            exit 0
        }
    } else {
        Write-Host "✅ Conservation de la base existante" -ForegroundColor Green
        Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
        exit 0
    }
}
Write-Host ""

# Créer la base de données
Write-Host "3. Création de la base 'sigeti_dwh'..." -ForegroundColor Yellow
try {
    psql -U $env:DWH_DB_USER -h $env:DWH_DB_HOST -p $env:DWH_DB_PORT -c "CREATE DATABASE sigeti_dwh ENCODING 'UTF8' LC_COLLATE='fr_FR.UTF-8' LC_CTYPE='fr_FR.UTF-8';" 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Base de données 'sigeti_dwh' créée avec succès" -ForegroundColor Green
    } else {
        throw "Erreur lors de la création"
    }
} catch {
    Write-Host "❌ Impossible de créer la base de données" -ForegroundColor Red
    Write-Host "   Erreur: $_" -ForegroundColor Yellow
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    exit 1
}
Write-Host ""

# Vérifier la création
Write-Host "4. Vérification..." -ForegroundColor Yellow
$dbCheck = psql -U $env:DWH_DB_USER -h $env:DWH_DB_HOST -p $env:DWH_DB_PORT -d sigeti_dwh -c "SELECT current_database();" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Connexion à 'sigeti_dwh' réussie" -ForegroundColor Green
} else {
    Write-Host "⚠️  Impossible de se connecter à la base créée" -ForegroundColor Yellow
}

# Nettoyer
Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Base de données prête !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prochaines étapes:" -ForegroundColor Yellow
Write-Host "1. Tester dbt: dbt debug" -ForegroundColor White
Write-Host "2. Lancer le DWH: .\scripts\run_flow.ps1 -FlowType full" -ForegroundColor White
Write-Host ""
