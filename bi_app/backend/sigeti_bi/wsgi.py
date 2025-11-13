"""
WSGI config for SIGETI BI project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')

application = get_wsgi_application()
