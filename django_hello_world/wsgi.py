"""
WSGI config for django_hello_world project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_hello_world.settings')

application = get_wsgi_application() 