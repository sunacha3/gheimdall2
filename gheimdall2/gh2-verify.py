#!/usr/bin/python

import sys
import saml2.utils

def main():
  key_filename = sys.stdin.readline()[:-1]
  saml_message = "".join(sys.stdin.readlines())
  try:
    result = saml2.utils.verify(saml_message, key_filename)
  except Exception, e:
    print e
    sys.exit(1)
  if result:
    print "True"
    sys.exit()
  print "Failed to verify"
  sys.exit(1)

if __name__ == '__main__':
  main()  
