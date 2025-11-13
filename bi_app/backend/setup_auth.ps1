# Script pour installer les dépendances d'authentification Django
Write-Host "Configuration de l'authentification SIGETI BI..." -ForegroundColor Cyan

# Activer l'environnement virtuel
& "..\..\venv\Scripts\Activate.ps1"

# Appliquer les migrations Django
Write-Host "`nApplication des migrations Django..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "`nCréation des utilisateurs de test..." -ForegroundColor Yellow
Get-Content create_test_users.py | python manage.py shell

Write-Host "`n✅ Configuration terminée!" -ForegroundColor Green
Write-Host "`nUtilisateurs de test créés:" -ForegroundColor Cyan
Write-Host "- admin@sigeti.ci / admin123" -ForegroundColor White
Write-Host "- finance@sigeti.ci / finance123" -ForegroundColor White
Write-Host "- ops@sigeti.ci / ops123" -ForegroundColor White
Write-Host "- direction@sigeti.ci / direction123" -ForegroundColor White
