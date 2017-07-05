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
from pyqso.adif import *


class TestADIF(unittest.TestCase):

    """ The unit tests for the ADIF class. """

    def setUp(self):
        """ Set up the ADIF object needed for the unit tests. """
        self.adif = ADIF()

    def test_read(self):
        """ Check that a single ADIF record can be read and parsed correctly. """
        f = open("ADIF.test_read.adi", 'w')
        f.write("""Some test ADI data.<eoh>

<call:4>TEST<band:3>40m<mode:2>CW
<qso_date:8:d>20130322<time_on:4>1955<eor>""")
        f.close()

        records = self.adif.read("ADIF.test_read.adi")
        expected_records = [{'TIME_ON': '1955', 'BAND': '40m', 'CALL': 'TEST', 'MODE': 'CW', 'QSO_DATE': '20130322'}]
        print("Imported records: ", records)
        print("Expected records: ", expected_records)
        assert(len(records) == 1)
        assert(len(list(records[0].keys())) == len(list(expected_records[0].keys())))
        assert(records == expected_records)

    def test_read_multiple(self):
        """ Check that multiple ADIF records can be read and parsed correctly. """
        f = open("ADIF.test_read_multiple.adi", 'w')
        f.write("""Some test ADI data.<eoh>

<call:4>TEST<band:3>40m<mode:2>CW
<qso_date:8:d>20130322<time_on:4>1955<eor>

<call:8>TEST2ABC<band:3>20m<mode:3>SSB
<qso_date:8>20150227<time_on:4>0820<eor>

<call:5>HELLO<band:2>2m<mode:2>FM<qso_date:8:d>20150227<time_on:4>0832<eor>""")
        f.close()

        records = self.adif.read("ADIF.test_read_multiple.adi")
        expected_records = [{'TIME_ON': '1955', 'BAND': '40m', 'CALL': 'TEST', 'MODE': 'CW', 'QSO_DATE': '20130322'}, {'TIME_ON': '0820', 'BAND': '20m', 'CALL': 'TEST2ABC', 'MODE': 'SSB', 'QSO_DATE': '20150227'}, {'TIME_ON': '0832', 'BAND': '2m', 'CALL': 'HELLO', 'MODE': 'FM', 'QSO_DATE': '20150227'}]
        print("Imported records: ", records)
        print("Expected records: ", expected_records)
        assert(len(records) == 3)
        for i in range(len(expected_records)):
            assert(len(list(records[i].keys())) == len(list(expected_records[i].keys())))
        assert(records == expected_records)

    def test_read_alphabet(self):
        """ Check that none of the letters of the alphabet are ignored during parsing. """
        f = open("ADIF.test_read_alphabet.adi", 'w')
        f.write("""Some test ADI data.<eoh>
<call:64>ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<eor>""")
        f.close()

        records = self.adif.read("ADIF.test_read_alphabet.adi")
        expected_records = [{'CALL': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'}]
        print("Imported records: ", records)
        print("Expected records: ", expected_records)
        assert(len(records) == 1)
        assert(len(list(records[0].keys())) == len(list(expected_records[0].keys())))
        assert(records == expected_records)

    def test_read_capitalisation(self):
        """ Check that the CALL field is capitalised correctly. """
        f = open("ADIF.test_read_capitalisation.adi", 'w')
        f.write("""Some test ADI data.<eoh>
<call:4>test<eor>""")
        f.close()

        records = self.adif.read("ADIF.test_read_capitalisation.adi")
        expected_records = [{'CALL': 'TEST'}]
        print("Imported records: ", records)
        print("Expected records: ", expected_records)
        assert(len(records) == 1)
        assert(len(list(records[0].keys())) == len(list(expected_records[0].keys())))
        assert(records == expected_records)

    def test_read_header_only(self):
        """ Check that no records are read in if the ADIF file only contains header information. """
        f = open("ADIF.test_read_header_only.adi", 'w')
        f.write("""Some test ADI data.<eoh>""")
        f.close()

        records = self.adif.read("ADIF.test_read_header_only.adi")
        expected_records = []
        print("Imported records: ", records)
        print("Expected records: ", expected_records)
        assert(len(records) == 0)
        assert(records == expected_records)

    def test_read_no_header(self):
        """ Check that an ADIF file can be parsed with no header information. """
        f = open("ADIF.test_read_no_header.adi", 'w')
        f.write("""<call:4>TEST<band:3>40m<mode:2>CW<qso_date:8:d>20130322<time_on:4>1955<eor>""")
        f.close()

        records = self.adif.read("ADIF.test_read_no_header.adi")
        expected_records = [{'TIME_ON': '1955', 'BAND': '40m', 'CALL': 'TEST', 'MODE': 'CW', 'QSO_DATE': '20130322'}]
        print("Imported records: ", records)
        print("Expected records: ", expected_records)
        assert(len(records) == 1)
        assert(len(list(records[0].keys())) == len(list(expected_records[0].keys())))
        assert(records == expected_records)

    def test_write(self):
        """ Check that records can be written to an ADIF file correctly. """
        records = [{"CALL": "TEST123", "QSO_DATE": "20120402", "TIME_ON": "1234", "FREQ": "145.500", "BAND": "2m", "MODE": "FM", "RST_SENT": "59", "RST_RCVD": "59"},
                   {"CALL": "TEST123", "QSO_DATE": "20130312", "TIME_ON": "0101", "FREQ": "145.750", "BAND": "2m", "MODE": "FM"}]
        self.adif.write(records, "ADIF.test_write.adi")

        f = open("ADIF.test_write.adi", 'r')
        text = f.read()
        print("File 'ADIF.test_write.adi' contains the following text:", text)
        assert("""
<adif_ver:5>3.0.4
<programid:5>PyQSO
<programversion:5>1.0.0
<eoh>
<call:7>TEST123
<qso_date:8>20120402
<time_on:4>1234
<freq:7>145.500
<band:2>2m
<mode:2>FM
<rst_sent:2>59
<rst_rcvd:2>59
<eor>
<call:7>TEST123
<qso_date:8>20130312
<time_on:4>0101
<freq:7>145.750
<band:2>2m
<mode:2>FM
<eor>
""" in text)  # Ignore the header line here, since it contains the date and time the ADIF file was written, which will change each time 'make unittest' is run.
        f.close()

    def test_write_sqlite3_Row(self):
        """ Check that records can be written to an ADIF file from a test database file. """
        import sqlite3
        import os.path
        path_to_test_database = os.path.join(os.path.realpath(os.path.dirname(__file__)), "res", "test.db")
        self.connection = sqlite3.connect(path_to_test_database)
        self.connection.row_factory = sqlite3.Row

        c = self.connection.cursor()
        c.execute("SELECT * FROM test")
        records = c.fetchall()
        print(records)

        self.adif.write(records, "ADIF.test_write_sqlite3_Row.adi")

        f = open("ADIF.test_write_sqlite3_Row.adi", 'r')
        text = f.read()
        print("File 'ADIF.test_write_sqlite3_Row.adi' contains the following text:", text)
        assert("""
<adif_ver:5>3.0.4
<programid:5>PyQSO
<programversion:5>1.0.0
<eoh>
<call:7>TEST123
<qso_date:8>20120402
<time_on:4>1234
<freq:7>145.500
<band:2>2m
<mode:2>FM
<rst_sent:2>59
<rst_rcvd:2>59
<eor>
<call:7>TEST456
<qso_date:8>20130312
<time_on:4>0101
<freq:7>145.750
<band:2>2m
<mode:2>FM
<eor>
""" in text)  # Ignore the header line here, since it contains the date and time the ADIF file was written, which will change each time 'make unittest' is run.
        f.close()

        self.connection.close()

    def test_is_valid(self):
        """ Check that ADIF field validation is working correctly for different data types. """
        assert(self.adif.is_valid("CALL", "TEST123", "S"))
        assert(self.adif.is_valid("QSO_DATE", "20120402", "D"))
        assert(self.adif.is_valid("TIME_ON", "1230", "T"))
        assert(self.adif.is_valid("TX_PWR", "5", "N"))

if(__name__ == '__main__'):
    unittest.main()
