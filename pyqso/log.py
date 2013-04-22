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
from record_dialog import *

class Log(Gtk.ListStore):
   ''' A Log object can store multiple Record objects. '''
   
   def __init__(self, connection, name):

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
      # Call the constructor of the super class (Gtk.ListStore)
      Gtk.ListStore.__init__(self, *data_types)

      self.connection = connection
      self.name = name
      
      logging.debug("New Log instance created!")
               
   def populate(self):
      # Remove everything that is rendered already and start afresh
      self.clear()
      records = self.get_all_records()
      for r in records:
         self.append(r)
      return

   def add_record(self, fields_and_data):

      log_entry = []
      field_names = self.SELECTED_FIELD_NAMES_ORDERED
      for i in range(0, len(field_names)):
         log_entry.append(fields_and_data[field_names[i]])

      with(self.connection):
         c = self.connection.cursor()
         query = "INSERT INTO %s VALUES (NULL" % self.name
         for i in range(0, len(field_names)):
            query = query + ",?"
         query = query + ")"
         c.execute(query, log_entry)
         index = c.lastrowid

      log_entry.insert(0, index) # Add the record's index.

      self.append(log_entry)

      return

   def delete_record(self, index, iter):
      # Get the selected row in the logbook
      with(self.connection):
         c = self.connection.cursor()
         query = "DELETE FROM %s" % self.name
         c.execute(query+" WHERE id=?", [index])
      self.remove(iter)
      return

   def edit_record(self, index, field_name, data):
      with(self.connection):
         c = self.connection.cursor()
         query = "UPDATE %s SET %s" % (self.name, field_name)
         query = query + "=? WHERE id=?"
         c.execute(query, [data, index])
      return

   def get_record_by_index(self, index):
      c = self.connection.cursor()
      query = "SELECT * FROM %s WHERE id=?" % self.name
      c.execute(query, [index])
      return c.fetchone()

   def get_all_records(self):
      c = self.connection.cursor()
      c.execute("SELECT * FROM %s" % self.name)
      return c.fetchall()

   def get_number_of_records(self):
      c = self.connection.cursor()
      c.execute("SELECT Count(*) FROM %s" % self.name)
      return c.fetchone()[0]

