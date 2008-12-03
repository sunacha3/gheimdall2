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

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from gheimdall2.conf import config
from gheimdall2.idp.models import LoginForm, LoginFormWithCheckBox, PasswdForm
from gheimdall2.idp.models import ResetForm
from gheimdall2 import utils, settings, const, auth, errors, passwd
from gheimdall2.errors import GHException
from django.utils.translation import ugettext as _
from saml2 import samlp
import logging, sys, time
import urllib

def static_login(request):
  if not config.get("use_static_login"):
    raise Http404
  if request.device.is_docomo():
    t = utils.gh_get_template(request, 'idp/error.html')
    c = RequestContext(request, {'message': _('Unsupported cell phone.')})
    return HttpResponse(t.render(c))
  user_name = request.POST.get('user_name')
  password = request.POST.get('password')
  auth_engine = auth.createAuthEngine(config.get('auth_engine'), config)
  try:
    auth_engine.authenticate(user_name, password)
  except auth.AuthException, e:
    logging.error("Failed login attempt from %s. User: %s. Reason: %s" %
                  (request.META['REMOTE_ADDR'], user_name, e.reason))
    time.sleep(config.get('sleep_time', 3))
    t = utils.gh_get_template(request, 'idp/error.html')
    c = RequestContext(request, {'message': '401 - ' + _('Can not login')})
    return HttpResponse(t.render(c), status=401)
  logging.debug('User has authenticated.')
  utils.init_session(request, user_name)
  import urllib
  class MyURLopener(urllib.FancyURLopener):
    version = '%s (%s/%s)' % (request.META['HTTP_USER_AGENT'],
                              const.APP_NAME, const.VERSION)
  urllib._urlopener = MyURLopener()
  url = utils.get_static_login_url(request)
  redirected_url = urllib.urlopen(url).geturl()
  import re
  matched = re.match('^.*SAMLRequest=(.*)&RelayState=(.*)$', redirected_url)
  try:
    SAMLRequest = urllib.unquote(matched.group(1))
    RelayState = urllib.unquote(matched.group(2))
    logging.debug("SAMLRequest: %s" % SAMLRequest)
    logging.debug("RelayState: %s" % RelayState)
    (authn_request, RelayState) = utils.create_authn_request(
      SAMLRequest, RelayState, samlp.AuthnRequestFromString)
  except Exception, e:
    logging.error(e)
    t = utils.gh_get_template(request, 'idp/error.html')
    c = RequestContext(request, {'message': _('Invalid SAMLRequest')})
    return HttpResponse(t.render(c))
  response = utils.create_saml_response(request, authn_request, RelayState,
                                        user_name)
  return response

def login(request):
  try:
    (authn_request, RelayState) = utils.parse_saml_request(
      request, samlp.AuthnRequestFromString)
  except Exception, e:
    logging.error(e)
    t = utils.gh_get_template(request, 'idp/error.html')
    c = RequestContext(request, {'message': _('Invalid SAMLRequest')})
    return HttpResponse(t.render(c))
  if config.get('use_header_auth'):
    header_key = config.get('auth_header_key')
    if request.META.has_key(header_key):
      return utils.create_saml_response(request, authn_request, RelayState,
                                        request.META[header_key])
    else:
      logging.error('use_header_auth is set to true,'
                    ' but can not retrieve user_name from header.')
      t = utils.gh_get_template(request, 'idp/error.html')
      c = RequestContext(request, {'message': _('Can not retrieve user_name')})
      return HttpResponse(t.render(c))
  if utils.is_user_authenticated(request):
    return utils.create_saml_response(request, authn_request, RelayState,
                                      request.session.get(const.USER_NAME),
                                      set_time=False)
  if authn_request.is_passive == 'true':
    #TODO: Passive!
    logging.warn('TODO: Correspond with passive authn_request.')
  if config.get('always_remember_me'):
    login_form_cls = LoginForm
  else:
    login_form_cls = LoginFormWithCheckBox
  initial = {}
  initial={'SAMLRequest': request.REQUEST.get("SAMLRequest"),
           'RelayState': request.REQUEST.get("RelayState")}
  login_form = login_form_cls(initial=initial)
  t = utils.gh_get_template(request, 'idp/login.html')
  c = RequestContext(request, {'form': login_form,
                               'flash': utils.get_flash(request)})
  return HttpResponse(t.render(c))

def login_do(request):
  try:
    (authn_request, RelayState) = utils.parse_saml_request(
      request, samlp.AuthnRequestFromString)
  except Exception, e:
    logging.error(e)
    t = utils.gh_get_template(request, 'idp/error.html')
    c = RequestContext(request, {'message': _('Invalid SAMLRequest')})
    return HttpResponse(t.render(c))
  user_name = request.POST.get('user_name')
  password = request.POST.get('password')
  auth_engine = auth.createAuthEngine(config.get('auth_engine'), config)
  try:
    auth_engine.authenticate(user_name, password)
  except auth.AuthException, e:
    if e.code == auth.NEW_AUTHTOK_REQD:
      logging.warn('TODO: lead user to password change page.')
      request.session.flush()
    logging.error("Failed login attempt from %s. User: %s. Reason: %s" %
                  (request.META['REMOTE_ADDR'], user_name, e.reason))
    time.sleep(config.get('sleep_time', 3))
    request.session[const.FLASH] = _('Can not login')
    redirect_url = reverse(login)
    SAMLRequest = request.POST.get("SAMLRequest", None)
    redirect_url += '?' + urllib.urlencode({'SAMLRequest': SAMLRequest,
                                            'RelayState': RelayState})
    return HttpResponseRedirect(redirect_url)
  # User has authenticated
  utils.init_session(request, user_name)
  response = utils.create_saml_response(request, authn_request, RelayState,
                                        user_name)
  return response

