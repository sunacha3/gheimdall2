#!/usr/bin/env python
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

from distutils.core import setup

setup(name='GHeimdall2',
      version='1.0',
      description='GHeimdall2',
      author='Takashi Matsuo',
      author_email='tmatsuo@shehas.net',
      url='http://code.google.com/p/gheimdall2/',
      packages=['gheimdall2', 'gheimdall2.conf', 'gheimdall2.auth',
                'gheimdall2.cookie_auth',
                'gheimdall2.cryptAES',
                'gheimdall2.idp', 'gheimdall2.middleware',
                'gheimdall2.idp.templatetags',
                'gheimdall2.passwd', 'gheimdall2.responsecreator'],
      package_data={'gheimdall2': ['locale/*/LC_MESSAGES/django.??',
                                   'conf/gheimdall2.conf', 'static/css/main.css',
                                   'static/images/*.png', 'templates/mobile/idp/*.html',
                                   'templates/*.html', 'templates/idp/*.html']},
     )

