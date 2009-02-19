#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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

import saml2
import saml2.utils
import xmldsig as ds
from saml2 import saml, samlp
import time

EMPTY_SAML_RESPONSE="""<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response Version="2.0"
  xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
  xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>
  <Assertion Version="2.0" xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    <Issuer></Issuer>
    <Subject>
      <SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
        <SubjectConfirmationData />
      </SubjectConfirmation>
    </Subject>
    <Conditions></Conditions>
    <AuthnStatement>
      <AuthnContext>
	    <AuthnContextClassRef>
	      urn:oasis:names:tc:SAML:2.0:ac:classes:Password
	    </AuthnContextClassRef>
      </AuthnContext>
    </AuthnStatement>
  </Assertion>
</samlp:Response>
"""

class ResponseCreator(object):
  user_name = None
  response = None
  request = None
  authn_request = None

  def createLogoutRequest(self, session_index, name_id):
    now = saml2.utils.getDateAndTime(time.time())
    req = samlp.LogoutRequest(id=saml2.utils.createID(),
                              version=saml2.V2,
                              issue_instant=now)
    req.issuer=saml.Issuer(text=self.config.get('issuer_name'))
    req.name_id = name_id
    req.session_index = samlp.SessionIndex(text=session_index)
    req.signature = self._get_signature()
    return req

  def createLogoutResponse(self, logout_request_id, status_code):
    now = saml2.utils.getDateAndTime(time.time())    
    self.response = samlp.LogoutResponse(id=saml2.utils.createID(),
                                         version=saml2.V2,
                                         issue_instant=now,
                                         in_response_to=logout_request_id)
    self.response.issuer = saml.Issuer(text=self.config.get('issuer_name'))
    self.response.status = samlp.Status()
    self.response.status.status_code = samlp.StatusCode(status_code)
    self.response.signature = self._get_signature()
    return self.response

  def createAuthnResponse(self, user_name, authn_request, valid_time,
                          auth_time, acsURL, request):
    self.user_name = user_name
    self.authn_request = authn_request
    response = samlp.ResponseFromString(EMPTY_SAML_RESPONSE)
    response.id = saml2.utils.createID()
    now = saml2.utils.getDateAndTime(
      time.time() - self.config.get('time_allowance', 10))
    until = saml2.utils.getDateAndTime(valid_time)
    auth_timestamp = saml2.utils.getDateAndTime(auth_time)
    response.issue_instant = now
    response.assertion[0].id = saml2.utils.createID()
    response.assertion[0].issue_instant = now
    response.assertion[0].issuer.text = self.config.get('issuer_name')
    response.assertion[0].conditions.not_before = now
    response.assertion[0].conditions.not_on_or_after = until
    response.assertion[0].authn_statement[0].authn_instant = auth_timestamp
    response.assertion[0].authn_statement[0].session_not_on_or_after = until
    response.assertion[0].subject.name_id = self._getNameID()
    response.assertion[0].subject.subject_confirmation[0].subject_confirmation_data.recipient = acsURL
    self.response = response
    self.response.signature = self._get_signature()
    self.__adjustment(request)
    return self.response

  def _get_signature(self):
    key_type = self.config.get("privkey_type")
    if key_type == "rsa":
      alg = ds.SIG_RSA_SHA1
    elif key_type == "dsa":
      alg = ds.SIG_DSA_SHA1
    else:
      alg = ds.SIG_RSA_SHA1
    return ds.GetEmptySignature(signature_method_algorithm=alg)

  def __init__(self, config):
    self._prepare(config)

  def _getNameID(self):
    raise NotImplementedError('Child class must implement me.')

  def _prepare(self, config):
    raise NotImplementedError('Child class must implement me.')

  def __adjustment(self, request):
    self._adjustment()
    return None

  def _adjustment(self):
    return None

cached_creators = {}

def create(mapper, config):
  global cached_creators
  if cached_creators.has_key(mapper):
    return cached_creators[mapper]
  exec('from gheimdall2.responsecreator import %s' % mapper)
  ret = eval('%s.cls(config)' % mapper)
  cached_creators[mapper] = ret
  return ret
