#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian Thomas Jacobs.

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

from pyqso.adif import AVAILABLE_FIELD_NAMES_ORDERED


class Log(Gtk.ListStore):

    """ A single log inside of the whole logbook. A Log object can store multiple records. This is """

    def __init__(self, connection, name):
        """ Set up a new Log object.

        :arg connection: An sqlite database connection.
        :arg str name: The name of the log (i.e. the database table name).
        """

        # The ListStore constructor needs to know the data types of the columns.
        # The index is always an integer. We will assume the fields are strings.
        data_types = [int] + [str]*len(AVAILABLE_FIELD_NAMES_ORDERED)
        # Call the constructor of the super class (Gtk.ListStore)
        Gtk.ListStore.__init__(self, *data_types)

        self.connection = connection
        self.name = name

        return

    def populate(self):
        """ Remove everything in the Gtk.ListStore that is rendered already (via the TreeView), and start afresh. """

        logging.debug("Populating '%s'..." % self.name)
        self.add_missing_db_columns()
        self.clear()

        try:
            records = self.records

            for r in records:
                liststore_entry = [r["id"]]
                for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
                    # Note: r may contain column names that are not in AVAILABLE_FIELD_NAMES_ORDERED,
                    # so we need to loop over and only select those that are, since the ListStore will
                    # expect a specific number of columns.
                    liststore_entry.append(r[field_name])
                self.append(liststore_entry)
            logging.debug("Finished populating '%s'." % self.name)

        except sqlite.Error as e:
            logging.error("Could not populate '%s' because of a database error." % self.name)
            logging.exception(e)

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
            c = self.connection.cursor()

            # Get all the column names in the current database table.
            c.execute("PRAGMA table_info(%s)" % self.name)
            column_names = c.fetchall()

            # Get the index/rowid of the last inserted record in the database.
            c.execute("SELECT max(id) FROM %s" % self.name)
            last_index = c.fetchone()[0]
            if last_index is None:
                # Assume no records are currently present.
                last_index = 0

        # A list of all the database entries, to be inserted in one go into the database.
        database_entries = []

        # Construct the SQL query.
        query = "INSERT INTO %s VALUES (NULL" % self.name
        for i in range(len(column_names)-1):  # -1 here because we don't want to count the database's 'id' column, since this is autoincremented.
            query = query + ",?"
        query = query + ")"

        # Gather all the records (making sure that the entries of each record are in the correct order).
        for r in range(len(fields_and_data)):
            # What if the database columns are not necessarily in the same order as (or even exist in) AVAILABLE_FIELD_NAMES_ORDERED?
            # PyQSO handles this here, but needs a separate list (called database_entry) to successfully perform the SQL query.
            database_entry = []
            for t in column_names:
                column_name = str(t[1])  # 't' here is a tuple
                if((column_name.upper() in AVAILABLE_FIELD_NAMES_ORDERED) and (column_name.upper() in list(fields_and_data[r].keys()))):
                    database_entry.append(fields_and_data[r][column_name.upper()])
                else:
                    if(column_name != "id"):  # Ignore the index/rowid field. This is a special case since it's not in AVAILABLE_FIELD_NAMES_ORDERED.
                        database_entry.append("")
            database_entries.append(database_entry)

        # Insert records in the database.
        with self.connection:
            c = self.connection.cursor()
            c.executemany(query, database_entries)

            # Get the indices/rowids of the newly-inserted records.
            query = "SELECT id FROM %s WHERE id > %s ORDER BY id ASC" % (self.name, last_index)
            c.execute(query)
            inserted = c.fetchall()

            # Check that the number of records we wanted to insert is the same as the number of records successfully inserted.
            assert(len(inserted) == len(database_entries))

            # Add the records to the ListStore as well.
            for r in range(len(fields_and_data)):
                liststore_entry = [inserted[r]["id"]]  # Add the record's index.
                field_names = AVAILABLE_FIELD_NAMES_ORDERED
                for i in range(0, len(field_names)):
                    if(field_names[i] in list(fields_and_data[r].keys())):
                        liststore_entry.append(fields_and_data[r][field_names[i]])
                    else:
                        liststore_entry.append("")
                self.append(liststore_entry)

        logging.debug("Successfully added the record(s) to the log.")
        return

    def delete_record(self, index, iter=None):
        """ Delete a specified record from the log. The corresponding record is also deleted from the Gtk.ListStore data structure.

        :arg int index: The index of the record in the SQL database.
        :arg iter: The iterator pointing to the record to be deleted in the Gtk.ListStore. If the default value of None is used, only the database entry is deleted and the corresponding Gtk.ListStore is left alone.
        :raises sqlite.Error, IndexError: if the record could not be deleted.
        """
        logging.debug("Deleting record from log...")
        # Get the selected row in the logbook.
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
        :arg iter: The iterator pointing to the record to be edited in the Gtk.ListStore. If the default value of None is used, only the database entry is edited and the corresponding Gtk.ListStore is left alone.
        :arg column_index: The index of the column in the Gtk.ListStore to be edited. If the default value of None is used, only the database entry is edited and the corresponding Gtk.ListStore is left alone.
        :raises sqlite.Error, IndexError: if the record could not be edited.
        """
        logging.debug("Editing field '%s' in record %d..." % (field_name, index))
        try:
            with self.connection:
                c = self.connection.cursor()
                query = "UPDATE %s SET %s" % (self.name, field_name)
                query = query + "=? WHERE id=?"
                c.execute(query, [data, index])  # First update the SQL database...
            if(iter is not None and column_index is not None):
                self.set(iter, column_index, data)  # ...and then the ListStore.
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
            return (0, 0)  # Nothing to do here.

        removed = 0  # Count the number of records that are removed. Hopefully this will be the same as len(duplicates).
        iter = self.get_iter_first()  # Start with the first row in the log.
        prev = iter  # Keep track of the previous iter (initially this will be the same as the first row in the log).
        while iter is not None:
            row_index = self.get_value(iter, 0)  # Get the index.
            if(row_index in duplicates):  # Is this a duplicate row? If so, delete it.
                self.delete_record(row_index, iter)
                removed += 1
                iter = prev  # Go back to the iter before the record that was just removed and continue from there.
                continue
            prev = iter
            iter = self.iter_next(iter)  # Move on to the next row, until iter_next returns None.

        return (len(duplicates), removed)

    def rename(self, new_name):
        """ Rename the log.

        :arg str new_name: The new name for the log.
        :returns: True if the renaming process is successful. Otherwise returns False.
        :rtype: bool
        """
        try:
            with self.connection:
                # First try to alter the table name in the database.
                c = self.connection.cursor()
                query = "ALTER TABLE %s RENAME TO %s" % (self.name, new_name)
                c.execute(query)
            # If the table name change was successful, then change the name attribute of the Log object too.
            self.name = new_name
            success = True
        except sqlite.Error as e:
            logging.exception(e)
            success = False
        return success

    def get_duplicates(self):
        """ Find the duplicates in the log, based on the CALL, QSO_DATE, and TIME_ON fields.

        :returns: A list of indices/ids corresponding to the duplicate records.
        :rtype: list
        """
        duplicates = []
        try:
            with self.connection:
                c = self.connection.cursor()
                c.execute(
                    """SELECT id FROM %s WHERE id NOT IN
   (
   SELECT MIN(id) FROM %s GROUP BY call, qso_date, time_on
   )""" % (self.name, self.name))
                result = c.fetchall()
            for index in result:
                duplicates.append(index[0])  # Get the integer from inside the tuple.
            duplicates.sort()  # These indices should monotonically increasing, but let's sort the list just in case.
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

    @property
    def records(self):
        """ Return a list of all the records in the log.

        :returns: A list of all the records in the log. Each record is represented by a dictionary.
        :rtype: dict
        :raises sqlite.Error: If the records could not be retrieved from the database.
        """
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT * FROM %s" % self.name)
            return c.fetchall()

    @property
    def record_count(self):
        """ Return the total number of records in the log.

        :returns: The total number of records in the log.
        :rtype: int
        :raises sqlite.Error: If the record count could not be determined due to a database error.
        """
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT Count(*) FROM %s" % self.name)
            return c.fetchone()[0]
