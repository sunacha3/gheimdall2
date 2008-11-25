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
#   $Id: pam.py 2 2007-07-20 03:11:43Z matsuo.takashi $

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

from gheimdall import passwd
import PAM
import re

def pam_conv(auth, query_list):
  resp = []
  regex = re.compile(".*new.+password.*", re.I)    
  for i in range(len(query_list)):
    query, type = query_list[i]
    if type == PAM.PAM_PROMPT_ECHO_ON or type == PAM.PAM_PROMPT_ECHO_OFF:
      data = auth.get_userdata()
      if regex.match(query):
        resp.append((data.get('new_password'), 0))
      else:
        resp.append((data.get('old_password'), 0))
    elif type == PAM.PAM_ERROR_MSG or type == PAM.PAM_TEXT_INFO:
      resp.append(('', 0));
    else:
      return None
  return resp

class PamPasswdEngine(passwd.BaseSyncPasswdEngine):

  def _changeLocalPassword(self, user_name, old_password, new_password):
    pam = PAM.pam()
    pam.start(self.appname)
    pam.set_item(PAM.PAM_USER, user_name)
    pam.set_item(PAM.PAM_CONV, pam_conv)
    pam.set_userdata(dict(old_password=old_password,
                          new_password=new_password))
    try:
      pam.chauthtok()
    except PAM.error, args:
      pam.close_session()
      raise passwd.PasswdException(args[0])
    except Exception, e:
      pam.close_session()
      raise passwd.PasswdException(e.__str__(), passwd.ERR_UNKNOWN)
    else:
      pam.close_session()
      return True

  def _prepare(self, config):
    # This is for standalone use.
    self.appname = config.get('apps.pam_appname')

cls = PamPasswdEngine
