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
from pyqso.awards import *
from pyqso.logbook import Logbook


class TestAwards(unittest.TestCase):

    """ The unit tests for the Awards class. """

    def setUp(self):
        """ Set up the objects needed for the unit tests. """
        PyQSO = mock.MagicMock()
        self.awards = Awards(application=PyQSO())
        self.logbook = Logbook(application=PyQSO())
        path_to_test_database = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir, "res/test.db")
        success = self.logbook.db_connect(path_to_test_database)
        assert(success)
        self.logbook.logs = self.logbook.get_logs()
        assert(self.logbook.logs is not None)

    def tearDown(self):
        """ Destroy any unit test resources. """
        pass

    def test_count(self):
        """ Check that there are 3 FM/AM/SSB/SSTV QSOs and 1 CW QSO. Note that the BAND must be specified in order to be counted. """
        count = self.awards.count(self.logbook)
        assert(sum(count[0]) == 3)  # FM/AM/SSB/SSTV
        assert(sum(count[1]) == 1)  # CW
        assert(sum(count[2]) == 1)  # Other modes
        assert(sum(count[3]) == 5)  # Mixed

if(__name__ == '__main__'):
    unittest.main()
