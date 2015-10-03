#!/usr/bin/env python 

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

from gi.repository import Gtk
import logging
import sqlite3 as sqlite
import unittest

from adif import AVAILABLE_FIELD_NAMES_ORDERED
from record_dialog import *

class Log(Gtk.ListStore):
   """ A single log inside of the whole logbook. A Log object can store multiple Record objects. """
   
   def __init__(self, connection, name):
      """ Set up a new Log object.
      
      :arg connection: An sqlite database connection.
      :arg str name: The name of the log (i.e. the sqlite table name).
      """

      # The ListStore constructor needs to know the data types of the columns.
      # The index is always an integer. We will assume the fields are strings.
      data_types = [int] + [str]*len(AVAILABLE_FIELD_NAMES_ORDERED)    
      # Call the constructor of the super class (Gtk.ListStore)
      Gtk.ListStore.__init__(self, *data_types)

      self.connection = connection
      self.name = name
      
      logging.debug("New Log instance created!")
      return

   def populate(self):
      """ Remove everything in the Gtk.ListStore that is rendered already (via the TreeView), and start afresh. """

      logging.debug("Populating '%s'..." % self.name)
      self.add_missing_db_columns()
      self.clear()
      records = self.get_all_records()
      if(records is not None):
         for r in records:
            liststore_entry = [r["id"]]
            for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
               # Note: r may contain column names that are not in AVAILABLE_FIELD_NAMES_ORDERED, 
               # so we need to loop over and only select those that are, since the ListStore will
               # expect a specific number of columns.
               liststore_entry.append(r[field_name])
            self.append(liststore_entry)
         logging.debug("Finished populating '%s'." % self.name)
      else:
         logging.error("Could not populate '%s' because of a database error." % self.name)
      return

   def add_missing_db_columns(self):
      """ Check whether each field name in AVAILABLE_FIELD_NAMES_ORDERED is in the database table. If not, add it
      (with all entries being set to an empty string initially).
      
      :raises sqlite.Error, IndexError: if the existing database column names could not be obtained, or missing column names could not be added.
      """
      logging.debug("Adding any missing database columns...")

      # Get all the column names in the current database table.
      column_names = []
      try:
         with self.connection:
            c = self.connection.cursor()
            c.execute("PRAGMA table_info(%s)" % self.name) 
            result = c.fetchall()
         for t in result:
            column_names.append(t[1].upper())
      except (sqlite.Error, IndexError) as e:
         logging.exception(e)
         logging.error("Could not obtain the database column names.")
         return

      for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
         if(not(field_name in column_names)):
            try:
               with self.connection:
                  c.execute("ALTER TABLE %s ADD COLUMN %s TEXT DEFAULT \"\"" % (self.name, field_name.lower()))
            except sqlite.Error as e:
               logging.exception(e)
               logging.error("Could not add the missing database column '%s'." % field_name)
               pass
      logging.debug("Finished adding any missing database columns.")
      return

   def add_record(self, fields_and_data):
      """ Add a record (or multiple records) to the log.
      
      :arg fields_and_data: A list of dictionaries (or possibly just a single dictionary), with each dictionary representing a single QSO, to be added to the log.
      """
      logging.debug("Adding record(s) to log...")
      
      # If a dictionary is given, assume that we only have one record to add.
      if isinstance(fields_and_data, dict):
         fields_and_data = [fields_and_data]
      
      with self.connection:
         # Get all the column names in the current database table.
         c = self.connection.cursor()
         c.execute("PRAGMA table_info(%s)" % self.name)
         column_names = c.fetchall()
         # Get the index of the last inserted record in the database.
         c.execute('SELECT max(id) FROM %s' % self.name)
         last_index = c.fetchone()[0]
         if last_index is None:
            # Assume no records are currently present.
            last_index = 0
      
      # A list of all the database entries, to be inserted in one go into the database.
      database_entries = []

      # Construct the SQL query.
      query = "INSERT INTO %s VALUES (NULL" % self.name
      for i in range(len(column_names)-1): # -1 here because we don't want to count the database's 'id' field.
         query = query + ",?"
      query = query + ")"
      
      # Gather all the records (making sure that the entries of each record are in the correct order).
      for r in range(len(fields_and_data)):
         # What if the database columns are not necessarily in the same order as (or even exist in) AVAILABLE_FIELD_NAMES_ORDERED?
         # PyQSO handles this here, but needs a separate list (called database_entry) to successfully perform the SQL query.
         database_entry = []
         for t in column_names:
            column_name = str(t[1]) # 't' here is a tuple
            if( (column_name.upper() in AVAILABLE_FIELD_NAMES_ORDERED) and (column_name.upper() in fields_and_data[r].keys()) ):
               database_entry.append(fields_and_data[r][column_name.upper()])
            else:
               if(column_name != "id"): # Ignore the row index field. This is a special case since it's not in AVAILABLE_FIELD_NAMES_ORDERED.
                  database_entry.append("")
         database_entries.append(database_entry)
         
         # Add the data to the ListStore as well.
         liststore_entry = []
         field_names = AVAILABLE_FIELD_NAMES_ORDERED
         for i in range(0, len(field_names)):
            if(field_names[i] in fields_and_data[r].keys()):
               liststore_entry.append(fields_and_data[r][field_names[i]])
            else:
               liststore_entry.append("")

         # Add the record's index.
         index = last_index + (r+1) # +1 here because r begins at zero, and we don't want to count the already-present record with index last_index.
         liststore_entry.insert(0, index)
         self.append(liststore_entry)
      
      # Execute the query.
      with self.connection:
         c.executemany(query, database_entries)
      
      logging.debug("Successfully added the record(s) to the log.")
      return

   def delete_record(self, index, iter=None):
      """ Delete a specified record from the log. The corresponding record is also deleted from the Gtk.ListStore data structure.
      
      :arg int index: The index of the record in the SQL database.
      :arg iter: iter should always be given. It is given a default value of None for unit testing purposes only.
      :raises sqlite.Error, IndexError: if the record could not be deleted.
      """
      logging.debug("Deleting record from log...")
      # Get the selected row in the logbook
      try:
         with self.connection:
            c = self.connection.cursor()
            query = "DELETE FROM %s" % self.name
            c.execute(query+" WHERE id=?", [index])
         if(iter is not None):
            self.remove(iter)
         logging.debug("Successfully deleted the record from the log.")
      except (sqlite.Error, IndexError) as e:
         logging.exception(e)
         logging.error("Could not delete the record from the log.")
      return

   def edit_record(self, index, field_name, data, iter=None, column_index=None):
      """ Edit a specified record by replacing the current data in a specified field with the data provided.
      
      :arg int index: The index of the record in the SQL database.
      :arg str field_name: The name of the field whose data should be modified.
      :arg str data: The data that should replace the current data in the field.
      :arg iter: Should always be given. A default value of None is used for unit testing purposes only.
      :arg column_index: Should always be given. A default value of None is used for unit testing purposes only.
      :raises sqlite.Error, IndexError: if the record could not be edited.
      """
      logging.debug("Editing field '%s' in record %d..." % (field_name, index))
      try:
         with self.connection:
            c = self.connection.cursor()
            query = "UPDATE %s SET %s" % (self.name, field_name)
            query = query + "=? WHERE id=?"
            c.execute(query, [data, index]) # First update the SQL database...
         if(iter is not None and column_index is not None):
            self.set(iter, column_index, data) # ...and then the ListStore.
         logging.debug("Successfully edited field '%s' in record %d in the log." % (field_name, index))
      except (sqlite.Error, IndexError) as e:
         logging.exception(e)
         logging.error("Could not edit field %s in record %d in the log." % (field_name, index))
      return

   def remove_duplicates(self):
      """ Remove any duplicate records from the log.
      
      :returns: The total number of duplicates, and the number of duplicates that were successfully removed. Hopefully these will be the same.
      :rtype: tuple
      """
      duplicates = self.get_duplicates()
      if(len(duplicates) == 0):
         return (0, 0) # Nothing to do here.

      removed = 0 # Count the number of records that are removed. Hopefully this will be the same as len(duplicates).
      while removed != len(duplicates): # Unfortunately, in certain cases, extra passes may be necessary to ensure that all duplicates are removed.
         path = Gtk.TreePath(0) # Start with the first row in the log.
         iter = self.get_iter(path)
         while iter is not None:
            row_index = self.get_value(iter, 0) # Get the index.
            if(row_index in duplicates): # Is this a duplicate row? If so, delete it.
               self.delete_record(row_index, iter)
               removed += 1
            iter = self.iter_next(iter) # Move on to the next row, until iter_next returns None.

      assert(removed == len(duplicates))
      return (len(duplicates), removed)

   def get_duplicates(self):
      """ Find the duplicates in the log, based on the CALL, QSO_DATE, TIME_ON, FREQ and MODE fields.
      
      :returns: A list of row IDs corresponding to the duplicate records.
      :rtype: list
      """
      duplicates = []
      try:
         with self.connection:
            c = self.connection.cursor()
            c.execute(
   """SELECT rowid FROM %s WHERE rowid NOT IN
   (
   SELECT MIN(rowid) FROM %s GROUP BY call, qso_date, time_on, freq, mode
   )""" % (self.name, self.name))
            result = c.fetchall()
         for rowid in result:
            duplicates.append(rowid[0]) # Get the integer from inside the tuple.
      except (sqlite.Error, IndexError) as e:
         logging.exception(e)
      return duplicates
         
   def get_record_by_index(self, index):
      """ Return a record with a given index in the log.
      
      :arg int index: The index of the record in the SQL database.
      :returns: The desired record, represented by a dictionary of field-value pairs.
      :rtype: dict
      """
      try:
         with self.connection:
            c = self.connection.cursor()
            query = "SELECT * FROM %s WHERE id=?" % self.name
            c.execute(query, [index])
            return c.fetchone()
      except sqlite.Error as e:
         logging.exception(e)
         return None

   def get_all_records(self):
      """ Return a list of all the records in the log.
      
      :returns: A list of all the records in the log. Each record is represented by a dictionary. 
      :rtype: dict
      """
      try:
         with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT * FROM %s" % self.name)
            return c.fetchall()
      except sqlite.Error as e:
         logging.exception(e)
         return None

   def get_number_of_records(self):
      """ Return the total number of records in the log.
      
      :returns: The total number of records in the log.
      :rtype: int
      """
      try:
         with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT Count(*) FROM %s" % self.name)
            return c.fetchone()[0]
      except (sqlite.Error, IndexError) as e:
         logging.exception(e)
         return None

