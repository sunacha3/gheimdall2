#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   GHeimdall - A small web application for Google Apps SSO service.
#   Copyright (C) 2007 SIOS Technology, Inc.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
#   USA.
#
#   $Id: appsclient.py 28 2007-08-08 05:00:27Z matsuo.takashi $

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

FILE = "apps_client_cpickle.data"
EXPIRE = 86340 #23h50m
DEADLOCK_TIMEOUT = 60

def getAppsClient(email, domain, password, source, dir):
  """ This is a wrapper function to share authentication token from
  google among all the processes.
  """

  pickle_file = os.path.join(dir, FILE)
  lock_file = pickle_file + ".lock"
  client = None

  try:
    # First, aquire lock
    lockFile(lock_file)
    # Second, try to read from pickle file
    try:
      f = open(pickle_file, "rb")
      (client, expire) = pickle.load(f)
      f.close()
      if expire < time.time():
        client = None
    except Exception:
      # ignore all exceptions
      pass
    # If client is invalid, create new one.
    if not isinstance(client, gdata.apps.service.AppsService):
      client = gdata.apps.service.AppsService(
        email=email, domain=domain, password=password,
        source=source)
      client.ProgrammaticLogin()
      try:
        import logging
        f = open(pickle_file, "wb")
        expire = time.time() + EXPIRE
        pickle.dump((client, expire), f, True)
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
