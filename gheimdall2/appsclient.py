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

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom
import gdata.apps
import gdata.apps.service
import pickle
import os
import time
import logging

FILE = "apps_client_token_cpickle.data"
EXPIRE = 86340 #23h50m
DEADLOCK_TIMEOUT = 60

def getAppsClient(email, domain, password, source, dir):
  """ This is a wrapper function to share authentication token from
  google among all the processes.
  """

  pickle_file = os.path.join(dir, FILE)
  lock_file = pickle_file + ".lock"
  token = None

  try:
    # First, aquire lock
    lockFile(lock_file)
    token_dict = {}
    # Second, try to read from pickle file
    try:
      f = open(pickle_file, "rb")
      token_dict = pickle.load(f)
      if token_dict.has_key(domain):
        (token, expire) = token_dict[domain]
        if expire < time.time():
          token = None
      else:
        token = None
      f.close()
    except Exception, e:
      # ignore all exceptions
      logging.error(e)
      pass
    client = gdata.apps.service.AppsService(
      email=email, domain=domain, password=password,
      source=source)
    if token:
      try:
        client.SetClientLoginToken(token)
      except AttirbuteError:
        client.auth_token = token
      logging.debug('An auth token re-used.')
    else:
      client.ProgrammaticLogin()
      try:
        token = client.GetClientLoginToken()
      except AttributeError:
        token = client.auth_token
      try:
        logging.debug('Writing token to file.')
        f = open(pickle_file, "wb")
        os.chmod(pickle_file, 0600)
        expire = time.time() + EXPIRE
        token_dict[domain] = (token, expire)
        pickle.dump(token_dict, f, True)
        f.close()
      except (IOError, EOFError):
        # TODO: log error?
        raise
  finally:
    unlockFile(lock_file)

  return client

def lockFile(path):
  start_time = time.time()
  while True:
    try:
      lockfd = os.open(path, os.O_CREAT|os.O_WRONLY|os.O_EXCL)
    except OSError:
      if time.time() - start_time > DEADLOCK_TIMEOUT:
        raise RuntimeError("Could not aquire lock.")
      time.sleep(0.5)
    else:
      os.close(lockfd)
      break

def unlockFile(path):
  os.unlink(path)
