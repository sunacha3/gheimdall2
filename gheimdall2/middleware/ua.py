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

import sys
import logging

from IPy import IP
from uamobile import (
  detect, cidr
)
try:
  from uamobile.exceptions import NoMatchingError
except Exception:
  pass
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseForbidden

from gheimdall2.conf import config
from gheimdall2.utils import import_string

class UserAgentMobileMiddleware(object):
  def process_request(self, request):
    try:
      request.device = detect(request.META)
      if request.device.is_nonmobile():
        request.is_mobile = False
      else:
        request.is_mobile = True
    except NoMatchingError, e:
      request.is_mobile = False

  def process_response(self, request, response):
    if request.is_mobile and (request.device.is_docomo() or request.device.is_ezweb()):
      if response['Content-Type'].startswith("text/html"):
        response['Content-Type'] = 'text/html; charset=SHIFT-JIS'
        response.content = unicode(response.content, 'utf-8').encode('cp932')
        return response
    return response


class MobileUidAccessControlMiddleware(object):
  def __init__(self):
    try:
      clsname = config.get("mobile_access_control_class")
      if clsname is None:
        raise RuntimeError("You must set mobile_access_control_class"
                           " properly.")
      cls = import_string(clsname)
      self.access_controller = cls(config)
    except Exception, e:
      raise ImproperlyConfigured(e)

  def process_request(self, request):
    if not hasattr(request, "device"):
      raise ImproperlyConfigured("You must use UserAgentMobileMiddleware.")

    is_full_browser = False
    client_ip = request.META.get(
      'HTTP_X_FORWARDED_FOR',
      request.META.get(
        'HTTP_CLIENT_IP',
        request.META.get('REMOTE_ADDR', None)))
    if client_ip.find(",") >= 0:
      client_ip = client_ip[:client_ip.find(",")]
    if client_ip is None:
      logging.debug("Cant get client's ip.")
      return HttpResponseForbidden("Cant get your ip.")
    sb_fullbrowser_ips = [IP("123.108.237.224/27"), IP("202.253.96.0/28")]
    for iprange in sb_fullbrowser_ips:
      if client_ip in iprange:
        import re
        m = re.match(r'.*SN(\d+).*', request.device.useragent)
        if m:
          setattr(request.device, 'serialnumber', m.groups()[0])
          is_full_browser = True
        else:
          logging.debug("Client is softbank with full browser presumably,"
                        " and cant get the serialnumber")
          return HttpResponseForbidden("Your mobile phone is not allowed.")
    docomo_ips = cidr.get_ip('docomo')
    docomo_ips.append(IP("210.153.87.0/24"))
    for iprange in docomo_ips:
      if client_ip in iprange and request.device.is_nonmobile():
        logging.debug("Client is docomo with full browser presumably,"
                      " access rejected.")
        return HttpResponseForbidden("Your mobile phone is not allowed.")
    if request.device.is_nonmobile() and is_full_browser is False:
      return
    if self.access_controller.check_authorization(request):
      return
    else:
      return HttpResponseForbidden("Your mobile phone is not allowed.")
