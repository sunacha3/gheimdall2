#!/usr/bin/env python

from distutils.core import setup

setup(name='GHeimdall2',
      version='1.0',
      description='GHeimdall2',
      author='Takashi Matsuo',
      author_email='tmatsuo@shehas.net',
      url='http://code.google.com/p/gheimdall2/',
      packages=['gheimdall2', 'gheimdall2.conf', 'gheimdall2.auth',
                'gheimdall2.idp', 'gheimdall2.middleware',
                'gheimdall2.passwd', 'gheimdall2.responsecreator'],
      package_data={'gheimdall2': ['locale/*/LC_MESSAGES/django.??',
                                   'conf/gheimdall2.conf', 'static/css/main.css',
                                   'static/images/*.png', 'templates/mobile/idp/*.html',
                                   'templates/*.html', 'templates/idp/*.html']},
     )

