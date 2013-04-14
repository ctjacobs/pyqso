#!/usr/bin/env python 
# File: log.py

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
from os.path import basename
import logging
import sqlite3 as sqlite

from adif import AVAILABLE_FIELD_NAMES_TYPES
from record import *
from record_dialog import *

class Log(Gtk.ListStore):
   ''' A Log object can store multiple Record objects. '''
   
   def __init__(self, connection, path=None):
            
      # Call the constructor of the super class (Gtk.ListStore)
      Gtk.ListStore.__init__(self, *data_types)

      # FIXME: Allow the user to select the field names. By default, let's select them all.
      self.SELECTED_FIELD_NAMES_TYPES = AVAILABLE_FIELD_NAMES_TYPES
      self.SELECTED_FIELD_NAMES_ORDERED = ["CALL", "DATE", "TIME", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]
      self.SELECTED_FIELD_NAMES_FRIENDLY = {"CALL":"Callsign",
                                            "DATE":"Date",
                                            "TIME":"Time",
                                            "FREQ":"Frequency",
                                            "BAND":"Band",
                                            "MODE":"Mode",
                                            "RST_SENT":"TX RST",
                                            "RST_RCVD":"RX RST"}

      # The ListStore constructor needs to know the data types of the columns.
      # The index is always an integer. We will assume the fields are strings.
      data_types = [int] + [str]*len(self.SELECTED_FIELD_NAMES_ORDERED)
      
      self.connection = connection

      if(path is None):
         self.name = "Untitled*"
         self.path = None
         self.modified = True
         # Set up a new log table in the database
         c = self.connection.cursor()
         c.execute('''CREATE TABLE log
                   (id INTEGER PRIMARY KEY, ? text, ? text, ? text)''')
      else:
         self.name = basename(path)
         self.path = path
         self.modified = False

      # Populate the ListStore with any existing records
      self.populate()
      
      logging.debug("New Log instance created!")
               
   def populate(self):
      # Remove everything that is rendered already and start afresh
      self.clear()
      
      for i in range(0, len(self.records)):
         log_entry = [] # Create a new record
         # First append the unique index given to the record.
         log_entry.append(i)
         for field in self.SELECTED_FIELD_NAMES_ORDERED:
            log_entry.append(self.records[i].get_data(field))
         self.append(log_entry)
      
      return

   def add_record(self, fields_and_data):
      record = Record(fields_and_data)
      self.records.append(record)
      self.set_modified(True)
      return

   def delete_record(self, index, iter):
      # Get the selected row in the logbook
      self.records.pop(index)
      self.remove(iter)
      self.set_modified(True)
      return

   def edit_record(self, index, field_name, data):
      self.records[index].set_data(field_name, data)
      self.set_modified(True)
      return

   def get_record(self, index):
      return self.records[index]

   def get_number_of_records(self):
      return len(self.records)

   def set_modified(self, modified):
      if(modified and self.modified):
         return # Already modified. Nothing to do here.
      elif(modified and (not self.modified)):
         self.modified = True
         self.name = self.name + "*"
         return
      else:
         self.modified = modified
         return

