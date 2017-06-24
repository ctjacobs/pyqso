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
import os
from pyqso.printer import *


class TestPrinter(unittest.TestCase):

    """ The unit tests for the Printer class. """

    def setUp(self):
        """ Set up the Printer object. """
        PyQSO = mock.MagicMock()
        self.printer = Printer(application=PyQSO())
        self.printer.application.window = Gtk.Window()

    def tearDown(self):
        """ Destroy any unit test resources. """
        return

    def test_print_records(self):
        """ Check that a list of records can be printed to a PDF file. """
        self.printer.action = Gtk.PrintOperationAction.EXPORT
        pdf = "Printer.test_print_records.pdf"
        self.printer.operation.set_export_filename(pdf)
        records = [{"CALL": "MYCALL", "QSO_DATE": "24062017", "TIME_ON": "1519", "FREQ": "145.550", "MODE": "FM"}]
        result = self.printer.print_records(records)
        assert(result != Gtk.PrintOperationResult.ERROR)
        assert(result == Gtk.PrintOperationResult.APPLY)
        assert(os.path.exists(pdf))

if(__name__ == '__main__'):
    unittest.main()
