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
import unittest

from adif import AVAILABLE_FIELD_NAMES_TYPES, AVAILABLE_FIELD_NAMES_ORDERED
from record_dialog import *

class Log(Gtk.ListStore):
   """ A Log object can store multiple Record objects. """
   
   def __init__(self, connection, name):

      # The ListStore constructor needs to know the data types of the columns.
      # The index is always an integer. We will assume the fields are strings.
      data_types = [int] + [str]*len(AVAILABLE_FIELD_NAMES_ORDERED)    
      # Call the constructor of the super class (Gtk.ListStore)
      Gtk.ListStore.__init__(self, *data_types)

      self.connection = connection
      self.name = name
      
      logging.debug("New Log instance created!")

   def populate(self):
      """ Removes everything in the Gtk.ListStore that is rendered already (via the TreeView), and starts afresh """
      self.add_missing_db_columns()
      self.clear()
      records = self.get_all_records()
      for r in records:
         liststore_entry = [r["id"]]
         for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
            # Note: r may contain column names that are not in AVAILABLE_FIELD_NAMES_ORDERED, 
            # so we need to loop over and only select those that are, since the ListStore will
            # expect a specific number of columns.
            liststore_entry.append(r[field_name])
         self.append(liststore_entry)
      return

   def add_missing_db_columns(self):
      """ Checks whether each field name in AVAILABLE_FIELD_NAMES_ORDERED is in the database table. If not, PyQSO will add it
      (with all entries being set to NULL initially). """
      with(self.connection):
         c = self.connection.cursor()
      for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
         try:
            # Tries to add a column, regardless of whether it already exists or not.
            # If an error occurs, then PyQSO just continues onto the next field name without doing anything.
            # FIXME: The error will (hopefully) be caused by the column name already existing. But in the case of a different error,
            # a better solution should be implemented here.
            c.execute('ALTER TABLE %s ADD COLUMN %s' % (self.name, field_name.lower()))
         except:
            pass # Column already exists, so don't do anything.
      return

   def add_record(self, fields_and_data):
      """ Adds a record comprising data given in the 'fields_and_data' argument to the log. """
      liststore_entry = []
      field_names = AVAILABLE_FIELD_NAMES_ORDERED
      for i in range(0, len(field_names)):
         if(field_names[i] in fields_and_data.keys()):
            liststore_entry.append(fields_and_data[field_names[i]])
         else:
            liststore_entry.append("")

      with(self.connection):
         c = self.connection.cursor()
         # What if the database columns are not necessarily in the same order as (or even exist in) AVAILABLE_FIELD_NAMES_ORDERED?
         # PyQSO handles this here, but needs a separate list (called database_entry) to successfully perform the SQL query.
         database_entry = []
         c.execute("PRAGMA table_info(%s)" % self.name) # Get all the column names in the current database table.
         column_names = c.fetchall()
         query = "INSERT INTO %s VALUES (NULL" % self.name
         for t in column_names:
            # 't' here is a tuple
            column_name = str(t[1])
            if(column_name.upper() in AVAILABLE_FIELD_NAMES_ORDERED):
               database_entry.append(fields_and_data[column_name.upper()])
               query = query + ",?"
            else:
               if(column_name != "id"): # Ignore the row index field. This is a special case since it's not in AVAILABLE_FIELD_NAMES_ORDERED.
                  query = query + ",NULL"
         query = query + ")"
         c.execute(query, database_entry)
         index = c.lastrowid

      liststore_entry.insert(0, index) # Add the record's index.

      self.append(liststore_entry)

      return

   def delete_record(self, index, iter=None):
      """ Deletes a record with a specific index in the log. If 'iter' is not None, the corresponding record is also deleted from the Gtk.ListStore data structure. """
      # Get the selected row in the logbook
      with(self.connection):
         c = self.connection.cursor()
         query = "DELETE FROM %s" % self.name
         c.execute(query+" WHERE id=?", [index])

      if(iter is not None):
         self.remove(iter)
      return

   def edit_record(self, index, field_name, data):
      """ Edits a specified record by replacing the data in the field 'field_name' with the data given in the argument called 'data'. """
      with(self.connection):
         c = self.connection.cursor()
         query = "UPDATE %s SET %s" % (self.name, field_name)
         query = query + "=? WHERE id=?"
         c.execute(query, [data, index])
      return

   def get_record_by_index(self, index):
      """ Returns a record with a given index in the log. The record is represented by a dictionary of field-value pairs. """
      c = self.connection.cursor()
      query = "SELECT * FROM %s WHERE id=?" % self.name
      c.execute(query, [index])
      return c.fetchone()

   def get_all_records(self):
      """ Returns a list of all the records in the log. Each record is represented by a dictionary. """
      c = self.connection.cursor()
      c.execute("SELECT * FROM %s" % self.name)
      return c.fetchall()

   def get_number_of_records(self):
      """ Returns the total number of records in the log. """
      c = self.connection.cursor()
      c.execute("SELECT Count(*) FROM %s" % self.name)
      return c.fetchone()[0]

