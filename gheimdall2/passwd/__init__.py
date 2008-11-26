#!/usr/bin/python
# -*- coding: utf-8 -*-
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

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom
import gdata.apps
import gdata.apps.service
import sha
from gheimdall2 import appsclient
import logging
from gheimdall2 import utils

ERR_UNKNOWN = 99
ERR_FATAL = 98

class PasswdException(Exception):
  def __init__(self, reason, code=ERR_UNKNOWN):
    self.reason = reason
    self.code = code

  def __str__(self):
    return "%d: %s" % (self.code, self.reason)

class BasePasswdEngine(object):

  def __init__(self, config):
    self._prepare(config)
    
  def hasResetPasswdCapability(self):

    return False

  def changePassword(self, user_name, old_password, new_password):
    self._changeLocalPassword(user_name, old_password, new_password)
    try:
      self._changeGooglePassword(user_name, new_password)
    except Exception, e1:
      try: 
        self._changeLocalPassword(user_name, new_password, old_password)
      except Exception, e2:
        raise PasswdException("Failed rollback password. " + str(e2),
                              ERR_FATAL)
      else:
        raise PasswdException("Failed to change google password. " + str(e1),
                              ERR_FATAL)
    return True

  def resetPassword(self, user_name):

    self._retrieveGoogleUser(user_name)
    self._checkLocalUser(user_name)
    new_password = utils.generate_random_password()
    self._resetLocalPassword(user_name, new_password)
    try:
      self._changeGooglePassword(user_name, new_password)
    except Exception, e1:
      try:
        self._revertLocalPassword(user_name)
      except Exception, e2:
        raise PasswdException("Failed rollback password. " + str(e2),
                              ERR_FATAL)
      else:
        raise PasswdException("Failed to change google password. " + str(e1),
                              ERR_FATAL)
    return new_password

  def _changeGooglePassword(self, user_name, new_password):

    return True

  def _changeLocalPassword(self, user_name, old_password, new_password):

    raise NotImplementedError('Child class must implement me.')

  def _checkGoogleUser(self, user_name):

    return True

  def _checkLocalUser(self, user_name):

    raise NotImplementedError('Child class must implement me.')

  def _revertLocalPassword(self, user_name):

    raise NotImplementedError('Child class must implement me.')
    
  def _resetLocalPassword(self, user_name, new_password):

    raise NotImplementedError('Child class must implement me.')

  def _prepare(self, config):
    raise NotImplementedError('Child class must implement me.')

class BaseSyncPasswdEngine(BasePasswdEngine):
  max_trial = 5
  target_user = None
  
  def __init__(self, config):
    self.domain = config.get('apps_domain')
    self.domain_admin = config.get('domain_admin')
    self.admin_passwd = config.get('admin_passwd')
    self.hash_function_name = config.get('hash_function_name')
    self.pickle_directory = config.get('var_directory')
    self.ready = False
    self._prepare(config)

  def _login(self):

    try:
      email = self.domain_admin + '@' + self.domain
      self.apps_client = appsclient.getAppsClient(email, self.domain,
                                                  self.admin_passwd,
                                                  'gheimdall',
                                                  self.pickle_directory)
      self.ready = True
    except Exception, e:
      logging.error(e)
      raise
    
  def _changeLocalPassword(self, user_name, old_password, new_password):
    raise NotImplementedError('Child class must implement me.')

  def _prepare(self, config):
    raise NotImplementedError('Child class must implement me.')

  def _retrieveGoogleUser(self, user_name, num_tried=0):
    if self.target_user is not None:
      return True
    
    if num_tried > self.max_trial:
      raise PasswdException('Can not retrieve user: %s.' % user_name,
                            ERR_FATAL)
    try:
      if not self.ready:
        self._login()
      self.target_user = self.apps_client.RetrieveUser(user_name)
    except Exception, e:
      logging.debug(e.args)
      if (isinstance(e, gdata.apps.service.AppsForYourDomainException) and
          e.error_code == gdata.apps.service.UNKOWN_ERROR):
        return self._retrieveGoogleUser(user_name, num_tried+1)
      self._cleanup()
      raise PasswdException('Can not retrieve user: %s.' % user_name,
                            ERR_FATAL)
    return True

  def _changeGooglePassword(self, user_name, new_password):

    try:
      if not self.ready:
        self._login()
      self._retrieveGoogleUser(user_name)
      if self.hash_function_name == 'SHA-1':
        sha_obj = sha.new(new_password)
        self.target_user.login.password = sha_obj.hexdigest()
        self.target_user.login.hash_function_name = 'SHA-1'
      else:
        self.target_user.login.password = new_password
      self.target_user = self.apps_client.UpdateUser(user_name,
                                                     self.target_user)
    except Exception,e:
      self._cleanup()
      logging.error(e)
      raise

    self._cleanup()
    return True

  def _cleanup(self):

    del(self.apps_client)
    self.ready = False

cached_engine = None

def createPasswdEngine(engine, config):
  global cached_engine
  if cached_engine is None:
    exec('from gheimdall2.passwd import %s' % engine)
    cached_engine = eval('%s.cls(config)' % engine)
  return cached_engine
