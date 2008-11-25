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
#   $Id: sample.py 2 2007-07-20 03:11:43Z matsuo.takashi $

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

from gheimdall2 import auth

class SampleAuthEngine(auth.BaseAuthEngine):

  def _prepare(self, config):
    pass

  def _authenticate(self, user_name, password):
    if password == 'good':
      return True
    else:
      raise auth.AuthException('login failure', auth.ERR_UNKNOWN)

cls = SampleAuthEngine
