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

import os
import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock
from pyqso.summary import *
from pyqso.logbook import Logbook


class TestSummary(unittest.TestCase):

    """ The unit tests for the Summary class. """

    def setUp(self):
        """ Set up the objects needed for the unit tests and create a connection to the test database. """
        PyQSO = mock.MagicMock()
        self.summary = Summary(application=PyQSO())
        self.summary.logbook = Logbook(application=PyQSO())
        path_to_test_database = os.path.join(os.path.realpath(os.path.dirname(__file__)), "res", "test.db")
        success = self.summary.logbook.db_connect(path_to_test_database)
        assert(success)
        self.summary.logbook.logs = self.summary.logbook.get_logs()
        assert(self.summary.logbook.logs is not None)

    def tearDown(self):
        """ Destroy the connection to the test database. """
        success = self.summary.logbook.db_disconnect()
        assert(success)

    def test_get_year_bounds(self):
        """ Check that the years of the earliest and latest QSO are correct. """
        year_min, year_max = self.summary.get_year_bounds()
        assert(year_min == 2012)
        assert(year_max == 2017)

    def test_get_annual_contact_count(self):
        """ Check that there are 3 QSOs in the year 2017. """
        count = self.summary.get_annual_contact_count(2017)
        april = datetime(2017, 4, 1)
        april_count = count[april]
        assert(april_count == 3)  # A total of 3 contacts made in April.
        assert(sum(count.values()) == 4)  # A total of 4 contacts made that whole year.

    def test_get_annual_mode_count(self):
        """ Check that, in the year 2017, there was 1 QSO made using CW, 2 QSOs made using FM, and 1 QSO made using SSB. """
        count = self.summary.get_annual_mode_count(2017)
        assert(count["CW"] == 1)
        assert(count["FM"] == 2)
        assert(count["SSB"] == 1)

if(__name__ == '__main__'):
    unittest.main()
