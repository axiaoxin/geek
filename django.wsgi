import os
import sys
import django.core.handlers.wsgi

sys.path.append(r'C:') #/path/to/project

os.environ['DJANGO_SETTINGS_MODULE'] = 'geek.settings'
application = django.core.handlers.wsgi.WSGIHandler()
