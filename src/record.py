#!/usr/bin/env python
# File: record.py

#    Copyright (C) 2012 Christian Jacobs.

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

class Record:
   
   def __init__(self, fields_and_data):
      # Class for a single record in the logbook.
      
      self.fields_and_data = fields_and_data
      logging.debug("New Record instance created!")
      
   def get_data(self, field_name):
      try:
         data = self.fields_and_data[field_name]
      except KeyError:
         # If we can't find the field name, return None
         logging.warning("Field name %s not found in the record!" % field_name)
         data = ""
      return data
      
   def set_data(self, field_name, data):   
      # NOTE: If the field_name already exists in the dictionary,
      # then any data stored there will be over-written.
      self.fields_and_data[field_name.upper()] = data
      return


