import os

from django import template
from random import randint
from urllib import quote_plus

from gheimdall2.conf import config

register = template.Library()

@register.simple_tag
def ga():
  ga_account = config.get("ga_account")
  if ga_account:
    return """<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%%3E%%3C/script%%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("%s");
pageTracker._trackPageview();
} catch(err) {}</script>""" % ga_account
  else:
    return ""

@register.simple_tag
def ga_mobile(request):
  """
  Returns the image link for tracking this mobile request.
    
  Retrieves two configurations from gheimdall2.conf.config:
    
  ga_pixel_url: url to location of your tracking CGI.
  ga_mobile_account: your GA mobile account number such as MO-XXXXXX-XX
  
  """

  r = str(randint(0, 0x7fffffff))

  ga_pixel_url = config.get("ga_pixel_url")
  ga_mobile_account = config.get("ga_mobile_account")
  if ga_pixel_url is None or ga_mobile_account is None or \
        ga_mobile_account == "":
    return ''

  referer = quote_plus(request.META.get('HTTP_REFERER', '-'))

  path = quote_plus(request.get_full_path())
    
  src = ga_pixel_url + \
   "?utmac=" + ga_mobile_account + \
   "&utmn=" + r + \
   "&utmr=" + referer + \
   "&utmp=" + path + \
   "&guid=ON"

  return '<img src="%s" width="1" height="1">' % src
