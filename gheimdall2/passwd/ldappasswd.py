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

from gheimdall2 import passwd, utils
import ldap

ERR_LDAP = 2

class LdapPasswdEngine(passwd.BaseSyncPasswdEngine):

  # TODO: suppress unnecessary ldap bind
  ldap_user = None

  def hasResetPasswdCapability(self):

    return True

  def _prepare(self, config):
    # This is for standalone use.
    self.ldap_uri = config.get('ldap_uri')
    self.ldap_basedn = config.get('ldap_basedn')
    self.ldap_filter = config.get('ldap_filter')
    self.ldap_rootdn = config.get('ldap_rootdn')
    self.ldap_rootpw = config.get('ldap_rootpw')
    self.ldap_passwd_hash_style = config.get('ldap_passwd_hash_style')

  def _checkLocalUser(self, user_name):
    ldapHandle = None
    try:
      ldapHandle = ldap.initialize(self.ldap_uri)
      ldapHandle.simple_bind_s(who=self.ldap_rootdn, cred=self.ldap_rootpw)
      self.ldap_user = ldapHandle.search_s(
        self.ldap_basedn,
        ldap.SCOPE_SUBTREE,
        self.ldap_filter % utils.ldap_escape(user_name))
      if len(self.ldap_user) != 1:
        try:
          ldapHandle.unbind_s()
        except:
          pass
        del(self.ldap_user)
        raise passwd.PasswdException("ldap search result count is not 1.",
                                     ERR_LDAP)
    except Exception, e:
      if ldapHandle is not None:
        try:
          ldapHandle.unbind_s()
        except:
          pass
      raise passwd.PasswdException(e,ERR_LDAP)
    ldapHandle.unbind_s()
    return True

  def _resetLocalPassword(self, user_name, new_password):
    hashed_pass = utils.hash_password(new_password,
                                      self.ldap_passwd_hash_style)
    ldapHandle = None
    try:
      ldapHandle = ldap.initialize(self.ldap_uri)
      ldapHandle.simple_bind_s(who=self.ldap_rootdn, cred=self.ldap_rootpw)
      ldapHandle.modify_s(self.ldap_user[0][0],
                          [(ldap.MOD_REPLACE, "userPassword", hashed_pass)])
    except Exception, e:
      if ldapHandle is not None:
        try:
          ldapHandle.unbind_s()
        except:
          pass
      raise passwd.PasswdException(e,ERR_LDAP)
    ldapHandle.unbind_s()
    return True

  def _revertLocalPassword(self, user_name):

    old_pass = self.ldap_user[0][1]['userPassword'][0]
    try:
      ldapHandle = ldap.initialize(self.ldap_uri)
      ldapHandle.simple_bind_s(who=self.ldap_rootdn, cred=self.ldap_rootpw)
      ldapHandle.modify_s(self.ldap_user[0][0],
                          [(ldap.MOD_REPLACE, "userPassword", old_pass)])
    except Exception, e:
      if ldapHandle is not None:
        try:
          ldapHandle.unbind_s()
        except:
          pass
      raise passwd.PasswdException(e,ERR_LDAP)
    ldapHandle.unbind_s()
    return True
    
  def _changeLocalPassword(self, user_name, old_password, new_password):
    ldapHandle = None
    try:
      ldapHandle = ldap.initialize(self.ldap_uri)
      result = ldapHandle.search_s(
        self.ldap_basedn,
        ldap.SCOPE_SUBTREE,
        self.ldap_filter % utils.ldap_escape(user_name))
      if len(result) != 1:
        try:
          ldapHandle.unbind_s()
        except:
          pass
        raise passwd.PasswdException("ldap search result count is not 1.",
                                     ERR_LDAP)
      dn = result[0][0]

      # change password
      ldapHandle.simple_bind_s(who=dn, cred=old_password)
      ldapHandle.passwd_s(dn, old_password, new_password)
      ldapHandle.unbind_s()
    except Exception, e:
      if ldapHandle is not None:
        try:
          ldapHandle.unbind_s()
        except:
          pass
      raise passwd.PasswdException(e,ERR_LDAP)
    return True

cls = LdapPasswdEngine
