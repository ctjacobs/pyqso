#!/usr/bin/env python
# File: callsign_lookup.py

#    Copyright (C) 2013 Christian Jacobs.

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

from gi.repository import Gtk, GObject
import logging
import httplib
from xml.dom import minidom

from auxiliary_dialogs import *

class CallsignLookup():
   ''' Uses qrz.com to lookup details about a particular callsign. '''

   def __init__(self, parent):
      logging.debug("New CallsignLookup instance created!")
      self.parent = parent
      self.connection = None
      self.session_key = None
      return

   def connect(self, username, password):
      ''' Initiates a session with the qrz.com server. Hopefully this will return a session key. '''
      self.connection = httplib.HTTPConnection('xmldata.qrz.com')
      request = '/xml/current/?username=%s;password=%s;agent=pyqso' % (username, password)
      self.connection.request('GET', request)
      response = self.connection.getresponse()

      xml_data = minidom.parseString(response.read())
      session_node = xml_data.getElementsByTagName('Session')[0] # There should only be one Session element
      session_key_node = session_node.getElementsByTagName('Key')
      if(len(session_key_node) > 0):
         self.session_key = session_key_node[0].firstChild.nodeValue

      # If there are any errors or warnings, print them out
      session_error_node = session_node.getElementsByTagName('Error')
      if(len(session_error_node) > 0):
         session_error = session_error_node[0].firstChild.nodeValue
         error(parent=self.parent, message=session_error)
      return

   def lookup(self, callsign):
      ''' Parses the XML tree that is returned from the qrz.com XML server to obtain the NAME, ADDRESS, STATE, COUNTRY, DXCC, CQZ, ITUZ, and IOTA field data (if present),
      and returns the data in the dictionary called fields_and_data. '''
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
               fields_and_data["ADDRESS"] = fields_and_data["ADDRESS"] + ", " + callsign_addr2_node[0].firstChild.nodeValue

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
               session_error_node = session_node.getElementsByTagName('Error')
               if(len(session_error_node) > 0):
                  session_error = session_error_node[0].firstChild.nodeValue
                  error(parent=self.parent, message=session_error)
            # Return empty strings for the field data

      return fields_and_data

