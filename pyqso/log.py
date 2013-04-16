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
      with self.connection:
         # This is a new log/table, so create it in the database
         c = self.connection.cursor()
         query = "CREATE TABLE %s (id INTEGER PRIMARY KEY" % name
         for field_name in self.SELECTED_FIELD_NAMES_ORDERED:
            s = ", %s TEXT" % field_name.lower()
            query = query + s
         query = query + ")"
         c.execute(query)

      # Populate the ListStore with any existing records
      self.populate()
      
      logging.debug("New Log instance created!")
               
   def populate(self):
      # Remove everything that is rendered already and start afresh
      self.clear()
      records = self.get_all_records()
      if(len(records) > 0):
         self.append(records)
      return

   def add_record(self, fields_and_data):

      return

   def delete_record(self, index, iter):
      # Get the selected row in the logbook
      #self.records.pop(index)
      self.remove(iter)
      return

   def edit_record(self, index, field_name, data):
      #self.records[index].set_data(field_name, data)
      return

   def get_record_by_index(self, index):
      c = self.connection.cursor()
      c.execute("SELECT * FROM ? WHERE id=?", (self.name, index))
      return c.fetchone()

   def get_all_records(self):
      c = self.connection.cursor()
      c.execute("SELECT * FROM %s" % self.name)
      return c.fetchall()

   def get_number_of_records(self):
      c = self.connection.cursor()
      c.execute("SELECT Count(*) FROM %s" % self.name)
      return c.fetchone()[0]

