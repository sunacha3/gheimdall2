#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   GHeimdall2 - A small web application for Google Apps SSO service.
#   Copyright (C) 2007 SIOS Technology, Inc.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
#   USA.
#
#   $Id: ldapauth.py 2 2007-07-20 03:11:43Z matsuo.takashi $

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

from gheimdall2 import auth, utils
import ldap

ERR_LDAP = 2

class LdapAuthEngine(auth.BaseAuthEngine):

  def _prepare(self, config):
    # This is for standalone use.
    self.ldap_uri = config.get('ldap_uri')
    self.ldap_basedn = config.get('ldap_basedn')
    self.ldap_filter = config.get('ldap_filter')

  def _authenticate(self, user_name, password):
    ldapHandle = None
    try:
      ldapHandle = ldap.initialize(self.ldap_uri)
      result = ldapHandle.search_s(
        self.ldap_basedn,
        ldap.SCOPE_SUBTREE,
        self.ldap_filter % utils.ldap_escape(user_name))
      if len(result) != 1:
        ldapHandle.unbind_s()
        raise auth.AuthException("ldap search result count is not 1.",
                                 ERR_LDAP)
      dn = result[0][0]

      # authenticate
      ldapHandle.simple_bind_s(who=dn, cred=password)
      ldapHandle.unbind_s()
    except Exception, e:
      if ldapHandle is not None:
        try:
          ldapHandle.unbind_s()
        except:
          pass
      raise auth.AuthException(e,ERR_LDAP)
    return True

cls = LdapAuthEngine
