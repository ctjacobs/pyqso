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
from pyqso.compare import *


class TestCompare(unittest.TestCase):

    """ The unit tests for the Compare class. """

    def setUp(self):
        data_types = [int] + [str]*3
        self.model = Gtk.ListStore(*data_types)
        row1 = [0, "100", "20150323", "1433"]
        self.model.append(row1)
        row2 = [1, "5000", "20160423", "1432"]
        self.model.append(row2)
        row3 = [2, "5000", "20160423", "1433"]
        self.model.append(row3)
        row4 = [3, "25", "20160423", "1433"]
        self.model.append(row4)
        return

    def tearDown(self):
        return

    def test_compare_default(self):
        """ Check the correctness of the default comparison scheme. """

        # Get the row iterables.
        path = Gtk.TreePath(0)
        iter1 = self.model.get_iter(path)
        iter2 = self.model.iter_next(iter1)
        iter3 = self.model.iter_next(iter2)
        iter4 = self.model.iter_next(iter3)

        # Compare values in the second column.
        column_index = 1
        result = compare_default(self.model, iter1, iter2, column_index)
        assert(result == 1)
        result = compare_default(self.model, iter2, iter3, column_index)
        assert(result == 0)
        result = compare_default(self.model, iter3, iter4, column_index)
        assert(result == -1)

    def test_compare_date_and_time(self):
        """ Check that dates in yyyymmdd format are compared correctly. """

        # Get the row iterables.
        path = Gtk.TreePath(0)
        iter1 = self.model.get_iter(path)
        iter2 = self.model.iter_next(iter1)
        iter3 = self.model.iter_next(iter2)
        iter4 = self.model.iter_next(iter3)

        # Compare values in the third (and fourth, if necessary) column.
        column_index = 2
        result = compare_date_and_time(self.model, iter1, iter2, [column_index, column_index+1])
        assert(result == 1)
        result = compare_date_and_time(self.model, iter2, iter3, [column_index, column_index+1])
        assert(result == 1)
        result = compare_date_and_time(self.model, iter3, iter4, [column_index, column_index+1])
        assert(result == 0)
        result = compare_date_and_time(self.model, iter4, iter1, [column_index, column_index+1])
        assert(result == -1)

if(__name__ == '__main__'):
    unittest.main()
