#!/bin/bash
# Script pour envoyer automatiquement les rapports programmés
# À exécuter périodiquement via cron (toutes les minutes recommandé)

cd "$(dirname "$0")"
python manage.py send_scheduled_reports

