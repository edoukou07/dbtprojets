from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)


class ReportScheduler(threading.Thread):
    """Thread qui vérifie et envoie les rapports programmés automatiquement"""
    daemon = True  # Le thread s'arrête quand le processus principal s'arrête
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.name = "ReportScheduler"
        
    def run(self):
        """Exécute la vérification des rapports toutes les minutes"""
        logger.info("📧 Scheduler de rapports automatique démarré - Vérification toutes les minutes")
        
        # Attendre un peu au démarrage pour que Django soit complètement initialisé
        time.sleep(5)
        
        while self.running:
            try:
                # Importer ici pour éviter les imports circulaires
                from django.core.management import call_command
                from django.db import connection
                
                # Fermer les connexions DB avant d'exécuter la commande
                connection.close()
                
                # Exécuter le management command silencieusement
                call_command('send_scheduled_reports', verbosity=0)
                
            except Exception as e:
                # Logger l'erreur mais continuer à tourner
                logger.error(f"Erreur dans le scheduler de rapports: {e}", exc_info=True)
            
            # Attendre 60 secondes avant la prochaine vérification
            # On attend par petits incréments pour pouvoir arrêter rapidement
            for _ in range(60):
                if not self.running:
                    break
                time.sleep(1)
        
        logger.info("Scheduler de rapports arrêté")
    
    def stop(self):
        """Arrête le scheduler"""
        self.running = False


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    _scheduler_started = False  # Variable de classe pour éviter les démarrages multiples
    
    def ready(self):
        """Démarre le scheduler automatique au démarrage de Django"""
        # Ne démarrer que si on n'est pas dans une migration
        import sys
        import os
        
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        # En mode développement avec runserver, Django utilise un auto-reloader
        # qui charge l'app deux fois (parent + enfant). On ne démarre que dans le processus enfant.
        # RUN_MAIN est défini uniquement dans le processus enfant (celui qui exécute réellement)
        if 'runserver' in sys.argv and not os.environ.get('RUN_MAIN'):
            # C'est le processus parent du reloader, on ne démarre pas le scheduler
            return
        
        # Éviter de démarrer plusieurs fois
        if AnalyticsConfig._scheduler_started:
            return
        
        # Vérifier si un scheduler est déjà en cours d'exécution
        for thread in threading.enumerate():
            if isinstance(thread, ReportScheduler) and thread.is_alive():
                AnalyticsConfig._scheduler_started = True
                return
        
        # Démarrer le scheduler dans un thread séparé
        try:
            scheduler = ReportScheduler()
            scheduler.start()
            AnalyticsConfig._scheduler_started = True
            logger.info("✅ Scheduler de rapports automatique activé")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du scheduler: {e}", exc_info=True)
