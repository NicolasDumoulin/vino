"""
WSGI config for vinosite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os, sys

sys.path.insert(0,"/var/local/Django-1.8.4")
sys.path.append("/var/www/vino/vinosite/")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vinosite.settings")

application = get_wsgi_application()

