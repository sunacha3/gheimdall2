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
#   $Id: $

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

STATUS_NONE = None
STATUS_LOGIN = 1
STATUS_LOGOUT_START = 2
STATUS_LOGOUT_SUCCESS = 4
STATUS_LOGOUT_FAIL = 8

class ServiceProvider(object):

  def __init__(self, name, status, assertion_id, name_id, logout_status=None):
    self.name = name
    self.status = status
    self.assertion_id = assertion_id
    self.name_id = name_id
    self.logout_status = None
