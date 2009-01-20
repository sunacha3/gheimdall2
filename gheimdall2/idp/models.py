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

from django.db import models
from django import forms
from gheimdall2.conf import config
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
import logging

# Create your models here.
class ResetForm(forms.Form):
  user_name = forms.CharField(
    label=_('User Name:'), max_length=32, widget=forms.TextInput(
      attrs={'size': config.get('user_name_field_length', 32)}))

class LoginForm(forms.Form):
  SAMLRequest = forms.CharField(label='SAMLRequest', widget=forms.HiddenInput)
  RelayState = forms.CharField(label='RelayState', widget=forms.HiddenInput)
  user_name = forms.CharField(required=True,
    label=_('User Name:'), max_length=32, widget=forms.TextInput(
      attrs={'size': config.get('user_name_field_length', 32)}))
  password = forms.CharField(required=True,
    label=_('Password:'), max_length=16, widget=forms.PasswordInput(
      attrs={'size': config.get('password_field_length', 24)}))

class LoginFormWithCheckBox(LoginForm):
  remember_me = forms.BooleanField(required=False,
                                   label=_('Remember me on this computer:'))

class PasswdForm(forms.Form):
  backURL = forms.CharField(label='backURL', widget=forms.HiddenInput,
                            required=False)
  SAMLRequest = forms.CharField(label='SAMLRequest', widget=forms.HiddenInput,
                                required=False)
  RelayState = forms.CharField(label='RelayState', widget=forms.HiddenInput,
                               required=False)
  user_name = forms.CharField(label=_('User Name:'), 
                              widget=forms.HiddenInput())
  old_password = forms.CharField(
    label=_('Old password:'), max_length=16, widget=forms.PasswordInput(
      attrs={'size': config.get('password_field_length', 24)}))
  new_password = forms.RegexField(
    error_messages={'invalid': _('Input does not match our password policy')},
    regex=config.get('passwd_regex'),
    label=_('New password:'), max_length=16, widget=forms.PasswordInput(
      attrs={'size': config.get('password_field_length', 24)}))
  password_confirm = forms.CharField(
    label=_('Confirm:'), max_length=16, widget=forms.PasswordInput(
      attrs={'size': config.get('password_field_length', 24)}))
  def clean(self):
    cleaned_data = self.cleaned_data
    new_password = cleaned_data.get('new_password')
    if new_password is None:
      # It must be that regex check didn't pass.
      return cleaned_data
    password_confirm = cleaned_data.get('password_confirm')
    if new_password != password_confirm:
      #raise forms.ValidationError(_('New password does not match'))
      self._errors['password_confirm'] = ErrorList(
        [_('New password does not match')])
    if config.get('password_cannot_contain_username', False):
      import re
      user_name = cleaned_data.get('user_name')
      if re.compile(user_name, re.I).search(new_password):
        logging.warn('New password contains username, rejected.')
        self._errors['new_password'] = ErrorList(
          [_('Input does not match our password policy')])
    return cleaned_data