def logout(request):
  if request.session.get(const.ISSUERS) is None:
    request.session[const.ISSUERS] = {}
  (SAMLRequest, SAMLResponse, RelayState) = utils.extract_logout_data(request)
  if SAMLRequest:
    try:
      (logout_request, decoded) = utils.build_logout_message(
        request, SAMLRequest, samlp.LogoutRequestFromString)
    except Exception, e:
      logging.error(e)
      t = utils.gh_get_template(request, 'idp/error.html')
      c = RequestContext(request, {'message': _('Invalid SAMLRequest')})
      return HttpResponse(t.render(c))
    issuer_name = logout_request.issuer.text.strip()
    try:
      utils.handle_logout_request(request, logout_request, decoded)
    except GHException, e:
      logging.error(e)
      return utils.createLogoutResponse(request, RelayState, issuer_name,
                                        logout_request.id,
                                        samlp.STATUS_RESPONDER)
  elif SAMLResponse:
    try:
      (logout_response, decoded) = utils.build_logout_message(
        request, SAMLResponse, samlp.LogoutResponseFromString)
    except Exception, e:
      logging.error(e)
      t = utils.gh_get_template(request, 'idp/error.html')
      c = RequestContext(request, {'message': _('Invalid SAMLResponse')})
      return HttpResponse(t.render(c))
    try:
      utils.handle_logout_response(request, logout_response, decoded)
    except GHException, e:
      logging.error(e)
  else:
    utils.handle_logout_from_google(request)
  return utils.handle_sp(request, RelayState)

def password(request):
  if not config.get("use_change_passwd"):
    raise Http404
  # first retrieve user_name from request
  user_name = request.REQUEST.get('user_name')
  if user_name is None:
    user_name = request.session.get(const.USER_NAME)
  if user_name is None:
    raise errors.GHException('Can not retrieve user name.')
  backURL = request.REQUEST.get('backURL')
  # TODO: sanitize user_name and backURL
  
  passwd_form = PasswdForm(initial={"user_name": user_name, 
                                    "backURL": backURL})
  if user_name.find('@') >= 0:
    mail_address = user_name
  else:
    mail_address = user_name + '@' + config.get('apps_domain')
  t = utils.gh_get_template(request, 'idp/passwd.html')
  c = RequestContext(request, {'mail_address': mail_address,
                               'backURL': backURL,
                               'form': passwd_form})
  return HttpResponse(t.render(c))

def passwd_do(request):
  if not config.get("use_change_passwd"):
    raise Http404
  passwd_form = PasswdForm(data=request.POST)
  user_name = request.POST.get('user_name')
  if user_name.find('@') >= 0:
    mail_address = user_name
  else:
    mail_address = user_name + '@' + config.get('apps_domain')
  if not passwd_form.is_valid():
    t = utils.gh_get_template(request, 'idp/passwd.html')
    c = RequestContext(request, {
        'mail_address': mail_address,
        'backURL': request.POST.get('backURL'),
        'form': passwd_form})
    return HttpResponse(t.render(c))
    
  passwd_engine = passwd.createPasswdEngine(
    engine=config.get('passwd_engine'), config=config)
  try:
    passwd_engine.changePassword(passwd_form.cleaned_data.get('user_name'),
                                 passwd_form.cleaned_data.get('old_password'),
                                 passwd_form.cleaned_data.get('new_password'))
  except passwd.PasswdException, e:
    # changing password failed
    logging.error(e)
    time.sleep(config.get('sleep_time', 3))
    t = utils.gh_get_template(request, 'idp/passwd.html')
    c = RequestContext(request, {
        'mail_address': mail_address,
        'flash': _('Failed to change password'),
        'backURL': passwd_form.cleaned_data.get('backURL'),
        'form': passwd_form})
    return HttpResponse(t.render(c))

  if passwd_form.cleaned_data.get('SAMLRequest'):
    # User's password was expired. Now, we can let them in...
    try:
      (authn_request, RelayState) = utils.parse_saml_request(
        request, samlp.AuthnRequestFromString)
    except Exception, e:
      logging.error(e)
      t = utils.gh_get_template(request, 'idp/error.html')
      c = RequestContext(request, {'message': _('Invalid SAMLRequest')})
      return HttpResponse(t.render(c))
    return utils.create_saml_response(request, authn_request, RelayState,
                                      user_name)
  t = utils.gh_get_template(request, 'idp/passwd-success.html')
  c = RequestContext(request, {
      'mail_address': mail_address,
      'backURL': passwd_form.cleaned_data.get('backURL')})
  return HttpResponse(t.render(c))

def reset_password(request):
  if not config.get("use_reset_passwd"):
    raise Http404
  t = utils.gh_get_template(request, 'idp/reset-password.html')
  c = RequestContext(request, {'form': ResetForm()})
  return HttpResponse(t.render(c))

def reset_password_do(request):
  reset_form = ResetForm(request.POST)
  if not reset_form.is_valid():
    t = utils.gh_get_template(request, 'idp/error.html')
    c = RequestContext(request, {'message': _('Invalid username.')})
    return HttpResponse(t.render(c))
  try:
    user_name = reset_form.cleaned_data.get('user_name')
    passwd_engine = passwd.createPasswdEngine(
      engine=config.get('passwd_engine'), config=config)
    new_pass = passwd_engine.resetPassword(user_name)
  except Exception, e:
    logging.error(e)
    t = utils.gh_get_template(request, 'idp/error.html')
    c = RequestContext(request, {'message': e})
    return HttpResponse(t.render(c))
  t = utils.gh_get_template(request, 'idp/reset-password-success.html')
  c = RequestContext(request, {'user_name': user_name,
                               'new_pass': new_pass})
  return HttpResponse(t.render(c))
  
