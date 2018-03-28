#!/usr/bin/env python3

#    Copyright (C) 2018 Christian Thomas Jacobs.

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
from pyqso.world_map import *


class TestMaidenhead(unittest.TestCase):

    """ The unit tests for the Maidenhead class. """

    def setUp(self):
        """ Set up the Maidenhead object needed for the unit tests. """
        self.maidenhead = Maidenhead()

    def test_ll2gs(self):
        """ Check that a latitude-longitude coordinate can correctly be converted to a Maidenhead grid square. """
        latitude = 51.0593
        longitude = -1.4262
        assert self.maidenhead.ll2gs(latitude, longitude, subsquare=False) == "IO91"
        assert self.maidenhead.ll2gs(latitude, longitude, subsquare=True) == "IO91gb"

    def test_gs2ll(self):
        """ Check that a Maidenhead grid square can correctly be converted to a latitude-longitude coordinate. """
        gs4 = "JN05"
        assert self.maidenhead.gs2ll(gs4) == (45.5, 1.0)
        gs6 = "JN05aa"
        assert self.maidenhead.gs2ll(gs6) == (45.020833333333336, 0.041666666666666664)
        gs6 = "IO91gb"
        assert self.maidenhead.gs2ll(gs6) == (51.0625, -1.4583333333333335)


class TestWorldMap(unittest.TestCase):

    """ The unit tests for the WorldMap class. """

    def setUp(self):
        """ Set up the WorldMap object needed for the unit tests. """
        PyQSO = mock.MagicMock()
        self.world_map = WorldMap(application=PyQSO())

    def test_get_worked_grid_squares(self):
        """ Check that the worked grid squares are determined correctly. """
        Logbook = mock.MagicMock()
        Log = mock.MagicMock()
        logbook = Logbook()
        l = Log()
        l.records = [{"CALL": "TEST123", "COUNTRY": "England", "GRIDSQUARE": "IO91gb"}, {"CALL": "TEST456", "COUNTRY": "England", "GRIDSQUARE": "IO90hv"}, {"CALL": "TEST789", "COUNTRY": "England", "GRIDSQUARE": None}]
        logbook.logs = [l]
        worked_grid_squares = self.world_map.get_worked_grid_squares(logbook=logbook)
        assert worked_grid_squares[14, 8]  # IO square.

if(__name__ == '__main__'):
    unittest.main()
