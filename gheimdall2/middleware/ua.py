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
print sys.path
from uamobile import detect, exceptions

class UserAgentMobileMiddleware(object):
  def process_request(self, request):
    try:
      request.device = detect(request.META)
      if request.device.is_nonmobile():
        request.is_mobile = False
      else:
        request.is_mobile = True
    except exceptions.NoMatchingError, e:
      request.is_mobile = False

  def process_response(self, request, response):
    if request.is_mobile and (request.device.is_docomo() or request.device.is_ezweb()):
      if response['Content-Type'].startswith("text/html"):
        response['Content-Type'] = 'text/html; charset=SHIFT-JIS'
        response.content = unicode(response.content, 'utf-8').encode('cp932')
        return response
    return response
