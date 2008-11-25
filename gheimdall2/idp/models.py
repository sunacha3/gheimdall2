from django.db import models
from django import forms
from gheimdall2.conf import config
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList

# Create your models here.
class LoginForm(forms.Form):
  SAMLRequest = forms.CharField(label='SAMLRequest', widget=forms.HiddenInput)
  RelayState = forms.CharField(label='RelayState', widget=forms.HiddenInput)
  user_name = forms.CharField(
    label=_('User Name:'), max_length=32, widget=forms.TextInput(
      attrs={'size': config.get('user_name_field_length', 32)}))
  password = forms.CharField(
    label=_('Password:'), max_length=16, widget=forms.PasswordInput(
      attrs={'size': config.get('password_field_length', 24)}))

class LoginFormWithCheckBox(LoginForm):
  remember_me = forms.BooleanField(label=_('Remember me on this computer:'))

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
    regex=config.get('passwd_regex'),
    label=_('New password:'), max_length=16, widget=forms.PasswordInput(
      attrs={'size': config.get('password_field_length', 24)}))
  password_confirm = forms.CharField(
    label=_('Confirm:'), max_length=16, widget=forms.PasswordInput(
      attrs={'size': config.get('password_field_length', 24)}))
  def clean(self):
    cleaned_data = self.cleaned_data
    new_password = cleaned_data.get('new_password')
    password_confirm = cleaned_data.get('password_confirm')
    if new_password != password_confirm:
      #raise forms.ValidationError(_('New password does not match'))
      self._errors['password_confirm'] = ErrorList(
        [_('New password does not match')])
    return cleaned_data
