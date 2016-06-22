# Script to be used for opening a shell session from ipython

import os
import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vinosite.settings")
from django.conf import settings
from vinosite import settings

