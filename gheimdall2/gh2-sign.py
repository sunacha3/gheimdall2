#!/usr/bin/python

import sys
import saml2.utils

def main():
  saml_response = sys.stdin.readline()[:-1]
  key_filename = sys.stdin.readline()[:-1]
  try:
    signed_response = saml2.utils.sign(saml_response, key_filename)
  except Exception, e:
    print e
    sys.exit(1)
  print signed_response

if __name__ == '__main__':
  main()  
