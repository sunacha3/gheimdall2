import os, sys
#sys.path.append('/some/where/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'gheimdall2.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
