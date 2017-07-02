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
from pyqso.record_dialog import *


class TestRecordDialog(unittest.TestCase):

    """ The unit tests for the RecordDialog class. """

    def setUp(self):
        """ Set up the objects needed for the unit tests. """
        PyQSO = mock.MagicMock()
        self.record_dialog = RecordDialog(application=PyQSO(), log=None)
        self.record_dialog.frequency_unit = "MHz"

        # Set up the necessary sources.
        self.record_dialog.sources["FREQ"] = Gtk.Entry()

        self.record_dialog.sources["BAND"] = Gtk.ComboBoxText()
        for band in BANDS:
            self.record_dialog.sources["BAND"].append_text(band)

        self.record_dialog.sources["MODE"] = Gtk.ComboBoxText()
        for mode in sorted(MODES.keys()):
            self.record_dialog.sources["MODE"].append_text(mode)

        self.record_dialog.sources["SUBMODE"] = Gtk.ComboBoxText()
        self.record_dialog.sources["SUBMODE"].append_text("")
        self.record_dialog.sources["SUBMODE"].set_active(0)

        return

    def test_autocomplete_band(self):
        """ Given a frequency, check that the band field is automatically set to the correct value. """
        self.record_dialog.sources["FREQ"].set_text("145.525")
        self.record_dialog.autocomplete_band()
        band = self.record_dialog.sources["BAND"].get_active_text()
        assert(band == "2m")

        self.record_dialog.sources["FREQ"].set_text("9001")
        self.record_dialog.autocomplete_band()
        band = self.record_dialog.sources["BAND"].get_active_text()
        assert(band == "")  # Frequency does not lie in any of the specified bands.

    def test_convert_frequency(self):
        """ Check that a frequency can be successfully converted from one unit to another. """
        frequency = "7.140"  # In MHz
        converted = self.record_dialog.convert_frequency(frequency, from_unit="MHz", to_unit="AHz")  # Unknown to_unit. This should return the input unmodified (and give an error message).
        assert(converted == frequency)
        converted = self.record_dialog.convert_frequency(frequency, from_unit="MHz", to_unit="kHz")  # Convert from MHz to kHz.
        assert(float(converted) == 1e3*float(frequency))
        converted = self.record_dialog.convert_frequency(converted, from_unit="kHz", to_unit="MHz")  # Convert from kHz back to MHz. This should give the original frequency.
        assert(float(converted) == float(frequency))

    def test_hamlib_autofill(self):
        """ Check that FREQ, MODE and SUBMODE information can be retrieved from Hamlib's dummy rig (if the Hamlib module exists). """
        if(have_hamlib):
            rig_model = "RIG_MODEL_DUMMY"
            rig_pathname = "/dev/Rig"
            self.record_dialog.hamlib_autofill(rig_model, rig_pathname)
            assert(self.record_dialog.sources["FREQ"].get_text() == "145.000000")
            assert(self.record_dialog.sources["MODE"].get_active_text() == "FM")
            assert(self.record_dialog.sources["SUBMODE"].get_active_text() == "")
        else:
            pass

if(__name__ == '__main__'):
    unittest.main()
