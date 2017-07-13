#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian Thomas Jacobs.

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

from gi.repository import Gtk, Gdk
import logging
import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from datetime import datetime
from os.path import expanduser
import base64
try:
    import Hamlib
    have_hamlib = True
except ImportError:
    logging.warning("Could not import the Hamlib module!")
    have_hamlib = False

from pyqso.adif import *
from pyqso.callsign_lookup import *
from pyqso.auxiliary_dialogs import *
from pyqso.calendar_dialog import CalendarDialog


class RecordDialog:

    """ A dialog through which users can enter information about a QSO/record. """

    def __init__(self, application, log, index=None):
        """ Set up the layout of the record dialog, populate the various fields with the QSO details (if the record already exists), and show the dialog to the user.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        :arg log: The log to which the record belongs (or will belong).
        :arg int index: If specified, then the dialog turns into 'edit record mode' and fills the data sources (e.g. the Gtk.Entry boxes) with the existing data in the log. If not specified (i.e. index is None), then the dialog starts off with nothing in the data sources.
        """

        logging.debug("Setting up the record dialog...")

        self.application = application
        self.builder = self.application.builder
        glade_file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "res", "pyqso.glade")
        self.builder.add_objects_from_file(glade_file_path, ("record_dialog",))
        self.dialog = self.builder.get_object("record_dialog")
        self.builder.get_object("record_dialog").connect("key-press-event", self.on_key_press)

        # Set dialog title
        if(index is not None):
            self.dialog.set_title("Edit Record %d" % index)
        else:
            self.dialog.set_title("Add Record")

        # Check if a configuration file is present, since we might need it to set up the rest of the dialog.
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])

        # Create label:entry pairs and store them in a dictionary
        self.sources = {}

        # QSO INFORMATION

        # CALL
        self.sources["CALL"] = self.builder.get_object("qso_call_entry")
        self.builder.get_object("callsign_lookup").connect("clicked", self.callsign_lookup_callback)

        # DATE
        self.sources["QSO_DATE"] = self.builder.get_object("qso_date_entry")
        self.builder.get_object("select_date").connect("clicked", self.calendar_callback)

        # TIME
        self.sources["TIME_ON"] = self.builder.get_object("qso_time_entry")
        self.builder.get_object("current_datetime").connect("clicked", self.set_current_datetime_callback)

        # FREQ
        self.sources["FREQ"] = self.builder.get_object("qso_frequency_entry")
        (section, option) = ("records", "default_frequency_unit")
        if(have_config and config.has_option(section, option)):
            self.frequency_unit = config.get(section, option)
            self.builder.get_object("qso_frequency_label").set_label("Frequency (%s)" % self.frequency_unit)
        else:
            self.frequency_unit = "MHz"

        # BAND
        self.sources["BAND"] = self.builder.get_object("qso_band_combo")
        for band in BANDS:
            self.sources["BAND"].append_text(band)
        self.sources["BAND"].set_active(0)  # Set an empty string as the default option.

        # MODE
        self.sources["MODE"] = self.builder.get_object("qso_mode_combo")
        for mode in sorted(MODES.keys()):
            self.sources["MODE"].append_text(mode)
        self.sources["MODE"].set_active(0)  # Set an empty string as the default option.
        self.sources["MODE"].connect("changed", self.on_mode_changed)

        # SUBMODE
        self.sources["SUBMODE"] = self.builder.get_object("qso_submode_combo")
        self.sources["SUBMODE"].append_text("")
        self.sources["SUBMODE"].set_active(0)  # Set an empty string initially. As soon as the user selects a particular MODE, the available SUBMODES will appear.

        # POWER
        self.sources["TX_PWR"] = self.builder.get_object("qso_power_entry")

        # RST_SENT
        self.sources["RST_SENT"] = self.builder.get_object("qso_rst_sent_entry")

        # RST_RCVD
        self.sources["RST_RCVD"] = self.builder.get_object("qso_rst_received_entry")

        # QSL_SENT
        self.sources["QSL_SENT"] = self.builder.get_object("qso_qsl_sent_combo")
        qsl_options = ["", "Y", "N", "R", "I"]
        for option in qsl_options:
            self.sources["QSL_SENT"].append_text(option)
        self.sources["QSL_SENT"].set_active(0)  # Set an empty string as the default option.

        # QSL_RCVD
        self.sources["QSL_RCVD"] = self.builder.get_object("qso_qsl_received_combo")
        qsl_options = ["", "Y", "N", "R", "I"]
        for option in qsl_options:
            self.sources["QSL_RCVD"].append_text(option)
        self.sources["QSL_RCVD"].set_active(0)  # Set an empty string as the default option.

        # NOTES
        self.sources["NOTES"] = self.builder.get_object("qso_notes_textview").get_buffer()

        # STATION INFORMATION

        # NAME
        self.sources["NAME"] = self.builder.get_object("station_name_entry")

        # ADDRESS
        self.sources["ADDRESS"] = self.builder.get_object("station_address_entry")

        # STATE
        self.sources["STATE"] = self.builder.get_object("station_state_entry")

        # COUNTRY
        self.sources["COUNTRY"] = self.builder.get_object("station_country_entry")

        # DXCC
        self.sources["DXCC"] = self.builder.get_object("station_dxcc_entry")

        # CQZ
        self.sources["CQZ"] = self.builder.get_object("station_cq_entry")

        # ITUZ
        self.sources["ITUZ"] = self.builder.get_object("station_itu_entry")

        # IOTA
        self.sources["IOTA"] = self.builder.get_object("station_iota_entry")

        # Populate various fields, if possible.
        if(index is not None):
            # The record already exists, so display its current data in the input boxes.
            record = log.get_record_by_index(index)
            field_names = AVAILABLE_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
                data = record[field_names[i].lower()]
                if(data is None):
                    data = ""
                if(field_names[i] == "BAND"):
                    self.sources[field_names[i]].set_active(BANDS.index(data))
                elif(field_names[i] == "FREQ" and self.frequency_unit != "MHz"):
                    converted = self.convert_frequency(data, from_unit="MHz", to_unit=self.frequency_unit)
                    self.sources[field_names[i]].set_text(str(converted))
                elif(field_names[i] == "MODE"):
                    self.sources[field_names[i]].set_active(sorted(MODES.keys()).index(data))
                    # Handle SUBMODE at the same time.
                    submode_data = record["submode"]
                    if(submode_data is None):
                        submode_data = ""
                    self.sources["SUBMODE"].set_active(MODES[data].index(submode_data))
                elif(field_names[i] == "SUBMODE"):
                    # Skip, because this has been (or will be) handled when populating the MODE field.
                    continue
                elif(field_names[i] == "QSL_SENT" or field_names[i] == "QSL_RCVD"):
                    self.sources[field_names[i]].set_active(qsl_options.index(data))
                else:
                    self.sources[field_names[i]].set_text(data)
        else:
            # Automatically fill in the current date and time
            self.set_current_datetime_callback()

            # Set up default field values
            # Mode
            (section, option) = ("records", "default_mode")
            if(have_config and config.has_option(section, option)):
                mode = config.get(section, option)
            else:
                mode = ""
            self.sources["MODE"].set_active(sorted(MODES.keys()).index(mode))

            # Submode
            (section, option) = ("records", "default_submode")
            if(have_config and config.has_option(section, option)):
                submode = config.get(section, option)
            else:
                submode = ""
            self.sources["SUBMODE"].set_active(MODES[mode].index(submode))

            # Power
            (section, option) = ("records", "default_power")
            if(have_config and config.has_option(section, option)):
                power = config.get(section, option)
            else:
                power = ""
            self.sources["TX_PWR"].set_text(power)

            # If the Hamlib module is present, then use it to fill in various fields if desired.
            if(have_hamlib):
                if(have_config and config.has_option("hamlib", "autofill") and config.has_option("hamlib", "rig_model") and config.has_option("hamlib", "rig_pathname")):
                    autofill = (config.getboolean("hamlib", "autofill"))
                    rig_model = config.get("hamlib", "rig_model")
                    rig_pathname = config.get("hamlib", "rig_pathname")
                    if(autofill):
                        self.hamlib_autofill(rig_model, rig_pathname)

        # Do we want PyQSO to autocomplete the Band field based on the Frequency field?
        (section, option) = ("records", "autocomplete_band")
        if(have_config and config.has_option(section, option)):
            autocomplete_band = (config.getboolean(section, option))
            if(autocomplete_band):
                self.sources["FREQ"].connect("changed", self.autocomplete_band)
        else:
            # If no configuration file exists, autocomplete the Band field by default.
            self.sources["FREQ"].connect("changed", self.autocomplete_band)

        self.dialog.show_all()

        logging.debug("Record dialog ready!")

        return

    def get_data(self, field_name):
        """ Return the data for a specified field from the Gtk.Entry/Gtk.ComboBoxText/etc boxes in the record dialog.

        :arg str field_name: The name of the field containing the desired data.
        :returns: The data in the specified field.
        :rtype: str
        """
        logging.debug("Retrieving the data in field %s from the record dialog..." % field_name)
        if(field_name == "CALL"):
            # Always show the callsigns in upper case.
            return self.sources[field_name].get_text().upper()
        elif(field_name == "FREQ" and self.frequency_unit != "MHz"):
            converted = self.convert_frequency(self.sources[field_name].get_text(), from_unit=self.frequency_unit, to_unit="MHz")
            return str(converted)
        elif(field_name == "MODE"):
            return self.sources["MODE"].get_active_text()
        elif(field_name == "SUBMODE"):
            return self.sources["SUBMODE"].get_active_text()
        elif(field_name == "BAND" or field_name == "QSL_SENT" or field_name == "QSL_RCVD"):
            return self.sources[field_name].get_active_text()
        elif(field_name == "NOTES"):
            (start, end) = self.sources[field_name].get_bounds()
            text = self.sources[field_name].get_text(start, end, True)
            return text
        else:
            return self.sources[field_name].get_text()

    def on_mode_changed(self, combo):
        """ If the MODE field has changed its value, then fill the SUBMODE field with all the available SUBMODE options for that new MODE. """
        self.sources["SUBMODE"].get_model().clear()
        mode = combo.get_active_text()
        for submode in MODES[mode]:
            self.sources["SUBMODE"].append_text(submode)
        self.sources["SUBMODE"].set_active(MODES[mode].index(""))  # Set the submode to an empty string.
        return

    def on_key_press(self, widget, event):
        """ If the Return key is pressed, emit the "OK" response to record the QSO. """
        child = widget.get_focus()
        if(not(isinstance(child, Gtk.ToggleButton) or isinstance(child, Gtk.Button) or isinstance(child, Gtk.TextView)) and event.keyval == Gdk.KEY_Return):
            self.dialog.emit('response', Gtk.ResponseType.OK)
        return

    def autocomplete_band(self, widget=None):
        """ If a value for the Frequency is entered, this function autocompletes the Band field. """

        frequency = self.sources["FREQ"].get_text()

        # Check whether we actually have a (valid) value to use. If not, set the BAND field to an empty string ("").
        try:
            frequency = float(frequency)
        except ValueError:
            self.sources["BAND"].set_active(0)
            return

        # Convert to MHz if necessary.
        if(self.frequency_unit != "MHz"):
            frequency = self.convert_frequency(frequency, from_unit=self.frequency_unit, to_unit="MHz")

        # Find which band the frequency lies in.
        for i in range(1, len(BANDS)):
            if(frequency >= BANDS_RANGES[i][0] and frequency <= BANDS_RANGES[i][1]):
                self.sources["BAND"].set_active(i)
                return

        self.sources["BAND"].set_active(0)  # If we've reached this, then the frequency does not lie in any of the specified bands.
        return

    def hamlib_autofill(self, rig_model, rig_pathname):
        """ Set the various fields using data from the radio via Hamlib.

        :arg str rig_model: The model of the radio/rig.
        :arg str rig_pathname: The path to the rig (or rig control device).
        """

        # Open a communication channel to the radio.
        try:
            Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_NONE)
            rig = Hamlib.Rig(Hamlib.__dict__[rig_model])  # Look up the model's numerical index in Hamlib's symbol dictionary.
            rig.set_conf("rig_pathname", rig_pathname)
            rig.open()
        except:
            logging.error("Could not open a communication channel to the rig via Hamlib!")
            return

        # Frequency
        try:
            frequency = "%.6f" % (rig.get_freq()/1.0e6)  # Converting to MHz here.
            # Convert to the desired unit, if necessary.
            if(self.frequency_unit != "MHz"):
                frequency = str(self.convert_frequency(frequency, from_unit="MHz", to_unit=self.frequency_unit))
            self.sources["FREQ"].set_text(frequency)
        except:
            logging.error("Could not obtain the current frequency via Hamlib!")

        # Mode
        try:
            (mode, width) = rig.get_mode()
            mode = Hamlib.rig_strrmode(mode).upper()
            # Handle USB and LSB as special cases.
            if(mode == "USB" or mode == "LSB"):
                submode = mode
                mode = "SSB"
                self.sources["MODE"].set_active(sorted(MODES.keys()).index(mode))
                self.sources["SUBMODE"].set_active(MODES[mode].index(submode))
            else:
                self.sources["MODE"].set_active(sorted(MODES.keys()).index(mode))
        except:
            logging.error("Could not obtain the current mode (e.g. FM, AM, CW) via Hamlib!")

        # Close communication channel.
        try:
            rig.close()
        except:
            logging.error("Could not close the communication channel to the rig via Hamlib!")

        return

    def callsign_lookup_callback(self, widget=None):
        """ Get the callsign-related data from an online database and store it in the relevant Gtk.Entry boxes, but return None. """

        # Get the database name.
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])
        try:
            if(have_config and config.has_option("records", "callsign_database")):
                database = config.get("records", "callsign_database")
                if(database == ""):
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            error(parent=self.dialog, message="To perform a callsign lookup, please specify the name of the callsign database in the Preferences.")
            return

        try:
            if(database == "qrz.com"):
                # QRZ.com
                callsign_lookup = CallsignLookupQRZ(parent=self.dialog)
            elif(database == "hamqth.com"):
                # HamQTH.com
                callsign_lookup = CallsignLookupHamQTH(parent=self.dialog)
            else:
                raise ValueError("Unknown callsign database: %s" % database)
        except ValueError as e:
            logging.exception(e)
            error(parent=self.dialog, message=e)
            return

        # Get username and password from configuration file.
        if(have_config and config.has_option("records", "callsign_database_username") and config.has_option("records", "callsign_database_password")):
            username = config.get("records", "callsign_database_username")
            password = base64.b64decode(config.get("records", "callsign_database_password")).decode("utf-8")
            if(not username or not password):
                details_given = False
            else:
                details_given = True
        else:
            details_given = False
        if(not details_given):
            error(parent=self.dialog, message="To perform a callsign lookup, please specify your username and password in the Preferences.")
            return

        # Get the callsign from the CALL field.
        full_callsign = self.sources["CALL"].get_text()
        if(not full_callsign):
            # Empty callsign field.
            error(parent=self.dialog, message="Please enter a callsign to lookup.")
            return

        # Connect to the database.
        connected = callsign_lookup.connect(username, password)
        if(connected):
            # Check whether we want to ignore any prefixes (e.g. "IA/") or suffixes "(e.g. "/M") in the callsign
            # before performing the lookup.
            if(have_config and config.has_option("records", "ignore_prefix_suffix")):
                ignore_prefix_suffix = (config.getboolean("records", "ignore_prefix_suffix"))
            else:
                ignore_prefix_suffix = True

            # Perform the lookup.
            fields_and_data = callsign_lookup.lookup(full_callsign, ignore_prefix_suffix=ignore_prefix_suffix)
            for field_name in list(fields_and_data.keys()):
                self.sources[field_name].set_text(fields_and_data[field_name])
        return

    def calendar_callback(self, widget):
        """ Open up a calendar widget for easy QSO_DATE selection. Return None after the user destroys the dialog. """
        c = CalendarDialog(self.application)
        response = c.dialog.run()
        if(response == Gtk.ResponseType.OK):
            self.sources["QSO_DATE"].set_text(c.date)
        c.dialog.destroy()
        return

    def set_current_datetime_callback(self, widget=None):
        """ Insert the current date and time. """

        # Check if a configuration file is present.
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])

        # Do we want to use UTC or the computer's local time?
        (section, option) = ("records", "use_utc")
        if(have_config and config.has_option(section, option)):
            use_utc = (config.getboolean(section, option))
            if(use_utc):
                dt = datetime.utcnow()
            else:
                dt = datetime.now()
        else:
            dt = datetime.utcnow()  # Use UTC by default, since this is expected by ADIF.

        self.sources["QSO_DATE"].set_text(dt.strftime("%Y%m%d"))
        self.sources["TIME_ON"].set_text(dt.strftime("%H%M"))

        return

    def convert_frequency(self, frequency, from_unit, to_unit):
        """ Convert a frequency from one unit to another.

        :arg float frequency: The frequency to convert.
        :arg str from_unit: The current unit of the frequency.
        :arg str to_unit: The desired unit of the frequency.
        :rtype: float
        :returns: The frequency in the to_unit.
        """
        scaling = {"Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}
        # Check that the from/to frequency units are valid.
        try:
            if(from_unit not in scaling.keys()):
                raise ValueError("Unknown frequency unit '%s' in from_unit" % from_unit)
            if(to_unit not in scaling.keys()):
                raise ValueError("Unknown frequency unit '%s' in to_unit" % to_unit)
        except ValueError as e:
            logging.exception(e)
            return frequency
        # Cast to float before scaling.
        if(not isinstance(frequency, float)):
            try:
                if(frequency == "" or frequency is None):
                    return frequency
                else:
                    frequency = float(frequency)
            except(ValueError, TypeError):
                logging.exception("Could not convert frequency to a floating-point value.")
                return frequency
        # Do not bother scaling if the units are the same.
        if(from_unit == to_unit):
            return frequency

        coefficient = scaling[from_unit]/scaling[to_unit]
        return float("%.6f" % (coefficient*frequency))