class TestLog(unittest.TestCase):

   def test_log_add_record(self):
      connection = sqlite.connect(":memory:")
      connection.row_factory = sqlite.Row
      
      c = connection.cursor()
      query = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT"
      for field_name in ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]:
         s = ", %s TEXT" % field_name.lower()
         query = query + s
      query = query + ")"
      c.execute(query)
      
      log = Log(connection, "test")
      fields_and_data = {"CALL":"TEST123", "QSO_DATE":"123456789", "TIME_ON":"123456789", "FREQ":"145.500", "BAND":"2m", "MODE":"FM", "RST_SENT":"59", "RST_RCVD":"59"}
      log.add_record(fields_and_data)
      c = connection.cursor()
      c.execute("SELECT * FROM test")
      records = c.fetchall()
      
      assert len(records) == 1
      
      for field_name in ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]:
         print fields_and_data[field_name], records[0][field_name]
         assert fields_and_data[field_name] == records[0][field_name]
      
      connection.close()

   def test_log_delete_record(self):
      connection = sqlite.connect(":memory:")
      connection.row_factory = sqlite.Row
      
      c = connection.cursor()
      query = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT"
      for field_name in ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]:
         s = ", %s TEXT" % field_name.lower()
         query = query + s
      query = query + ")"
      c.execute(query)
      
      log = Log(connection, "test")
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c.execute(query, ("TEST123", "123456789", "123456789", "145.500", "2m", "FM", "59", "59"))

      c.execute("SELECT * FROM test")
      records_before = c.fetchall()

      log.delete_record(1)

      c.execute("SELECT * FROM test")
      records_after = c.fetchall()

      assert(len(records_before) == 1)
      assert(len(records_after) == 0)

      connection.close()
      
   def test_log_edit_record(self):
      connection = sqlite.connect(":memory:")
      connection.row_factory = sqlite.Row
      
      c = connection.cursor()
      query = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT"
      for field_name in ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]:
         s = ", %s TEXT" % field_name.lower()
         query = query + s
      query = query + ")"
      c.execute(query)
      
      log = Log(connection, "test")
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c.execute(query, ("TEST123", "123456789", "123456789", "145.500", "2m", "FM", "59", "59"))

      c.execute("SELECT * FROM test")
      record_before = c.fetchall()[0]

      log.edit_record(1, "CALL", "TEST456")
      log.edit_record(1, "FREQ", "145.450")

      c.execute("SELECT * FROM test")
      record_after = c.fetchall()[0]

      assert(record_before["CALL"] == "TEST123")
      assert(record_after["CALL"] == "TEST456")
      assert(record_before["FREQ"] == "145.500")
      assert(record_after["FREQ"] == "145.450")

      connection.close()
              
if(__name__ == '__main__'):
   unittest.main()
