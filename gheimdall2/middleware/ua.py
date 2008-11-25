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
