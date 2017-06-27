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
from pyqso.dx_cluster import *


class TestDXCluster(unittest.TestCase):

    """ The unit tests for the DXCluster class. """

    def setUp(self):
        """ Set up the objects needed for the unit tests. """

        PyQSO = mock.MagicMock()
        self.dxcluster = DXCluster(application=PyQSO())

    def test_on_telnet_io(self):
        """ Check that the response from the Telnet server can be correctly decoded. """

        telnetlib.Telnet = mock.Mock(spec=telnetlib.Telnet)
        connection = telnetlib.Telnet("hello", "world")
        connection.read_very_eager.return_value = b"Test message from the Telnet server."
        self.dxcluster.connection = connection
        result = self.dxcluster.on_telnet_io()
        assert(result)

if(__name__ == '__main__'):
    unittest.main()
