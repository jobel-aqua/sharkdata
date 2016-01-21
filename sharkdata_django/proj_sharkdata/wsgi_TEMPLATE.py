"""
Template for the Django WSGI file. Django version 1.6.1.
- Replace 'proj_sharkdata' if the django project folder has a different name.
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj_sharkdata.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
