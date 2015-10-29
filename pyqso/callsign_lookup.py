#!/usr/bin/env python3

#    Copyright (C) 2013 Christian T. Jacobs.

#    This file is part of PyQSO.

#    PyQSO is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyQSO is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyQSO.  If not, see <http://www.gnu.org/licenses/>.

import logging
import unittest
import http.client
from xml.dom import minidom

from auxiliary_dialogs import *

class CallsignLookupQRZ():
   """ Use qrz.com to lookup details about a particular callsign. """

   def __init__(self, parent):
      """ Initialise a new callsign lookup handler.
      
      :arg parent: The parent Gtk dialog.
      """
      self.parent = parent
      self.connection = None
      self.session_key = None
      return

   def connect(self, username, password):
      """ Initiate a session with the qrz.com server. Hopefully this will provide a session key.
      
      :arg str username: The username of the qrz.com user account.
      :arg str password: The password of the qrz.com user account.
      :returns: True if a successful connection was made to the server, and False otherwise.
      :rtype: bool
      """
      logging.debug("Connecting to the qrz.com server...")
      try:
         self.connection = http.client.HTTPConnection('xmldata.qrz.com')
         request = '/xml/current/?username=%s;password=%s;agent=pyqso' % (username, password)
         self.connection.request('GET', request)
         response = self.connection.getresponse()
      except:
         error(parent=self.parent, message="Could not connect to the qrz.com server. Check connection to the internets?")
         return False
     
      xml_data = minidom.parseString(response.read())
      session_node = xml_data.getElementsByTagName('Session')[0] # There should only be one Session element
      session_key_node = session_node.getElementsByTagName('Key')
      if(len(session_key_node) > 0):
         self.session_key = session_key_node[0].firstChild.nodeValue
         logging.debug("Successfully connected to the qrz.com server...")
         connected = True
      else:
         connected = False

      # If there are any errors or warnings, print them out
      session_error_node = session_node.getElementsByTagName('Error')
      if(len(session_error_node) > 0):
         session_error = session_error_node[0].firstChild.nodeValue
         error(parent=self.parent, message="qrz.com session error: "+session_error)

      return connected

   def lookup(self, full_callsign, ignore_prefix_suffix = True):
      """ Parse the XML tree that is returned from the qrz.com XML server to obtain the NAME, ADDRESS, STATE, COUNTRY, DXCC, CQZ, ITUZ, and IOTA field data (if present).
      
      :arg str full_callsign: The callsign to look up (without any prefix/suffix stripping).
      :arg bool ignore_prefix_suffix: True if callsign prefixes/suffixes should be removed prior to querying the server, False otherwise.
      :returns: The data in a dictionary called fields_and_data. 
      :rtype: dict
      """
      
      logging.debug("Looking up callsign. The full callsign (with a prefix and/or suffix) is %s" % full_callsign)
      
      # Remove any prefix or suffix from the callsign before performing the lookup.
      if(ignore_prefix_suffix):
         callsign = strip(full_callsign)
      else:
         callsign = full_callsign
                          
      # Commence lookup.
      fields_and_data = {"NAME":"", "ADDRESS":"", "STATE":"", "COUNTRY":"", "DXCC":"", "CQZ":"", "ITUZ":"", "IOTA":""}
      if(self.session_key):
         request = '/xml/current/?s=%s;callsign=%s' % (self.session_key, callsign)
         self.connection.request('GET', request)
         response = self.connection.getresponse()

         xml_data = minidom.parseString(response.read())
         callsign_node = xml_data.getElementsByTagName('Callsign')
         if(len(callsign_node) > 0): 
            callsign_node = callsign_node[0] # There should only be a maximum of one Callsign element

            callsign_fname_node = callsign_node.getElementsByTagName('fname')
            callsign_name_node = callsign_node.getElementsByTagName('name')
            if(len(callsign_fname_node) > 0):
               fields_and_data["NAME"] = callsign_fname_node[0].firstChild.nodeValue
            if(len(callsign_name_node) > 0): # Add the surname, if present
               fields_and_data["NAME"] = fields_and_data["NAME"] + " " + callsign_name_node[0].firstChild.nodeValue

            callsign_addr1_node = callsign_node.getElementsByTagName('addr1')
            callsign_addr2_node = callsign_node.getElementsByTagName('addr2')
            if(len(callsign_addr1_node) > 0):
               fields_and_data["ADDRESS"] = callsign_addr1_node[0].firstChild.nodeValue
            if(len(callsign_addr2_node) > 0): # Add the second line of the address, if present
               fields_and_data["ADDRESS"] = (fields_and_data["ADDRESS"] + ", " if len(callsign_addr1_node) > 0 else "") + callsign_addr2_node[0].firstChild.nodeValue

            callsign_state_node = callsign_node.getElementsByTagName('state')
            if(len(callsign_state_node) > 0):
               fields_and_data["STATE"] = callsign_state_node[0].firstChild.nodeValue

            callsign_country_node = callsign_node.getElementsByTagName('country')
            if(len(callsign_country_node) > 0):
               fields_and_data["COUNTRY"] = callsign_country_node[0].firstChild.nodeValue

            callsign_ccode_node = callsign_node.getElementsByTagName('ccode')
            if(len(callsign_ccode_node) > 0):
               fields_and_data["DXCC"] = callsign_ccode_node[0].firstChild.nodeValue

            callsign_cqzone_node = callsign_node.getElementsByTagName('cqzone')
            if(len(callsign_cqzone_node) > 0):
               fields_and_data["CQZ"] = callsign_cqzone_node[0].firstChild.nodeValue

            callsign_ituzone_node = callsign_node.getElementsByTagName('ituzone')
            if(len(callsign_ituzone_node) > 0):
               fields_and_data["ITUZ"] = callsign_ituzone_node[0].firstChild.nodeValue

            callsign_iota_node = callsign_node.getElementsByTagName('iota')
            if(len(callsign_iota_node) > 0):
               fields_and_data["IOTA"] = callsign_iota_node[0].firstChild.nodeValue
         else:
            # If there is no Callsign element, then print out the error message in the Session element
            session_node = xml_data.getElementsByTagName('Session')
            if(len(session_node) > 0): 
               session_error_node = session_node[0].getElementsByTagName('Error')
               if(len(session_error_node) > 0):
                  session_error = session_error_node[0].firstChild.nodeValue
                  error(parent=self.parent, message=session_error)
            # Return empty strings for the field data
         logging.debug("Callsign lookup complete. Returning data...")
      return fields_and_data


