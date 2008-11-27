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

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from gheimdall2.conf import config
from gheimdall2.idp.models import LoginForm, LoginFormWithCheckBox, PasswdForm
from gheimdall2 import utils, settings, const, auth, errors, passwd
from django.utils.translation import ugettext as _
from saml2 import samlp
import logging, sys, time
import urllib

def login(request):
  authn_request = request.session.get(const.AUTHN_REQUEST, None)
  RelayState = request.session.get(const.RELAY_STATE, None)
  if authn_request is None:
    try:
      (authn_request, RelayState) = utils.parse_saml_request(
        request, samlp.AuthnRequestFromString)
    except Exception, e:
      logging.error(e)
      # TODO: gently handle this situation.
      raise
  if config.get('use_header_auth'):
    #TODO: implement header auth
    return HttpResponse('TODO: Dig in the header.')
  if utils.is_user_authenticated(request):
    return utils.create_saml_response(request, authn_request, RelayState,
                                      request.session.get(const.USER_NAME),
                                      set_time=False)
  if authn_request.is_passive == 'true':
    #TODO: Passive!
    logging.warn('TODO: Correspond with passive authn_request.')
  request.session[const.AUTHN_REQUEST] = authn_request
  request.session[const.RELAY_STATE] = RelayState
  if config.get('always_remember_me'):
    login_form_cls = LoginForm
  else:
    login_form_cls = LoginFormWithCheckBox
  initial = {}
  if request.device.is_docomo():
    initial={'SAMLRequest': request.REQUEST.get("SAMLRequest"),
             'RelayState': request.REQUEST.get("RelayState")}
  login_form = login_form_cls(initial=initial)
  t = utils.gh_get_template(request, 'idp/login.html')
  c = RequestContext(request, {'form': login_form,
                               'flash': utils.get_flash(request)})
  return HttpResponse(t.render(c))

def login_do(request):
  authn_request = request.session.get(const.AUTHN_REQUEST, None)
  RelayState = request.session.get(const.RELAY_STATE, None)
  if authn_request is None:
    try:
      (authn_request, RelayState) = utils.parse_saml_request(
        request, samlp.AuthnRequestFromString)
    except Exception, e:
      logging.debug(sys.exc_info())
      # TODO: gently handle this situation.
      raise
  user_name = request.POST.get('user_name')
  password = request.POST.get('password')
  auth_engine = auth.createAuthEngine(config.get('auth_engine'), config)
  try:
    auth_engine.authenticate(user_name, password)
  except auth.AuthException, e:
    if e.code == auth.NEW_AUTHTOK_REQD:
      #TODO: lead user to password change page.
      pass
    logging.error("Failed login attempt from %s. User: %s" %
                  (request.META['REMOTE_ADDR'], user_name))
    time.sleep(config.get('sleep_time', 3))
    request.session[const.FLASH] = _('Can not login')
    redirect_url = reverse(login)
    if request.device.is_docomo():
      SAMLRequest = request.POST.get("SAMLRequest", None)
      redirect_url += '?' + urllib.urlencode({'SAMLRequest': SAMLRequest,
                                              'RelayState': RelayState})
    return HttpResponseRedirect(redirect_url)
  # User has authenticated
  response = utils.create_saml_response(request, authn_request, RelayState,
                                        user_name)
  return response

def logout(request):
  if request.session.get(const.ISSUERS) is None:
    request.session[const.ISSUERS] = {}
  (SAMLRequest, SAMLResponse, RelayState) = utils.extract_logout_data(request)
  if SAMLRequest:
    # TODO
    raise NotImplementedError("Can not handle SAMLRequest for logout yet.")
  elif SAMLResponse:
    # TODO
    raise NotImplementedError("Can not handle SAMLResponse for logout yet.")
  else:
    utils.handle_logout_from_google(request)
  return utils.handle_sp(request, RelayState)

def password(request):
  # first retrieve user_name from request
  user_name = request.REQUEST.get('user_name')
  if user_name is None:
    user_name = request.session.get(const.USER_NAME)
  if user_name is None:
    raise errors.GHException('Can not retrieve user name.')
  backURL = request.REQUEST.get('backURL')
  # TODO: sanitize user_name and backURL
  if not config.get('use_change_passwd'):
    # TODO: gently handle this situation
    # changing password is not available.
    raise errors.GHException('Changing password is not available here')
  
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
  if not config.get('use_change_passwd'):
    # TODO: gently handle this situation
    # changing password is not available.
    raise errors.GHException('Changing password is not available here')
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
    #time.sleep(config.get('sleep_time', 3))
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
      # TODO: gently handle this situation.
      raise
    return utils.create_saml_response(request, authn_request, RelayState,
                                      user_name)
  t = utils.gh_get_template(request, 'idp/passwd-success.html')
  c = RequestContext(request, {
      'mail_address': mail_address,
      'backURL': passwd_form.cleaned_data.get('backURL')})
  return HttpResponse(t.render(c))
