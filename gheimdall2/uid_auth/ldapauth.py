
import logging
import ldap

from gheimdall2 import utils

class LDAPAccessController(object):
  def __init__(self, config):
    self.config = config
    self.ldap_uri = config.get("mobile_access_control_ldap_uri")
    self.ldap_basedn = config.get("mobile_access_control_ldap_basedn")
    self.ldap_filter = config.get("mobile_access_control_ldap_filter")

  def check_authorization(self, request):
    ldapHandle = None
    serialnumber_or_guid = getattr(request.device, 'serialnumber', None)
    if serialnumber_or_guid is None:
      serialnumber_or_guid = getattr(request.device, 'guid', None)
    logging.debug("serial: %s " % serialnumber_or_guid)
    if serialnumber_or_guid is None:
      return False
    try:
      ldapHandle = ldap.initialize(self.ldap_uri)
      result = ldapHandle.search_s(
        self.ldap_basedn,
        ldap.SCOPE_SUBTREE,
        self.ldap_filter % utils.ldap_escape(serialnumber_or_guid))
      if len(result) > 0:
        logging.debug("serial found, access accepted.")
        ldapHandle.unbind_s()
        return True
      else:
        ldapHandle.unbind_s()
        logging.debug("serial not found, access rejected.")
        return False
    except Exception, e:
      logging.error(e)
      if ldapHandle is not None:
        try:
          ldapHandle.unbind_s()
        except:
          pass
      return False
      
