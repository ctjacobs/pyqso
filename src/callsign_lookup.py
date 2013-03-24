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

# Uses qrz.com to lookup details about a particular callsign.

def init_session(username, password):
   ''' Initiates a session with the qrz.com server. Hopefully this will return a session ID. '''
   connection = httplib.HTTPSConnection('xmldata.qrz.com', port=443)
   request = '/xml/current/?username=%s;password=%s;agent=pyqso' % (username, password)
   connection.request('GET', request)
   response = connection.getresponse()
   data = response.read()

   if(successful):
      return session_id
   else:
      return None

