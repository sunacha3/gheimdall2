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

import logging, sys
import zlib, base64, sha, md5
import saml2
import xmldsig as ds
import time, random
import crypt
from saml2 import saml, samlp
from saml2 import utils as samlutils
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from gheimdall2 import const, sp, responsecreator, errors
from gheimdall2.conf import config
from gheimdall2.errors import GHException

if sys.version_info < (2,4):
  b64decode = base64.decodestring
else:
  b64decode = base64.b64decode

def ldap_escape(data):
  data = data.replace('*', '\\2a')
  data = data.replace('(', '\\28')
  data = data.replace(')', '\\29')
  data = data.replace('\\', '\\5c')
  return data

def hash_password(password, hash_style):
  if hash_style == '{SHA}':
    return hash_style + base64.b64encode(sha.new(password).digest())
  elif hash_style == '{MD5}':
    return hash_style + base64.b64encode(md5.new(password).digest())
  elif hash_style == '{CRYPT}':
    chars = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    rng = random.Random()
    salt = rng.choice(chars) + rng.choice(chars)
    return hash_style + crypt.crypt(password, salt)
  elif hash_style == '{CLEARTEXT}':
    return password

  raise NotImplementedError('hash style is not implemented: %s.' % hash_style)

righthand = '6789yuiophjknmYUIPHJKLNM'
lefthand = '2345qwertasdfgzxcvbQWERTASDFGZXCVB'
allchars = righthand + lefthand

def generate_random_password(length=8, alternate_hands=True):
  rng = random.Random()
  ret = ''
  for i in range(length):
    if not alternate_hands:
      ret += rng.choice(allchars)
    else:
      if i%2:
        ret += rng.choice(lefthand)
      else:
        ret += rng.choice(righthand)
  return ret

def is_user_authenticated(request):
  if request.session.get(const.REMEMBER_ME) and \
        request.session.get(const.AUTHENTICATED):
    auth_time = request.session.get(const.AUTH_TIME, 0)
    valid_time = request.session.get(const.VALID_TIME, 0)
    now = time.time()
    if auth_time < now and now < valid_time:
      return True
  return False

def get_template_list(request, path):
  if request.is_mobile:
    return [settings.MOBILE_TEMPLATE_DIR + '/' + path, path]
  else:
    return [path]

def gh_get_template(request, path):
  return loader.select_template(get_template_list(request, path))

def get_flash(request):
  ret = request.session.get(const.FLASH, None)
  try:
    del request.session[const.FLASH]
  except KeyError:
    pass
  return ret

def get_domain(request):
  user_name = request.session.get(const.USER_NAME)
  if user_name and user_name.find('@') >= 0:
    return user_name[user_name.find('@')+1:]
  return config.get('apps_domain')

def get_static_login_url(request):
  service = request.POST.get('service', 'mail')
  schema = request.POST.get('schema', 'https')
  baseURL = request.POST.get('base_url')
  if schema != 'http' and schema != 'https':
    schema = 'https'
  #if baseURL:
  #  return baseURL
  elif service == 'docs':
    return '%s://docs.google.com/a/%s' % (schema, get_domain(request))
  elif service == 'calendar':
    return '%s://www.google.com/calendar/a/%s' % (schema, get_domain(request))
  elif service == 'startpage':
    logging.warn("service 'startpage' is not supported by static_login")
  elif service == 'sites':
    logging.warn("service 'sites' is not supported by static_login")
  return '%s://mail.google.com/a/%s' % (schema, get_domain(request))

def init_session(request, user_name):
  request.session.flush()
  request.session[const.USER_NAME] = user_name
  request.session[const.AUTHENTICATED] = True
  if config.get('always_remember_me') or request.POST.get('remember_me'):
    if not config.get('use_header_auth'):
      request.session[const.REMEMBER_ME] = True

