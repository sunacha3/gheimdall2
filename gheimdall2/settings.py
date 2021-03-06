# Django settings for gheimdall2 project.
#
#   GHeimdall2 - A small web application for Google Apps SSO service.
#   Copyright (C) 2008 SIOS Technology, Inc.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

import logging
import os

# For plugins for gheimdall.
import sys
try:
  import gheimdall2
  sys.modules['gheimdall'] = sys.modules['gheimdall2']
except:
  pass

DEBUG = False
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1')

#CONFDIR = os.path.join(os.path.dirname(__file__), 'conf')
CONFDIR = '/etc/gheimdall2'
EXTCONFDIR = os.path.join(CONFDIR, "conf.d")
CONFFILE = 'gheimdall2.conf'

file_logger = logging.FileHandler("/var/log/gheimdall2/error.log")
file_logger.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s: %(pathname)s: %(lineno)d: %(name)s: %(levelname)s: %(message)s')
file_logger.setFormatter(formatter)
logging.getLogger('').addHandler(file_logger)
logging.getLogger().setLevel(logging.WARN)

ADMINS = (
    ('admin', 'root@localhost'),
)

MANAGERS = ADMINS

EMAIL_HOST = 'localhost'

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB"}
DATABASE_NAME = '/var/gheimdall2/gheimdall2.sqlite'             # Or path to database file if using sqlite3.
DATABASE_USER = 'gheimdall2'             # Not used with sqlite3.
DATABASE_PASSWORD = 'gheimdall2'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
if DEBUG:
  MEDIA_URL = '/gheimdall2/static/'
else:
  MEDIA_URL = '/gheimdall2/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h#xua$vzc)zzglgosc(!!c8xkctjluxsvo!6rp!%q=9wgwoza0'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.load_template_source',
  'django.template.loaders.app_directories.load_template_source',
#   'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
  'gheimdall2.middleware.handle_exception.StandardExceptionMiddleware',
  'gheimdall2.middleware.cache_control.CacheControlMiddleware',
  'gheimdall2.middleware.ua.UserAgentMobileMiddleware',
  'django.middleware.locale.LocaleMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  #'djangologging.middleware.LoggingMiddleware',
)

ROOT_URLCONF = 'gheimdall2.urls'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
)

MOBILE_TEMPLATE_DIR = 'mobile'

INSTALLED_APPS = (
  'django.contrib.sessions',
  'gheimdall2.idp',
)

STATIC_DOC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'static')

#FORCE_SCRIPT_NAME = "/gheimdall2"
SESSION_COOKIE_NAME = 'gh2sessionid'
SESSION_COOKIE_SECURE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = '/var/gheimdall2/session'

LOG_CRITICAL_TO_FILE = True
