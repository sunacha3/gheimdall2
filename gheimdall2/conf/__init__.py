import os, logging, re
from django.conf import settings

from gheimdall2.conf.configobj import ConfigObj
_config = ConfigObj(os.path.join(settings.CONFDIR, settings.CONFFILE),
                    unrepr=True)
for file in os.listdir(settings.EXTCONFDIR):
  _config.merge(ConfigObj(os.path.join(settings.EXTCONFDIR, file),unrepr=True))

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

