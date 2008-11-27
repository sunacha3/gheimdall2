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

import saml2
import saml2.utils
import xmldsig as ds
from saml2 import saml, samlp
from gheimdall2 import responsecreator

class DefaultResponseCreator(responsecreator.ResponseCreator):

  def _getNameID(self):
    if self.user_name.find('@') >= 0:
      user_name = self.user_name
    else:
      user_name = self.user_name+"@"+self.config.get("apps_domain")
    return saml.NameID(format=saml.NAMEID_FORMAT_EMAILADDRESS,
                       text=user_name)

  def _prepare(self, config):
    self.config = config

cls = DefaultResponseCreator
