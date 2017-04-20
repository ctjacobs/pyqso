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

from gi.repository import Gtk
import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock
from pyqso.calendar_dialog import *


class TestCalendarDialog(unittest.TestCase):

    """ The unit tests for the CalendarDialog class. """

    def setUp(self):
        """ Set up the objects needed for the unit tests. """
        self.cd = CalendarDialog(application=mock.MagicMock())
        self.cd.calendar = Gtk.Calendar()
        self.cd.calendar.select_month(3, 2017)  # Note: Months start from 0 when using the Calendar widget. So "3" represents April here.
        self.cd.calendar.select_day(2)

    def tearDown(self):
        """ Destroy any unit test resources. """
        pass

    def test_date(self):
        """ Check that the date obtained from the Calendar is in the correct format. """
        assert(self.cd.date == "20170402")

if(__name__ == '__main__'):
    unittest.main()