class TestLog(unittest.TestCase):

   def setUp(self):
      self.connection = sqlite.connect(":memory:")
      self.connection.row_factory = sqlite.Row

      self.field_names = ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]
      self.fields_and_data = {"CALL":"TEST123", "QSO_DATE":"20130312", "TIME_ON":"1234", "FREQ":"145.500", "BAND":"2m", "MODE":"FM", "RST_SENT":"59", "RST_RCVD":"59"}

      c = self.connection.cursor()
      query = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT"
      for field_name in self.field_names:
         s = ", %s TEXT" % field_name.lower()
         query = query + s
      query = query + ")"
      c.execute(query)

      self.log = Log(self.connection, "test")

   def tearDown(self):
      self.connection.close()

   def test_log_add_missing_db_columns(self):

      column_names_before = []
      column_names_after = []

      c = self.connection.cursor()
      c.execute("PRAGMA table_info(test)") 
      result = c.fetchall()
      for t in result:
         column_names_before.append(t[1].upper())

      self.log.add_missing_db_columns()

      c.execute("PRAGMA table_info(test)") 
      result = c.fetchall()
      for t in result:
         column_names_after.append(t[1].upper())

      print "Column names before: ", column_names_before
      print "Column names after: ", column_names_after

      assert(len(column_names_before) == len(self.field_names) + 1) # Added 1 here because of the "ID" column in all database tables.
      assert(len(column_names_after) == len(AVAILABLE_FIELD_NAMES_ORDERED) + 1)
      for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
         assert(field_name in column_names_after)

   def test_log_add_record(self):
      self.log.add_record(self.fields_and_data)
      c = self.connection.cursor()
      c.execute("SELECT * FROM test")
      records = c.fetchall()
      
      assert len(records) == 1
      
      for field_name in self.field_names:
         print self.fields_and_data[field_name], records[0][field_name]
         assert self.fields_and_data[field_name] == records[0][field_name]

   def test_log_delete_record(self):
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c = self.connection.cursor()
      c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))

      c.execute("SELECT * FROM test")
      records_before = c.fetchall()

      self.log.delete_record(1)

      c.execute("SELECT * FROM test")
      records_after = c.fetchall()

      assert(len(records_before) == 1)
      assert(len(records_after) == 0)
      
   def test_log_edit_record(self):
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c = self.connection.cursor()
      c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))

      c.execute("SELECT * FROM test")
      record_before = c.fetchall()[0]

      self.log.edit_record(1, "CALL", "TEST456")
      self.log.edit_record(1, "FREQ", "145.450")

      c.execute("SELECT * FROM test")
      record_after = c.fetchall()[0]

      assert(record_before["CALL"] == "TEST123")
      assert(record_after["CALL"] == "TEST456")
      assert(record_before["FREQ"] == "145.500")
      assert(record_after["FREQ"] == "145.450")

   def test_log_get_record_by_index(self):
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c = self.connection.cursor()
      c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))

      record = self.log.get_record_by_index(1)
      print "Contents of retrieved record: ", record
      for field_name in record.keys():
         if(field_name.upper() == "ID"):
            continue
         else:
            assert(record[field_name.upper()] == self.fields_and_data[field_name.upper()])
      assert(len(record) == len(self.fields_and_data) + 1)

   def test_log_get_all_records(self):
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c = self.connection.cursor()
      # Add the same record twice
      c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))
      c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))

      records = self.log.get_all_records()
      print "Contents of all retrieved records: ", records
      assert(len(records) == 2) # There should be 2 records
      for field_name in self.field_names:
         assert(records[0][field_name] == self.fields_and_data[field_name])
         assert(records[1][field_name] == self.fields_and_data[field_name])

   def test_log_get_number_of_records(self):
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c = self.connection.cursor()
      # Add the same record twice
      c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))
      c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))

      number_of_records = self.log.get_number_of_records()
      print "Number of records in the log: ", number_of_records
      assert(number_of_records == 2) # There should be 2 records

   def test_log_get_duplicates(self):
      query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
      c = self.connection.cursor()
      n = 5 # The total number of records to insert.
      for i in range(0, n):
         c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))
      assert len(self.log.get_duplicates()) == n-1 # Expecting n-1 duplicates.

if(__name__ == '__main__'):
   unittest.main()
