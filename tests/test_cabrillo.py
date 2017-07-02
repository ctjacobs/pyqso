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
from pyqso.cabrillo import *


class TestCabrillo(unittest.TestCase):

    """ The unit tests for the Cabrillo class. """

    def setUp(self):
        """ Set up the Cabrillo object needed for the unit tests. """
        self.cabrillo = Cabrillo()
        return

    def test_write(self):
        """ Check that QSOs are written correctly in Cabrillo format. """
        records = [{'TIME_ON': '1955', 'BAND': '40m', 'CALL': 'TEST', 'FREQ': "145.550", 'MODE': 'FM', 'QSO_DATE': '20130322', 'RST_SENT': '59 001', 'RST_RCVD': '59 002'}, {'TIME_ON': '0820', 'BAND': '20m', 'CALL': 'TEST2ABC', 'FREQ': "144.330", 'MODE': 'SSB', 'QSO_DATE': '20150227', 'RST_SENT': '55 020', 'RST_RCVD': '57 003'}, {'TIME_ON': '0832', 'BAND': '2m', 'CALL': 'HELLO', 'FREQ': "145.550", 'MODE': 'FM', 'QSO_DATE': '20150227', 'RST_SENT': '59 001', 'RST_RCVD': '59 002'}]

        expected = """START-OF-LOG: 3.0
CREATED-BY: PyQSO v1.0.0
CALLSIGN: MYCALL
CONTEST: MYCONTEST
QSO: 145550.0 FM 2013-03-22 1955 MYCALL 59 001 TEST 59 002 0
QSO: 144330.0 PH 2015-02-27 0820 MYCALL 55 020 TEST2ABC 57 003 0
QSO: 145550.0 FM 2015-02-27 0832 MYCALL 59 001 HELLO 59 002 0
END-OF-LOG:"""
        print("Expected Cabrillo file contents: ", expected)

        mycall = "MYCALL"
        mycontest = "MYCONTEST"
        path = "Cabrillo.test_write.log"
        success = self.cabrillo.write(records, path, contest=mycontest, mycall=mycall)
        assert(success)

        actual = ""
        f = open(path, "r")
        for line in f:
            actual += line
        f.close()
        print("Actual Cabrillo file contents: ", actual)
        assert(expected == actual)

if(__name__ == '__main__'):
    unittest.main()