class CallsignLookupHamQTH():
   """ Use hamqth.com to lookup details about a particular callsign. """

   def __init__(self, parent):
      self.parent = parent
      self.connection = None
      self.session_id = None
      return

   def connect(self, username, password):
      """ Initiate a session with the hamqth.com server. Hopefully this will provide a session key.
      
      :arg str username: The username of the hamqth.com user account.
      :arg str password: The password of the hamqth.com user account.
      :returns: True if a successful connection was made to the server, and False otherwise.
      :rtype: bool
      """

      logging.debug("Connecting to the hamqth.com server...")
      try:
         self.connection = http.client.HTTPConnection('www.hamqth.com')
         request = '/xml.php?u=%s&p=%s' % (username, password)
         self.connection.request('GET', request)
         response = self.connection.getresponse()
      except:
         error(parent=self.parent, message="Could not connect to the hamqth.com server. Check connection to the internets?")
         return False
      
      xml_data = minidom.parseString(response.read())
      session_node = xml_data.getElementsByTagName('session')[0] # There should only be one Session element
      session_id_node = session_node.getElementsByTagName('session_id')
      if(len(session_id_node) > 0):
         self.session_id = session_id_node[0].firstChild.nodeValue
         logging.debug("Successfully connected to the hamqth.com server...")
         connected = True
      else:
         connected = False

      # If there are any errors or warnings, print them out
      session_error_node = session_node.getElementsByTagName('error')
      if(len(session_error_node) > 0):
         session_error = session_error_node[0].firstChild.nodeValue
         error(parent=self.parent, message="hamqth.com session error: "+session_error)

      return connected

   def lookup(self, full_callsign, ignore_prefix_suffix = True):
      """ Parse the XML tree that is returned from the hamqth.com XML server to obtain the NAME, ADDRESS, STATE, COUNTRY, DXCC, CQZ, ITUZ, and IOTA field data (if present),

      :arg str full_callsign: The callsign to look up (without any prefix/suffix stripping).
      :arg bool ignore_prefix_suffix: True if callsign prefixes/suffixes should be removed prior to querying the server, False otherwise.
      :returns: The data in a dictionary called fields_and_data. 
      :rtype: dict
      """
      
      logging.debug("Looking up callsign. The full callsign (with a prefix and/or suffix) is %s" % full_callsign)
      
      # Remove any prefix or suffix from the callsign before performing the lookup.
      if(ignore_prefix_suffix):
         callsign = strip(full_callsign)
      else:
         callsign = full_callsign
                          
      # Commence lookup.
      fields_and_data = {"NAME":"", "ADDRESS":"", "STATE":"", "COUNTRY":"", "DXCC":"", "CQZ":"", "ITUZ":"", "IOTA":""}
      if(self.session_id):
         request = '/xml.php?id=%s&callsign=%s&prg=pyqso' % (self.session_id, callsign)
         self.connection.request('GET', request)
         response = self.connection.getresponse()

         xml_data = minidom.parseString(response.read())
         search_node = xml_data.getElementsByTagName('search')
         if(len(search_node) > 0):
            search_node = search_node[0] # There should only be a maximum of one Callsign element

            search_name_node = search_node.getElementsByTagName('nick')
            if(len(search_name_node) > 0):
               fields_and_data["NAME"] = fields_and_data["NAME"] + " " + search_name_node[0].firstChild.nodeValue

            search_addr1_node = search_node.getElementsByTagName('addr_street1')
            search_addr2_node = search_node.getElementsByTagName('addr_street2')
            if(len(search_addr1_node) > 0):
               fields_and_data["ADDRESS"] = search_addr1_node[0].firstChild.nodeValue
            if(len(search_addr2_node) > 0): # Add the second line of the address, if present
               fields_and_data["ADDRESS"] = (fields_and_data["ADDRESS"] + ", " if len(search_addr1_node) > 0 else "") + search_addr2_node[0].firstChild.nodeValue

            search_state_node = search_node.getElementsByTagName('us_state')
            if(len(search_state_node) > 0):
               fields_and_data["STATE"] = search_state_node[0].firstChild.nodeValue

            search_country_node = search_node.getElementsByTagName('country')
            if(len(search_country_node) > 0):
               fields_and_data["COUNTRY"] = search_country_node[0].firstChild.nodeValue

            search_cqzone_node = search_node.getElementsByTagName('CQ')
            if(len(search_cqzone_node) > 0):
               fields_and_data["CQZ"] = search_cqzone_node[0].firstChild.nodeValue

            search_ituzone_node = search_node.getElementsByTagName('itu')
            if(len(search_ituzone_node) > 0):
               fields_and_data["ITUZ"] = search_ituzone_node[0].firstChild.nodeValue

            search_iota_node = search_node.getElementsByTagName('grid')
            if(len(search_iota_node) > 0):
               fields_and_data["IOTA"] = search_iota_node[0].firstChild.nodeValue
         else:
            # If there is no Callsign element, then print out the error message in the Session element
            session_node = xml_data.getElementsByTagName('session')
            if(len(session_node) > 0): 
               session_error_node = session_node[0].getElementsByTagName('error')
               if(len(session_error_node) > 0):
                  session_error = session_error_node[0].firstChild.nodeValue
                  error(parent=self.parent, message=session_error)
            # Return empty strings for the field data
         logging.debug("Callsign lookup complete. Returning data...")
      return fields_and_data


