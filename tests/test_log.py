#!/usr/bin/env python3

#    Copyright (C) 2017 Christian Thomas Jacobs.

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

import unittest
from pyqso.log import *


class TestLog(unittest.TestCase):

    """ The unit tests for the Log class. """

    def setUp(self):
        self.connection = sqlite.connect(":memory:")
        self.connection.row_factory = sqlite.Row

        self.field_names = ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]
        self.fields_and_data = {"CALL": "TEST123", "QSO_DATE": "20130312", "TIME_ON": "1234", "FREQ": "145.500", "BAND": "2m", "MODE": "FM", "RST_SENT": "59", "RST_RCVD": "59"}

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

        print("Column names before: ", column_names_before)
        print("Column names after: ", column_names_after)

        assert(len(column_names_before) == len(self.field_names) + 1)  # Added 1 here because of the "ID" column in all database tables.
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
            print(self.fields_and_data[field_name], records[0][field_name])
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
        print("Contents of retrieved record: ", record)
        for field_name in list(record.keys()):
            if(field_name.upper() == "ID"):
                continue
            else:
                assert(record[field_name.upper()] == self.fields_and_data[field_name.upper()])
        assert(len(record) == len(self.fields_and_data) + 1)

    def test_log_records(self):
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        # Add the same record twice
        c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))
        c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))

        records = self.log.records
        print("Contents of all retrieved records: ", records)
        assert(len(records) == 2)  # There should be 2 records
        for field_name in self.field_names:
            assert(records[0][field_name] == self.fields_and_data[field_name])
            assert(records[1][field_name] == self.fields_and_data[field_name])

    def test_log_record_count(self):
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        # Add the same record twice
        c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))
        c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))

        record_count = self.log.record_count
        print("Number of records in the log: ", record_count)
        assert(record_count == 2)  # There should be 2 records

    def test_log_get_duplicates(self):
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        n = 5  # The total number of records to insert.
        for i in range(0, n):
            c.execute(query, (self.fields_and_data["CALL"], self.fields_and_data["QSO_DATE"], self.fields_and_data["TIME_ON"], self.fields_and_data["FREQ"], self.fields_and_data["BAND"], self.fields_and_data["MODE"], self.fields_and_data["RST_SENT"], self.fields_and_data["RST_RCVD"]))
        assert(len(self.log.get_duplicates()) == n-1)  # Expecting n-1 duplicates.

    def test_log_rename(self):
        old_name = "test"
        new_name = "hello"
        success = self.log.rename(new_name)
        assert(success)
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE name=?)", [old_name])
            exists = c.fetchone()
            assert(exists[0] == 0)  # Old log name should no longer exist.
            c.execute("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE name=?)", [new_name])
            exists = c.fetchone()
            assert(exists[0] == 1)  # New log name should now exist.
        assert(self.log.name == new_name)

if(__name__ == '__main__'):
    unittest.main()