def create_saml_response(request, authn_request, RelayState, user_name,
                         set_time=True):
  """ Returns HttpResponse object
  """

  acsURL = authn_request.assertion_consumer_service_url
  issuer = authn_request.issuer.text.strip()
  creators = config.get('response_creators', dict())
  module_name = creators.get(issuer)
  if module_name is None:
    module_name = config.get("default_response_creator","default")
  response_creator = responsecreator.create(module_name, config)

  if set_time:
    auth_time = time.time()
    valid_time = auth_time + config.get('session_lifetime')
  else:
    auth_time = request.session.get(const.AUTH_TIME)
    valid_time = request.session.get(const.VALID_TIME)

  # create saml response
  saml_response = response_creator.createAuthnResponse(user_name,
                                                       authn_request,
                                                       valid_time,
                                                       auth_time,
                                                       acsURL,
                                                       request)
  if request.session.get(const.ISSUERS, None) is None:
    request.session[const.ISSUERS] = {}

  request.session[const.ISSUERS][issuer] = sp.ServiceProvider(
    name=issuer, status=sp.STATUS_LOGIN,
    assertion_id=saml_response.assertion[0].id,
    name_id=saml_response.assertion[0].subject.name_id)
  request.session.modified = True

  if issuer.startswith('google.com') and RelayState is not None and \
         RelayState.find('continue=https') >= 0:
    request.session[const.USE_SSL] = True

  if set_time:
    request.session[const.AUTH_TIME] = auth_time
    request.session[const.VALID_TIME] = valid_time  

  if authn_request.protocol_binding == saml2.BINDING_HTTP_POST:
    signed_response = saml2.utils.sign(saml_response.ToString(),
                                       config.get('privkey_filename'))
    encoded_response = base64.encodestring(signed_response)
    t = gh_get_template(request,'idp/login-success.html')
    c = RequestContext(request, {'acsURL': acsURL,
                                 'SAMLResponse': encoded_response,
                                 'RelayState': RelayState})
    return HttpResponse(t.render(c))
  else:
    raise NotImplementedError("Specified binding not supported. Binding: %s" %
                              authn_request.protocol_binding)

def create_authn_request(SAMLRequest, RelayState, meth):
  try:
    try:
      xml = zlib.decompress(b64decode(SAMLRequest), -8)
    except:
      xml = zlib.decompress(b64decode(SAMLRequest))
  except:
    xml = b64decode(SAMLRequest)
  ret = meth(xml)
  return (ret, RelayState)

def parse_saml_request(request, meth):
  if request.method == "GET":
    SAMLRequest = request.GET.get("SAMLRequest", None)
    RelayState = request.GET.get("RelayState", None)
  elif request.method == "POST":
    SAMLRequest = request.POST.get("SAMLRequest", None)
    RelayState = request.POST.get("RelayState", None)
  return create_authn_request(SAMLRequest, RelayState, meth)

def extract_logout_data(request):
  SAMLRequest = request.REQUEST.get("SAMLRequest", None)
  SAMLResponse = request.REQUEST.get("SAMLResponse", None)
  RelayState = request.REQUEST.get("RelayState", None)
  return (SAMLRequest, SAMLResponse, RelayState)

def clear_user_session(request):
  request.session[const.REMEMBER_ME] = False
  request.session[const.AUTHENTICATED] = False
  request.session[const.AUTH_TIME] = 0
  request.session[const.VALID_TIME] = 0

def handle_logout_from_google(request):
  # first check if there is google apps session
  google_session = None
  for key, issuer in request.session[const.ISSUERS].iteritems():
    if key.startswith("google.com"):
      google_session = key
  if google_session is None:
    logging.debug("No Google Apps session")
    clear_user_session(request)
    request.session[const.ORIGINAL_ISSUER] = 'google.com'
    return
  if request.session[const.ISSUERS][google_session].status == \
        sp.STATUS_LOGOUT_START:
    logging.debug("Assumed that logout from Google Apps was succeeded.")
    request.session[const.ISSUERS][google_session].status = \
        sp.STATUS_LOGOUT_SUCCESS
    request.session.modified = True
  elif request.session[const.ISSUERS][google_session].status == \
        sp.STATUS_LOGIN:
    logging.debug('Assumed this is a logout request from Google Apps.')
    request.session[const.ISSUERS][google_session].status = \
         sp.STATUS_LOGOUT_START
    clear_user_session(request)
    request.session[const.ORIGINAL_ISSUER] = google_session
  
def handle_sp(request, RelayState):
  any_failed = False
  for key, issuer in request.session[const.ISSUERS].iteritems():
    if issuer.status == sp.STATUS_LOGIN:
      request.session[const.ISSUERS][issuer.name].status = \
          sp.STATUS_LOGOUT_START
      if key.startswith("google.com"):
        useSSL = request.session.get(const.USE_SSL, False)
        if useSSL:
          scheme = 'https'
        else:
          scheme = 'http'
        url = scheme + '://mail.google.com/a/' + get_domain(request) + \
          '/?logout'
        t = gh_get_template(request, 'idp/logout.html')
        c = RequestContext(request, {"url": url})
        return HttpResponse(t.render(c))
      else:
        return send_logout_request(request, RelayState, issuer.name,
                                   issuer.assertion_id, issuer.name_id)
    elif issuer.status == sp.STATUS_LOGOUT_START or\
          issuer.status == sp.STATUS_LOGOUT_FAIL:
      any_failed = True
  # send logout response to issuer_origin
  request.session[const.ISSUERS] = {}
  if any_failed:
    status_to_send = samlp.STATUS_PARTIAL_LOGOUT
  else:
    status_to_send = samlp.STATUS_SUCCESS
  if request.session[const.ORIGINAL_ISSUER].startswith("google.com"):
    useSSL = request.session.get(const.USE_SSL, False)
    if useSSL:
      scheme = 'https'
    else:
      scheme = 'http'
    url = scheme + '://mail.google.com/a/' + get_domain(request) + '/'
    t = gh_get_template(request, 'idp/logout-success.html')
    c = RequestContext(request, {"url": url})
    return HttpResponse(t.render(c))
  else:
    return send_logout_response(
      request, RelayState, request.session[const.ORIGINAL_ISSUER],
      request.session[const.LOGOUT_REQUEST_ID], status_to_send)

