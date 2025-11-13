"""
ASGI config for SIGETI BI project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')

application = get_asgi_application()
