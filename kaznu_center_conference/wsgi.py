import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaznu_center_conference.settings')

application = get_wsgi_application()
