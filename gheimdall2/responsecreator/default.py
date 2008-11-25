#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   GHeimdall - A small web application for Google Apps SSO service.
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
#   $Id: default.py 72 2007-11-27 08:15:31Z matsuo.takashi $

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

import saml2
import saml2.utils
import xmldsig as ds
from saml2 import saml, samlp
from gheimdall2 import responsecreator

class DefaultResponseCreator(responsecreator.ResponseCreator):

  def _getNameID(self):
    return saml.NameID(format=saml.NAMEID_FORMAT_EMAILADDRESS,
                       text=self.user_name+"@"+self.config.get("apps_domain"))

  def _prepare(self, config):
    self.config = config

cls = DefaultResponseCreator
