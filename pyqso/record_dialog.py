#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian T. Jacobs.

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
import logging
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


class RecordDialog(Gtk.Dialog):

    """ A dialog through which users can enter information about a QSO/record. """

    def __init__(self, parent, log, index=None):
        """ Set up the layout of the record dialog, populate the various fields with the QSO details (if the record already exists), and show the dialog to the user.

        :arg parent: The parent Gtk window.
        :arg log: The log to which the record belongs (or will belong).
        :arg int index: If specified, then the dialog turns into 'edit record mode' and fills the data sources (e.g. the Gtk.Entry boxes) with the existing data in the log. If not specified (i.e. index is None), then the dialog starts off with nothing in the data sources.
        """

        logging.debug("Setting up the record dialog...")

        self.parent = parent

        if(index is not None):
            title = "Edit Record %d" % index
        else:
            title = "Add Record"
        Gtk.Dialog.__init__(self, title=title, parent=parent.window, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        # Check if a configuration file is present, since we might need it to set up the rest of the dialog.
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])

        # QSO DATA FRAME
        qso_frame = Gtk.Frame()
        qso_frame.set_label("QSO Information")
        self.vbox.add(qso_frame)

        hbox_inner = Gtk.HBox(spacing=2)

        vbox_inner = Gtk.VBox(spacing=2)
        hbox_inner.pack_start(vbox_inner, True, True, 2)

        # Create label:entry pairs and store them in a dictionary
        self.sources = {}

        # CALL
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["CALL"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["CALL"] = Gtk.Entry()
        self.sources["CALL"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["CALL"], False, False, 2)
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_INFO, Gtk.IconSize.MENU)
        button = Gtk.Button()
        button.add(icon)
        button.connect("clicked", self.lookup_callback)  # Looks up the callsign using an online database, for callsign and station information.
        button.set_tooltip_text("Callsign lookup")
        hbox_temp.pack_start(button, True, True, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # DATE
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["QSO_DATE"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["QSO_DATE"] = Gtk.Entry()
        self.sources["QSO_DATE"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["QSO_DATE"], False, False, 2)
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_GO_BACK, Gtk.IconSize.MENU)
        button = Gtk.Button()
        button.add(icon)
        button.connect("clicked", self.calendar_callback)
        button.set_tooltip_text("Select date from calendar")
        hbox_temp.pack_start(button, True, True, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # TIME
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["TIME_ON"], halign=Gtk.Align.START)
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["TIME_ON"] = Gtk.Entry()
        self.sources["TIME_ON"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["TIME_ON"], False, False, 2)
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.MENU)
        button = Gtk.Button()
        button.add(icon)
        button.connect("clicked", self.set_current_datetime_callback)
        button.set_tooltip_text("Use the current time and date")
        hbox_temp.pack_start(button, True, True, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # FREQ
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["FREQ"], halign=Gtk.Align.START)
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["FREQ"] = Gtk.Entry()
        self.sources["FREQ"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["FREQ"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # BAND
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["BAND"], halign=Gtk.Align.START)
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)

        self.sources["BAND"] = Gtk.ComboBoxText()
        for band in BANDS:
            self.sources["BAND"].append_text(band)
        self.sources["BAND"].set_active(0)  # Set an empty string as the default option.
        hbox_temp.pack_start(self.sources["BAND"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # MODE
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["MODE"])
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)

        self.sources["MODE"] = Gtk.ComboBoxText()
        for mode in sorted(MODES.keys()):
            self.sources["MODE"].append_text(mode)
        self.sources["MODE"].set_active(0)  # Set an empty string as the default option.
        self.sources["MODE"].connect("changed", self._on_mode_changed)
        hbox_temp.pack_start(self.sources["MODE"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # SUBMODE
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["SUBMODE"])
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)

        self.sources["SUBMODE"] = Gtk.ComboBoxText()
        self.sources["SUBMODE"].append_text("")
        self.sources["SUBMODE"].set_active(0)  # Set an empty string initially. As soon as the user selects a particular MODE, the available SUBMODES will appear.
        hbox_temp.pack_start(self.sources["SUBMODE"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # POWER
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["TX_PWR"], halign=Gtk.Align.START)
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["TX_PWR"] = Gtk.Entry()
        self.sources["TX_PWR"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["TX_PWR"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        vbox_inner = Gtk.VBox(spacing=2)
        hbox_inner.pack_start(Gtk.SeparatorToolItem(), False, False, 0)
        hbox_inner.pack_start(vbox_inner, True, True, 2)

        # RST_SENT
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["RST_SENT"])
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["RST_SENT"] = Gtk.Entry()
        self.sources["RST_SENT"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["RST_SENT"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # RST_RCVD
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["RST_RCVD"])
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["RST_RCVD"] = Gtk.Entry()
        self.sources["RST_RCVD"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["RST_RCVD"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # QSL_SENT
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["QSL_SENT"])
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        qsl_options = ["", "Y", "N", "R", "I"]
        self.sources["QSL_SENT"] = Gtk.ComboBoxText()
        for option in qsl_options:
            self.sources["QSL_SENT"].append_text(option)
        self.sources["QSL_SENT"].set_active(0)  # Set an empty string as the default option.
        hbox_temp.pack_start(self.sources["QSL_SENT"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # QSL_RCVD
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["QSL_RCVD"])
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        qsl_options = ["", "Y", "N", "R", "I"]
        self.sources["QSL_RCVD"] = Gtk.ComboBoxText()
        for option in qsl_options:
            self.sources["QSL_RCVD"].append_text(option)
        self.sources["QSL_RCVD"].set_active(0)  # Set an empty string as the default option.
        hbox_temp.pack_start(self.sources["QSL_RCVD"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # NOTES
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["NOTES"])
        label.set_alignment(0, 0.5)
        label.set_width_chars(15)
        hbox_temp.pack_start(label, False, False, 2)
        self.textview = Gtk.TextView()
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.textview)
        self.sources["NOTES"] = self.textview.get_buffer()
        hbox_temp.pack_start(sw, True, True, 2)
        vbox_inner.pack_start(hbox_temp, True, True, 2)

        qso_frame.add(hbox_inner)

        # STATION INFORMATION FRAME
        station_frame = Gtk.Frame()
        station_frame.set_label("Station Information")
        self.vbox.add(station_frame)

        hbox_inner = Gtk.HBox(spacing=2)

        vbox_inner = Gtk.VBox(spacing=2)
        hbox_inner.pack_start(vbox_inner, True, True, 2)

        # NAME
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["NAME"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["NAME"] = Gtk.Entry()
        self.sources["NAME"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["NAME"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # ADDRESS
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["ADDRESS"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["ADDRESS"] = Gtk.Entry()
        self.sources["ADDRESS"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["ADDRESS"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # STATE
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["STATE"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["STATE"] = Gtk.Entry()
        self.sources["STATE"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["STATE"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # COUNTRY
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["COUNTRY"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["COUNTRY"] = Gtk.Entry()
        self.sources["COUNTRY"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["COUNTRY"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        vbox_inner = Gtk.VBox(spacing=2)
        hbox_inner.pack_start(Gtk.SeparatorToolItem(), False, False, 0)
        hbox_inner.pack_start(vbox_inner, True, True, 2)

        # DXCC
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["DXCC"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["DXCC"] = Gtk.Entry()
        self.sources["DXCC"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["DXCC"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # CQZ
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["CQZ"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["CQZ"] = Gtk.Entry()
        self.sources["CQZ"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["CQZ"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # ITUZ
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["ITUZ"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["ITUZ"] = Gtk.Entry()
        self.sources["ITUZ"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["ITUZ"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        # IOTA
        hbox_temp = Gtk.HBox(spacing=0)
        label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["IOTA"], halign=Gtk.Align.START)
        label.set_width_chars(15)
        label.set_alignment(0, 0.5)
        hbox_temp.pack_start(label, False, False, 2)
        self.sources["IOTA"] = Gtk.Entry()
        self.sources["IOTA"].set_width_chars(15)
        hbox_temp.pack_start(self.sources["IOTA"], False, False, 2)
        vbox_inner.pack_start(hbox_temp, False, False, 2)

        station_frame.add(hbox_inner)

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
                elif(field_names[i] == "MODE"):
                    self.sources[field_names[i]].set_active(sorted(MODES.keys()).index(data))

                    submode_data = record["submode"]
                    if(submode_data is None):
                        submode_data = ""
                    self.sources["SUBMODE"].set_active(MODES[data].index(submode_data))
                elif(field_names[i] == "SUBMODE"):
                    continue
                elif(field_names[i] == "QSL_SENT" or field_names[i] == "QSL_RCVD"):
                    self.sources[field_names[i]].set_active(qsl_options.index(data))
                elif(field_names[i] == "NOTES"):
                    # Remember to put the new line escape characters back in when displaying the data in a Gtk.TextView
                    text = data.replace("\\n", "\n")
                    self.sources[field_names[i]].set_text(text)
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
                    autofill = (config.get("hamlib", "autofill") == "True")
                    rig_model = config.get("hamlib", "rig_model")
                    rig_pathname = config.get("hamlib", "rig_pathname")
                    if(autofill):
                        self._hamlib_autofill(rig_model, rig_pathname)

        # Do we want PyQSO to autocomplete the Band field based on the Frequency field?
        (section, option) = ("records", "autocomplete_band")
        if(have_config and config.has_option(section, option)):
            autocomplete_band = (config.get(section, option) == "True")
            if(autocomplete_band):
                self.sources["FREQ"].connect("changed", self._autocomplete_band)
        else:
            # If no configuration file exists, autocomplete the Band field by default.
            self.sources["FREQ"].connect("changed", self._autocomplete_band)

        self.show_all()

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
        elif(field_name == "MODE"):
            return self.sources["MODE"].get_active_text()
        elif(field_name == "SUBMODE"):
            return self.sources["SUBMODE"].get_active_text()
        elif(field_name == "BAND" or field_name == "QSL_SENT" or field_name == "QSL_RCVD"):
            return self.sources[field_name].get_active_text()
        elif(field_name == "NOTES"):
            (start, end) = self.sources[field_name].get_bounds()
            text = self.sources[field_name].get_text(start, end, True)
            # Replace the escape characters with a slightly different new line marker.
            # If we don't do this, the rows in the Gtk.TreeView expand based on the number of new lines.
            text = text.replace("\n", "\\n")
            return text
        else:
            return self.sources[field_name].get_text()

    def _on_mode_changed(self, combo):
        """ If the MODE field has changed its value, then fill the SUBMODE field with all the available SUBMODE options for that new MODE. """
        self.sources["SUBMODE"].get_model().clear()
        text = combo.get_active_text()
        for submode in MODES[text]:
            self.sources["SUBMODE"].append_text(submode)
        return

    def _autocomplete_band(self, widget=None):
        """ If a value for the Frequency is entered, this function autocompletes the Band field. """

        frequency = self.sources["FREQ"].get_text()
        # Check whether we actually have a (valid) value to use. If not, set the BAND field to an empty string ("").
        try:
            frequency = float(frequency)
        except ValueError:
            self.sources["BAND"].set_active(0)
            return

        # Find which band the frequency lies in.
        for i in range(1, len(BANDS)):
            if(frequency >= BANDS_RANGES[i][0] and frequency <= BANDS_RANGES[i][1]):
                self.sources["BAND"].set_active(i)
                return

        self.sources["BAND"].set_active(0)  # If we've reached this, then the frequency does not lie in any of the specified bands.
        return

    def _hamlib_autofill(self, rig_model, rig_pathname):
        """ Set the various fields using data from the radio via Hamlib.

        :arg str rig_model: The model of the radio/rig.
        :arg str rig_pathname: The path to the rig (or rig control device).
        """

        # Open a communication channel to the radio.
        try:
            Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_NONE)
            rig = Hamlib.Rig(Hamlib.__dict__[rig_model])  # Look up the model's numerical index in Hamlib's symbol dictionary
            rig.set_conf("rig_pathname", rig_pathname)
            rig.open()
        except:
            logging.error("Could not open a communication channel to the rig via Hamlib!")
            return

        # Frequency
        try:
            frequency = "%.6f" % (rig.get_freq()/1.0e6)  # Converting to MHz here
            self.sources["FREQ"].set_text(frequency)
        except:
            logging.error("Could not obtain the current frequency via Hamlib!")

        # Mode
        try:
            (mode, width) = rig.get_mode()
            mode = mode.upper()
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

    def lookup_callback(self, widget=None):
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
            error(parent=self, message="To perform a callsign lookup, please specify the name of the callsign database in the Preferences.")
            return

        try:
            if(database == "qrz.com"):
                # QRZ.com
                callsign_lookup = CallsignLookupQRZ(parent=self)
            elif(database == "hamqth.com"):
                # HamQTH
                callsign_lookup = CallsignLookupHamQTH(parent=self)
            else:
                raise ValueError("Unknown callsign database: %s" % database)
        except ValueError as e:
            logging.exception(e)
            error(e)
            return

        # Get username and password from configuration file
        if(have_config and config.has_option("records", "callsign_database_username") and config.has_option("records", "callsign_database_password")):
            username = config.get("records", "callsign_database_username")
            password = base64.b64decode(config.get("records", "callsign_database_password")).decode("utf-8")
            if(username == "" or password == ""):
                details_given = False
            else:
                details_given = True
        else:
            details_given = False
        if(not details_given):
            error(parent=self, message="To perform a callsign lookup, please specify your username and password in the Preferences.")
            return

        # Connect and look up
        connected = callsign_lookup.connect(username, password)
        if(connected):
            full_callsign = self.sources["CALL"].get_text()
            # Check whether we want to ignore any prefixes (e.g. "IA/") or suffixes "(e.g. "/M") in the callsign
            # before performing the lookup.
            if(have_config and config.has_option("records", "ignore_prefix_suffix")):
                ignore_prefix_suffix = (config.get("records", "ignore_prefix_suffix") == "True")
            else:
                ignore_prefix_suffix = True

            fields_and_data = callsign_lookup.lookup(full_callsign, ignore_prefix_suffix=ignore_prefix_suffix)
            for field_name in list(fields_and_data.keys()):
                self.sources[field_name].set_text(fields_and_data[field_name])
        return

    def calendar_callback(self, widget):
        """ Open up a calendar widget for easy QSO_DATE selection. Return None after the user destroys the dialog. """
        c = CalendarDialog(self.parent.builder)
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
            use_utc = (config.get(section, option) == "True")
            if(use_utc):
                dt = datetime.utcnow()
            else:
                dt = datetime.now()
        else:
            dt = datetime.utcnow()  # Use UTC by default, since this is expected by ADIF.

        self.sources["QSO_DATE"].set_text(dt.strftime("%Y%m%d"))
        self.sources["TIME_ON"].set_text(dt.strftime("%H%M"))

        return
