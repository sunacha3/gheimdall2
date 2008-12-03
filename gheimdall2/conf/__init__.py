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

import os, logging, re
from django.conf import settings

from gheimdall2.conf.configobj import ConfigObj
_config = ConfigObj(os.path.join(settings.CONFDIR, settings.CONFFILE),
                    unrepr=True)
for file in os.listdir(settings.EXTCONFDIR):
  if file.endswith('.conf'):
    _config.merge(ConfigObj(os.path.join(settings.EXTCONFDIR, file),
                            unrepr=True))

compat_dict = {
  'idp_session_lifetime': 'session_lifetime',
  'apps.domain': 'apps_domain',
  'external.command': 'external_command',
  'external.use_env': 'external_use_env',
  'external.env_user': 'external_env_user',
  'external.env_password': 'external_env_password',
  'external.stdin_format': 'external_stdin_format',
}

ltrim = lambda item, to_trim,: re.sub('^' + to_trim, '', item)

def compat_rewrite(key):
  if compat_dict.has_key(key):
    logging.warn("Configuration directive `%s` is deprecated. Use `%s` instead"
                 % (key, compat_dict[key]))
    return compat_dict[key]
  if key.startswith('apps.'):
    new_val = ltrim(key, 'apps.')
    logging.warn("Configuration directive `%s` is deprecated. Use `%s` instead"
                 % (key, new_val))
    return new_val
  return key

class ConfigWrapper:
  def __init__(self, config):
    self._config = config
  def __getattr__(self, attrib):
    if attrib != '__repr__':
      logging.warn('__getattr__ called. Attrib: %s' % attrib)
    return getattr(self._config['global'], attrib)
  def get(self, key, default=None):
    key = compat_rewrite(key)
    ret = self._config['global'].get(key)
    if ret is None:
      return default
    else:
      return ret

config = ConfigWrapper(_config)

