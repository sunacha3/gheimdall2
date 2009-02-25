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

import logging
import cookie_auth

class GrnOpenAuthEngine(cookie_auth.BaseCookieAuthEngine):

  def _authenticate(self, request):
    import urllib
    import base64
    import time

    cookie = request.COOKIES.get(self.cookie_name)
    if cookie is None:
      raise cookie_auth.AuthException('No cookie with cookie_name: %s' %
                                      self.cookie_name)
    decoded_cookie = urllib.unquote_plus(urllib.unquote_plus(cookie))

    shifted_cookie = ''
    for c in decoded_cookie:
      shifted_cookie += chr(ord(c)>>1);

    base64_decoded_cookie = base64.decodestring(shifted_cookie)

    (account, password, expire, md5_string) = base64_decoded_cookie.split(':')

    logging.debug("account: %s" % account)
    logging.debug("password: %s" % password)
    logging.debug("expire: %s" % expire)
    logging.debug("md5_string: %s" % md5_string)

    try:
      import md5
      m = md5.new()
    except:
      import hashlib
      m = hashlib.md5()

    md5_src = "%s:%s:%s:%s" % (
      account, password, expire, self.magic
    )

    m.update(md5_src)
    created_md5 = m.hexdigest()

    if created_md5 != md5_string:
      raise cookie_auth.AuthException("MD5 checksum does not match.")

    if password != self.system_password:
      raise cookie_auth.AuthException("System Password does not match.")

    timestamp = time.time()

    if expire < timestamp:
      raise cookie_auth.AuthException("Cookie is expired.")
    return account


  def _prepare(self, config):
    self.magic = config.get('grn_openauth_magic')
    self.system_password = config.get('grn_openauth_system_password')
    self.cookie_name = config.get('grn_openauth_cookie_name')

cls = GrnOpenAuthEngine
