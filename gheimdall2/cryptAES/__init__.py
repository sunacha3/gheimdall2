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

__author__ = 'kaname@sios.com (Kaname YOSHIDA)'

from Crypto.Cipher import AES
from binascii import unhexlify, hexlify
import md5

class CryptAES(object):
  def __init__(self, config):
    key = config.get('aes_key')
    self.AES = AES.new(md5.new(key).digest(), AES.MODE_ECB)
    self.pad = config.get('aes_pad')

  def encryption_str(self, str):
    str += self.pad * (-len(str)%16)  # Padding
    return hexlify(self.AES.encrypt(str))

  def decryption_str(self, enstr):
    str = self.AES.decrypt(unhexlify(enstr))
    return str.rstrip(self.pad)  # UnPadding

cached_AES = None

def createAES(config):
  global cached_AES
  if cached_AES is None:
    cached_AES = CryptAES(config)
  return cached_AES
