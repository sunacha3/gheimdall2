#!/usr/bin/env python
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

from django.core.management import setup_environ
from gheimdall2 import settings

setup_environ(settings)
from gheimdall2.conf.configobj import ConfigObj
from gheimdall2.conf import compat_dict, ltrim
from django.conf import settings
import os, sys

DEBUG = True

def usage():
  sys.stderr.write('Usage: %s old-config new-config\n' % sys.argv[0])

def debug(message):
  if DEBUG:
    sys.stderr.write('%s\n' % message)

def get_new_key(old_key):
  if compat_dict.has_key(old_key):
    return compat_dict[old_key]
  if old_key.startswith('apps.'):
    return ltrim(old_key, 'apps.')
  return old_key

def my_walk(section, key, new_config=None):
  if section.depth == 1:
    new_key = get_new_key(key)
    if new_config['global'].has_key(new_key):
      new_config['global'][new_key] = section[key]
    else:
      print 'ignored %s: %s' % (key, section[key])
      
def main():
  conf_file = os.path.join(settings.CONFDIR, settings.CONFFILE)
  if len(sys.argv) < 3:
    usage()
    sys.exit(1)
  oldconf_file = sys.argv[1]
  newconf_file = sys.argv[2]
  old_config = ConfigObj(oldconf_file, unrepr=True, interpolation=False)
  new_config = ConfigObj(conf_file, unrepr=True)
  old_config['global'].walk(my_walk, call_on_sections=True, new_config=new_config)
  f = file(newconf_file, 'w')
  new_config.write(f)
  f.close()
  print "suggested configuration wrote to file: %s." % newconf_file
 
if __name__ == '__main__':
  main()
