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

ERR_UNKNOWN = 99
NEW_AUTHTOK_REQD = 12

class AuthException(Exception):

  def __init__(self, reason, code):
    self.reason = reason
    self.code = code

  def __str__(self):
    return "%d: %s" % (self.code, self.reason)

class BaseAuthEngine(object):

  def __init__(self, config):
    self._prepare(config)

  def authenticate(self, user_name, password):
    ret = self._authenticate(user_name, password)
    if ret:
      self._postAuthHook(user_name, password)
    return ret

  def _authenticate(self, user_name, password):
    raise NotImplementedError('Child class must implement me.')

  def _postAuthHook(self, user_name, password):
    """ Default: do nothing
    """
    
    pass

  def _prepare(self, config):
    raise NotImplementedError('Child class must implement me.')

cached_engine = None

def createAuthEngine(engine, config):
  global cached_engine
  if cached_engine is None:
    exec('from gheimdall2.auth import %s' % engine)
    cached_engine = eval('%s.cls(config)' % engine)
  return cached_engine
