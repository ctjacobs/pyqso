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

    @mock.patch('pyqso.logbook.Logbook.filter_by_callsign')
    def setUp(self, mock_filter_by_callsign):
        """ Set up the Logbook object and connection to the test database needed for the unit tests. """

        self.logbook = Logbook(application=mock.MagicMock())

        # Open the test database file.
        path_to_test_database = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir, "res/test.db")
        opened = self.logbook.open(path=path_to_test_database)
        assert(opened)
        assert(self.logbook.connection is not None)

        # Check that the logs have been retrieved.
        assert(len(self.logbook.logs) == 2)
        assert(self.logbook.logs[0].name == "test")
        assert(self.logbook.logs[1].name == "test2")

    def tearDown(self):
        """ Close the logbook and disconnect from the test database. """
        self.logbook.notebook.get_n_pages.return_value = 0
        closed = self.logbook.close()
        assert(closed)

    def test_db_disconnect(self):
        """ Check that the logbook can disconnect from the database. """
        disconnected = self.logbook.db_disconnect()
        assert(disconnected)
        # Attempt to disconnect again. This shouldn't do anything.
        disconnected = self.logbook.db_disconnect()
        assert(disconnected)

    def test_new(self):
        """  """
        #path_to_new_database = "Logbook.test_new.db"
        #opened = self.logbook.open(path=path_to_invalid_database)
        pass

    @mock.patch('pyqso.auxiliary_dialogs.handle_gtk_dialog')
    def test_open_invalid_logbook(self, mock_handle_gtk_dialog):
        """ Open an invalid database file (comprising only one line of plain text) and check that an error occurs. """
        path_to_invalid_database = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir, "res/invalid.db")
        opened = self.logbook.open(path=path_to_invalid_database)
        assert(not opened)
        assert(self.logbook.logs is None)

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

        # Consider only the first record of the first log.
        model = self.logbook.logs[0]
        path = Gtk.TreePath(0)
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

    def test_get_log_index(self):
        """ Check that a log's index can be resolved using the log's name. """
        assert(self.logbook.get_log_index(name="test") == 0)
        assert(self.logbook.get_log_index(name="test2") == 1)
        assert(self.logbook.get_log_index(name="helloworld") is None)

    @mock.patch('pyqso.logbook.Logbook.render_log')
    @mock.patch('pyqso.auxiliary_dialogs.handle_gtk_dialog')
    @mock.patch('pyqso.logbook.LogNameDialog')
    def test_new_log(self, mock_LogNameDialog, mock_handle_gtk_dialog, mock_render_log):
        """ Start off with an empty logbook and check that a new log can successfully be added. """
        f = open("Logbook.test_new_log.db", "w").close()
        opened = self.logbook.open(path="Logbook.test_new_log.db")
        self.logbook.summary = mock.MagicMock()
        assert(opened)
        mock_LogNameDialog().dialog.run.return_value = Gtk.ResponseType.OK
        mock_LogNameDialog().name = "my_new_log"
        self.logbook.new_log()
        assert(len(self.logbook.logs) == 1)
        assert(self.logbook.logs[0].name == "my_new_log")

if(__name__ == '__main__'):
    unittest.main()
