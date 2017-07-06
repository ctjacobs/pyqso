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
from pyqso.callsign_lookup import *


class TestCallsignLookup(unittest.TestCase):

    """ The unit tests for the callsign lookup functionality. """

    def setUp(self):
        """ Set up the objects needed for the unit tests. """
        self.qrz = CallsignLookupQRZ(parent=None)
        self.hamqth = CallsignLookupHamQTH(parent=None)

    def test_strip(self):
        """ Check that a callsign with a prefix and a suffix is stripped correctly. """
        callsign = "EA3/MYCALL/MM"
        assert strip(callsign) == "MYCALL"

    def test_strip_prefix_only(self):
        """ Check that a callsign with only a prefix is stripped correctly. """
        callsign = "EA3/MYCALL"
        assert strip(callsign) == "MYCALL"

    def test_strip_suffix_only(self):
        """ Check that a callsign with only a suffix is stripped correctly. """
        callsign = "MYCALL/M"
        assert strip(callsign) == "MYCALL"

    def test_strip_no_prefix_or_suffix(self):
        """ Check that a callsign with no prefix or suffix remains unmodified. """
        callsign = "MYCALL"
        assert strip(callsign) == "MYCALL"

    def test_qrz_connect(self):
        """ Check the example response from the qrz.com server, and make sure the session key has been correctly extracted. """

        http_client.HTTPConnection = mock.Mock(spec=http_client.HTTPConnection)
        http_client.HTTPResponse = mock.Mock(spec=http_client.HTTPResponse)
        connection = http_client.HTTPConnection()
        response = http_client.HTTPResponse()

        response.read.return_value = b'<?xml version="1.0" encoding="utf-8" ?>\n<QRZDatabase version="1.33" xmlns="http://xmldata.qrz.com">\n<Session>\n<Key>3b1fd1d3ba495189984f93ff67bd45b6</Key>\n<Count>61</Count>\n<SubExp>non-subscriber</SubExp>\n<GMTime>Sun Nov 22 21:25:34 2015</GMTime>\n<Remark>cpu: 0.147s</Remark>\n</Session>\n</QRZDatabase>\n'
        connection.getresponse.return_value = response

        result = self.qrz.connect("hello", "world")
        assert(result)
        assert(self.qrz.session_key == "3b1fd1d3ba495189984f93ff67bd45b6")

    def test_qrz_lookup(self):
        """ Check the example callsign lookup response from the qrz.com server, and make sure the callsign information has been correctly extracted. """

        http_client.HTTPConnection = mock.Mock(spec=http_client.HTTPConnection)
        http_client.HTTPResponse = mock.Mock(spec=http_client.HTTPResponse)
        connection = http_client.HTTPConnection()
        response = http_client.HTTPResponse()

        response.read.return_value = b'<?xml version="1.0" encoding="utf-8" ?>\n<QRZDatabase version="1.33" xmlns="http://xmldata.qrz.com">\n<Callsign>\n<call>MYCALL</call>\n<fname>FIRSTNAME</fname>\n<name>LASTNAME</name>\n<addr2>ADDRESS2</addr2>\n<country>COUNTRY</country>\n</Callsign>\n<Session>\n<Key>3b1fd1d3ba495189984f93ff67bd45b6</Key>\n<Count>61</Count>\n<SubExp>non-subscriber</SubExp>\n<Message>A subscription is required to access the complete record.</Message>\n<GMTime>Sun Nov 22 21:34:46 2015</GMTime>\n<Remark>cpu: 0.026s</Remark>\n</Session>\n</QRZDatabase>\n'
        connection.getresponse.return_value = response

        self.qrz.connection = connection
        self.qrz.session_key = "3b1fd1d3ba495189984f93ff67bd45b6"
        fields_and_data = self.qrz.lookup("MYCALL")
        assert(fields_and_data["NAME"] == "FIRSTNAME LASTNAME")
        assert(fields_and_data["ADDRESS"] == "ADDRESS2")
        assert(fields_and_data["COUNTRY"] == "COUNTRY")

    def test_hamqth_connect(self):
        """ Check the example response from the hamqth.com server, and make sure the session ID has been correctly extracted. """

        http_client.HTTPSConnection = mock.Mock(spec=http_client.HTTPSConnection)
        http_client.HTTPResponse = mock.Mock(spec=http_client.HTTPResponse)
        connection = http_client.HTTPSConnection()
        response = http_client.HTTPResponse()

        response.read.return_value = b'<?xml version="1.0"?>\n<HamQTH version="2.6" xmlns="https://www.hamqth.com">\n<session>\n<session_id>09b0ae90050be03c452ad235a1f2915ad684393c</session_id>\n</session>\n</HamQTH>\n'
        connection.getresponse.return_value = response

        result = self.hamqth.connect("hello", "world")
        assert(result)
        assert(self.hamqth.session_id == "09b0ae90050be03c452ad235a1f2915ad684393c")

    def test_hamqth_lookup(self):
        """ Check the example callsign lookup response from the hamqth.com server, and make sure the callsign information has been correctly extracted. """

        http_client.HTTPSConnection = mock.Mock(spec=http_client.HTTPSConnection)
        http_client.HTTPResponse = mock.Mock(spec=http_client.HTTPResponse)
        connection = http_client.HTTPSConnection()
        response = http_client.HTTPResponse()

        response.read.return_value = b'<?xml version="1.0"?>\n<HamQTH version="2.6" xmlns="https://www.hamqth.com">\n<search>\n<callsign>MYCALL</callsign>\n<nick>NAME</nick>\n<country>COUNTRY</country>\n<itu>ITU</itu>\n<cq>CQ</cq>\n<grid>GRID</grid>\n<adr_street1>ADDRESS</adr_street1>\n</search>\n</HamQTH>\n'
        connection.getresponse.return_value = response

        self.hamqth.connection = connection
        self.hamqth.session_id = "09b0ae90050be03c452ad235a1f2915ad684393c"
        fields_and_data = self.hamqth.lookup("MYCALL")
        assert(fields_and_data["NAME"] == "NAME")
        assert(fields_and_data["ADDRESS"] == "ADDRESS")
        assert(fields_and_data["COUNTRY"] == "COUNTRY")
        assert(fields_and_data["CQZ"] == "CQ")
        assert(fields_and_data["ITUZ"] == "ITU")
        assert(fields_and_data["IOTA"] == "GRID")

if(__name__ == '__main__'):
    unittest.main()
