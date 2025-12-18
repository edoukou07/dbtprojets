@echo off
REM Script Windows pour envoyer automatiquement les rapports programmés
REM À exécuter périodiquement via Task Scheduler (toutes les minutes recommandé)

cd /d "%~dp0"
python manage.py send_scheduled_reports

