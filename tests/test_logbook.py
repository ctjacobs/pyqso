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
try:
    import unittest.mock as mock
except ImportError:
    import mock
import os
from pyqso.logbook import *


class TestLogbook(unittest.TestCase):

    """ The unit tests for the Logbook class. """

    def setUp(self):
        """ Set up the Logbook object and connection to the test database needed for the unit tests. """
        self.logbook = Logbook(application=mock.MagicMock())
        path_to_test_database = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir, "res/test.db")
        success = self.logbook.db_connect(path_to_test_database)
        assert(success)
        self.logbook.logs = self.logbook.get_logs()
        assert(self.logbook.logs is not None)
        # Check that the logs have been retrieved.
        temp = []
        for log_name in ["test", "test2"]:
            l = Log(self.logbook.connection, log_name)
            l.populate()
            temp.append(l)
        assert(self.logbook.logs[0].name == temp[0].name)
        assert(self.logbook.logs[1].name == temp[1].name)

    def tearDown(self):
        """ Disconnect from the test database. """
        success = self.logbook.db_disconnect()
        assert(success)

    def test_log_name_exists(self):
        """ Check that only the log called 'test' exists. """
        assert(self.logbook.log_name_exists("test"))  # Log 'test' exists.
        assert(not self.logbook.log_name_exists("hello"))  # Log 'hello' should not exist.

    def test_log_count(self):
        """ Check the log count. """
        assert(self.logbook.log_count == 2)

    def test_record_count(self):
        """ Check the total number of records over all the logs in the logbook. """
        assert(self.logbook.record_count == 7)

    def test_filter_by_callsign(self):
        """ Check that callsigns are filtered correctly. """
        data_types = [int] + [str]*3
        model = self.logbook.logs[0]  # Consider only the first log.

        path = Gtk.TreePath(0)  # Consider only the first record.
        iter = model.get_iter(path)

        self.logbook.application.toolbar.filter_source.get_text.return_value = ""
        present = self.logbook.filter_by_callsign(model, iter, data=None)
        assert(present)  # Show all the callsigns.

        self.logbook.application.toolbar.filter_source.get_text.return_value = "TEST123"
        present = self.logbook.filter_by_callsign(model, iter, data=None)
        assert(present)  # "TEST123" is present.

        self.logbook.application.toolbar.filter_source.get_text.return_value = "TEST"
        present = self.logbook.filter_by_callsign(model, iter, data=None)
        assert(present)  # "TEST" is present in "TEST123"

        self.logbook.application.toolbar.filter_source.get_text.return_value = "HELLOWORLD"
        present = self.logbook.filter_by_callsign(model, iter, data=None)
        assert(not present)  # "HELLOWORLD" is not present in "TEST123"

if(__name__ == '__main__'):
    unittest.main()