def strip(full_callsign):
   """ Remove any prefixes or suffixes from a callsign.
   
   :arg str full_callsign: The callsign to be considered for prefix/suffix removal.
   :returns: The callsign with prefixes/suffixes removed.
   :rtype: str
   """
   
   components = full_callsign.split("/") # We assume that prefixes or suffixes come before/after a forward slash character "/".
   suffixes = ["P", "M", "A", "PM", "MM", "AM", "QRP"]
   try:
      if(len(components) == 3):
         # We have both a prefix and a suffix.
         callsign = components[1]
         
      elif(len(components) == 2):
         if(components[1].upper() in suffixes or components[1].lower() in suffixes):
            # If the last part of the full_callsign is a valid suffix, then use the part before that.
            callsign = components[0]
            logging.debug("Suffix %s found. Callsign to lookup is %s" % (components[1], callsign))
         else:
            # We have a prefix, so take the part after the first "/".
            callsign = components[1]
            logging.debug("Prefix %s found. Callsign to lookup is %s" % (components[0], callsign))
            
      elif(len(components) == 1):
         # We have neither a prefix nor a suffix, so use the full_callsign.
         callsign = full_callsign
         logging.debug("No prefix or suffix found. Callsign to lookup is %s" % callsign)
         
      else:
         raise ValueError
   except ValueError:
      callsign = full_callsign
   return callsign
      
class TestCallsignLookup(unittest.TestCase):
   """ The unit tests for the CallsignLookup class. """

   def setUp(self):
      """ Set up the CallsignLookup object needed for the unit tests. """
      pass

   def test_strip(self):
      callsign = "EA3/MYCALL/MM"
      assert strip(callsign) == "MYCALL"
      
   def test_strip_prefix_only(self):
      callsign = "EA3/MYCALL"
      assert strip(callsign) == "MYCALL"
      
   def test_strip_suffix_only(self):
      callsign = "MYCALL/M"
      assert strip(callsign) == "MYCALL"

   def test_strip_no_prefix_or_suffix(self):
      callsign = "MYCALL"
      assert strip(callsign) == "MYCALL"

if(__name__ == '__main__'):
   unittest.main()
