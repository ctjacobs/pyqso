#!/usr/bin/env python
# File: record_dialog.py

#    Copyright (C) 2013 Christian Jacobs.

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

from gi.repository import Gtk, GObject
import logging
import ConfigParser
from datetime import datetime
from os.path import expanduser
import base64
try:
   import Hamlib
   have_hamlib = True
except ImportError:
   logging.error("Could not import the Hamlib module!")
   have_hamlib = False

from adif import AVAILABLE_FIELD_NAMES_FRIENDLY, AVAILABLE_FIELD_NAMES_ORDERED
from callsign_lookup import *
from auxiliary_dialogs import *

class RecordDialog(Gtk.Dialog):
   """ A dialog through which users can enter information about a QSO/record. """
   
   def __init__(self, parent, log, index=None):
      """ Set up the layout of the record dialog.
      If a record index is specified in the 'index' argument, then the dialog turns into 'edit record mode' and fills the data sources with the existing data in the log.
      If the 'index' argument is None, then the dialog starts off with nothing in the data sources (e.g. the Gtk.Entry boxes). """

      logging.debug("Setting up the record dialog...")
      
      if(index is not None):
         title = "Edit Record %d" % index
      else:
         title = "Add Record"
      Gtk.Dialog.__init__(self, title=title, parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      ## QSO DATA FRAME
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
      button.connect("clicked", self.lookup_callback) # Looks up the callsign on qrz.com for callsign and station information.
      button.set_tooltip_text("Lookup on qrz.com")
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
      bands = ["", "2190m", "560m", "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "4m", "2m", "1.25m", "70cm", "33cm", "23cm", "13cm", "9cm", "6cm", "3cm", "1.25cm", "6mm", "4mm", "2.5mm", "2mm", "1mm"]
      self.sources["BAND"] = Gtk.ComboBoxText()
      for band in bands:
         self.sources["BAND"].append_text(band)
      self.sources["BAND"].set_active(0) # Set an empty string as the default option.
      hbox_temp.pack_start(self.sources["BAND"], False, False, 2)
      vbox_inner.pack_start(hbox_temp, False, False, 2)

      # MODE
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["MODE"])
      label.set_alignment(0, 0.5)
      label.set_width_chars(15)
      hbox_temp.pack_start(label, False, False, 2)
      modes = ["", "AM", "AMTORFEC", "ASCI", "ATV", "CHIP64", "CHIP128", "CLO", "CONTESTI", "CW", "DSTAR", "DOMINO", "DOMINOF", "FAX", "FM", "FMHELL", "FSK31", "FSK441", "GTOR", "HELL", "HELL80", "HFSK", "ISCAT", "JT44", "JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G", "JT65", "JT65A", "JT65B", "JT65C", "JT6M", "MFSK8", "MFSK16", "MT63", "OLIVIA", "PAC", "PAC2", "PAC3", "PAX", "PAX2", "PCW", "PKT", "PSK10", "PSK31", "PSK63", "PSK63F", "PSK125", "PSKAM10", "PSKAM31", "PSKAM50", "PSKFEC31", "PSKHELL", "Q15", "QPSK31", "QPSK63", "QPSK125", "ROS", "RTTY", "RTTYM", "SSB", "SSTV", "THRB", "THOR", "THRBX", "TOR", "V4", "VOI", "WINMOR", "WSPR"]
      self.sources["MODE"] = Gtk.ComboBoxText()
      for mode in modes:
         self.sources["MODE"].append_text(mode)
      self.sources["MODE"].set_active(0) # Set an empty string as the default option.
      hbox_temp.pack_start(self.sources["MODE"], False, False, 2)
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
      self.sources["QSL_SENT"].set_active(0) # Set an empty string as the default option.
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
      self.sources["QSL_RCVD"].set_active(0) # Set an empty string as the default option.
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


      ## STATION INFORMATION FRAME
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

      # Check if a configuration file is present, since we might need it to set up the rest of the dialog.
      config = ConfigParser.ConfigParser()
      have_config = (config.read(expanduser('~/.pyqso.ini')) != [])

      if(index is not None):
         # The record already exists, so display its current data in the input boxes.
         record = log.get_record_by_index(index)
         field_names = AVAILABLE_FIELD_NAMES_ORDERED
         for i in range(0, len(field_names)):
            data = record[field_names[i].lower()]
            if(data is None):
               data = ""
            if(field_names[i] == "BAND"):
               self.sources[field_names[i]].set_active(bands.index(data))
            elif(field_names[i] == "MODE"):
               self.sources[field_names[i]].set_active(modes.index(data))
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
         dt = datetime.now()
         (year, month, day) = (dt.year, dt.month, dt.day)
         (hour, minute) = (dt.hour, dt.minute)
         # If necessary, add on leading zeros so the YYYYMMDD and HHMM format is followed.
         if(month < 10):
            month = "0" + str(month) # Note: Unlike the calendar widget, the months start from an index of 1 here.
         if(day < 10):
            day = "0" + str(day)
         if(hour < 10):
            hour = "0" + str(hour)
         if(minute < 10):
            minute = "0" + str(minute)
         date = str(year) + str(month) + str(day)
         time = str(hour) + str(minute)
         self.sources["QSO_DATE"].set_text(date)
         self.sources["TIME_ON"].set_text(time)

         if(have_hamlib):
            # If the Hamlib module is present, then use it to fill in the Frequency field if desired.
            if(have_config):
               autofill = (config.get("hamlib", "autofill") == "True")
               rig_model = config.get("hamlib", "rig_model")
               rig_pathname = config.get("hamlib", "rig_pathname")
               if(autofill):
                  # Use Hamlib (if available) to get the frequency
                  try:
                     Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_NONE)
                     rig = Hamlib.Rig(Hamlib.__dict__[rig_model]) # Look up the model's numerical index in Hamlib's symbol dictionary
                     rig.set_conf("rig_pathname", rig_pathname)
                     rig.open()
                     frequency = "%.6f" % (rig.get_freq()/1.0e6) # Converting to MHz here
                     self.sources["FREQ"].set_text(frequency)
                     rig.close()
                  except:
                     logging.error("Could not obtain Frequency data via Hamlib!")

      # Do we want PyQSO to autocomplete the Band field based on the Frequency field?
      if(have_config):
         autocomplete_band = (config.get("records", "autocomplete_band") == "True")
         if(autocomplete_band):
            self.sources["FREQ"].connect("changed", self._autocomplete_band)
      else:
         self.sources["FREQ"].connect("changed", self._autocomplete_band)

      self.show_all()

      logging.debug("Record dialog ready!")

      return

   def get_data(self, field_name):
      """ Return the data for a specified field (with name 'field_name') from the Gtk.Entry/Gtk.ComboBoxText/etc boxes in the record dialog. """
      logging.debug("Retrieving the data in field %s from the record dialog..." % field_name)
      if(field_name == "BAND" or field_name == "MODE" or field_name == "QSL_SENT" or field_name == "QSL_RCVD"):
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


   def _autocomplete_band(self, widget=None):
      """ If a value for the Frequency is entered, this function autocompletes the Band field (if desired). """

      frequency = self.sources["FREQ"].get_text()
      if((frequency == "") or (frequency is None)):
         self.sources["BAND"].set_active(0)
         return
      else:
         try:
            frequency = float(frequency)
         except ValueError:
            return

      speed_of_light = 3.0e8 # Units: m/s
      wave_length = speed_of_light/(frequency*1e6) # Here we convert the frequency in MHz to the frequency in Hz. The wave length is in metres.
      
      bands = [2190.0, 560.0, 160.0, 80.0, 60.0, 40.0, 30.0, 20.0, 17.0, 15.0, 12.0, 10.0, 6.0, 4.0, 2.0, 1.25, 0.7, 0.33, 0.23, 0.13, 0.09, 0.06, 0.03, 0.0125, 0.006, 0.004, 0.0025, 0.002, 0.001]

      # Find the band which is closest to the wave_length
      for i in range(0, len(bands)-1):
         if(abs(bands[i] - wave_length) < abs(bands[i+1] - wave_length)):
            band = bands[i]
            self.sources["BAND"].set_active(bands.index(band) + 1)
            break

      return


   def lookup_callback(self, widget=None):
      """ Get the callsign-related data from the qrz.com database and store it in the relevant Gtk.Entry boxes, but return None. """
      callsign_lookup = CallsignLookup(parent = self)

      config = ConfigParser.ConfigParser()
      have_config = (config.read(expanduser('~/.pyqso.ini')) != [])
      if(have_config):
         username = config.get("general", "qrz_username")
         password = base64.b64decode(config.get("general", "qrz_password"))
         if(username == "" or password == ""):
            details_given = False
         else:
            details_given = True
      else:
         details_given = False
      if(not details_given):
         error(parent=self, message="To perform a callsign lookup, please specify your qrz.com username and password in the Preferences.")
         return

      connected = callsign_lookup.connect(username, password)
      if(connected):
         fields_and_data = callsign_lookup.lookup(self.sources["CALL"].get_text())
         for field_name in fields_and_data.keys():
            self.sources[field_name].set_text(fields_and_data[field_name])
      return

   def calendar_callback(self, widget):
      """ Open up a calendar widget for easy QSO_DATE selection. Return None after the user destroys the dialog. """
      calendar = CalendarDialog(parent = self)
      response = calendar.run()
      if(response == Gtk.ResponseType.OK):
         date = calendar.get_date()
         self.sources["QSO_DATE"].set_text(date)
      calendar.destroy()
      return

class CalendarDialog(Gtk.Dialog):
   """ A simple dialog containing a Gtk.Calendar widget. Using this ensures the date is in the correct YYYYMMDD format required by ADIF. """ 
   
   def __init__(self, parent):
      logging.debug("Setting up a calendar dialog...")
      Gtk.Dialog.__init__(self, title="Select Date", parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
      self.calendar = Gtk.Calendar()
      self.vbox.add(self.calendar)
      self.show_all()
      logging.debug("Calendar dialog ready!")
      return

   def get_date(self):
      """ Return the date from the Gtk.Calendar widget in YYYYMMDD format. """      
      logging.debug("Retrieving the date from the calendar widget...")
      (year, month, day) = self.calendar.get_date()
      # If necessary, add on leading zeros so the YYYYMMDD format is followed.
      if(month + 1 < 10):
         month = "0" + str(month + 1) # Note: the months start from an index of 0 when retrieved from the calendar widget.
      else:
         month = month + 1
      if(day < 10):
         day = "0" + str(day)
      date = str(year) + str(month) + str(day)
      return date