def send_logout_request(request, RelayState, issuer_name, session_index,
                        name_id):
  response_creator = responsecreator.create("default", config)
  logout_request = response_creator.createLogoutRequest(session_index, name_id)
  signed_request = saml2.utils.sign(logout_request.ToString(),
                                    config.get('privkey_filename'))
  logout_url = config.get("logout_request_urls").get(issuer_name)
  t = gh_get_template(request, 'idp/logout-post.html')
  c = RequestContext(request, {'param_name': 'SAMLRequest',
                               'SAMLMessage': base64.b64encode(signed_request),
                               'RelayState': RelayState,
                               'logout_url': logout_url})
  return HttpResponse(t.render(c))

def send_logout_response(request, RelayState, issuer_name, req_id,
                         status_code):
  response_creator = responsecreator.create("default", config)
  logout_response = response_creator.createLogoutResponse(req_id, status_code)
  signed_response = saml2.utils.sign(logout_response.ToString(),
                                     config.get('privkey_filename'))
  logout_url = config.get("logout_response_urls").get(issuer_name)
  t = gh_get_template(request, 'idp/logout-post.html')
  c = RequestContext(request,
                     {'param_name': 'SAMLResponse',
                      'SAMLMessage': base64.b64encode(signed_response),
                      'RelayState': RelayState,
                      "logout_url": logout_url})
  return HttpResponse(t.render(c))


def build_logout_message(request, SAMLMessage, meth):
  decoded_message = base64.b64decode(SAMLMessage)
  logout_request = meth(decoded_message)
  return (logout_request, decoded_message)

def handle_logout_response(request, logout_response, decoded_response):

  issuer_name = logout_response.issuer.text.strip()
  key_file = config.get('public_keys').get(issuer_name, None)
  if key_file is None:
    raise GHException('Failed to get public key filename.'
                      ' issuer: %s' % issuer_name)
  if samlutils.verify(decoded_response, key_file) == False:
    raise GHException('Failed verifyng the signature'
                      ' of logout response.')
  issuers = request.session.get(const.ISSUERS, {})
  issuer_in_session = issuers.get(issuer_name, None)
  if issuer_in_session is None:
    raise GHException('Request from invalid issuer. Issuer: %s.' % issuer_name)
  if issuer_in_session.status != sp.STATUS_LOGOUT_START:
    raise GHException('Request from invalid issuer.')
  if logout_response.status.status_code.value == samlp.STATUS_SUCCESS:
    request.session[const.ISSUERS][issuer_name].status = \
                                                       sp.STATUS_LOGOUT_SUCCESS
  else:
    request.session[const.ISSUERS][issuer_name].status = \
                                                       sp.STATUS_LOGOUT_FAIL
  request.session.modified = True
  
def handle_logout_request(request, logout_request, decoded_request):

  issuer_name = logout_request.issuer.text.strip()
  key_file = config.get('public_keys').get(issuer_name, None)
  if key_file is None:
    raise GHException('Failed to get public key filename.'
                      ' issuer: %s' % issuer_name)
  if samlutils.verify(decoded_request, key_file) == False:
    raise GHException('Failed verifyng the signature'
                      ' of logout request.')

  issuers = request.session.get(const.ISSUERS, {})
  issuer_in_session = issuers.get(issuer_name, None)
  if issuer_in_session is None:
    raise GHException('Request from invalid issuer. Issuer: %s.' % issuer_name)
  if logout_request.name_id.text is None:
    raise GHException('Request with empty NameID.')
  if issuer_in_session.name_id.text.strip() != \
         logout_request.name_id.text.strip():
    raise GHException('Request with invalid NameID.')

  logging.debug('Succeeded verifying the signature of logout request.')
  issuer_in_session.status = sp.STATUS_LOGOUT_SUCCESS
  request.session[const.ISSUERS][issuer_name] = issuer_in_session
  clear_user_session(request)
  request.session[const.ORIGINAL_ISSUER] = issuer_name
  request.session[const.LOGOUT_REQUEST_ID] = logout_request.id            
  
