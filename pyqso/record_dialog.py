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

from adif import AVAILABLE_FIELD_NAMES_FRIENDLY, AVAILABLE_FIELD_NAMES_ORDERED
from callsign_lookup import *

class RecordDialog(Gtk.Dialog):
   
   def __init__(self, root_window, log, index=None):
      logging.debug("New RecordDialog instance created!")
      
      if(index is not None):
         title = "Edit Record %d" % index
      else:
         title = "Add Record"
      Gtk.Dialog.__init__(self, title=title, parent=root_window, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      frame = Gtk.Frame()
      label = Gtk.Label("QSO Data")
      frame.set_label_widget(label)
      self.vbox.add(frame)
      vbox_inner = Gtk.VBox(spacing=2)

      # Create label:entry pairs and store them in a dictionary
      self.sources = {}

      # CALL
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["CALL"], halign=Gtk.Align.START)
      label.set_width_chars(11)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["CALL"] = Gtk.Entry()
      self.sources["CALL"].set_width_chars(15)
      hbox_temp.pack_start(self.sources["CALL"], False, False, 6)
      lookup = Gtk.Button("Lookup") # Looks up the callsign on qrz.com for more details.
      lookup.connect("clicked", self.lookup_callback)
      hbox_temp.pack_start(lookup, True, True, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      # DATE
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["QSO_DATE"], halign=Gtk.Align.START)
      label.set_width_chars(11)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["QSO_DATE"] = Gtk.Entry()
      self.sources["QSO_DATE"].set_width_chars(15)
      hbox_temp.pack_start(self.sources["QSO_DATE"], False, False, 6)

      # TIME
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["TIME_ON"], halign=Gtk.Align.START)
      label.set_alignment(0, 0.5)
      label.set_width_chars(11)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["TIME_ON"] = Gtk.Entry()
      self.sources["TIME_ON"].set_width_chars(15)
      hbox_temp.pack_start(self.sources["TIME_ON"], False, False, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      # FREQ
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["FREQ"], halign=Gtk.Align.START)
      label.set_alignment(0, 0.5)
      label.set_width_chars(11)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["FREQ"] = Gtk.Entry()
      self.sources["FREQ"].set_width_chars(15)
      hbox_temp.pack_start(self.sources["FREQ"], False, False, 6)

      # BAND
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["BAND"], halign=Gtk.Align.START)
      label.set_alignment(0, 0.5)
      label.set_width_chars(11)
      hbox_temp.pack_start(label, False, False, 6)
      bands = ["", "2190m", "560m", "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "4m", "2m", "1.25m", "70cm", "33cm", "23cm", "13cm", "9cm", "6cm", "3cm", "1.25cm", "6mm", "4mm", "2.5mm", "2mm", "1mm"]
      self.sources["BAND"] = Gtk.ComboBoxText()
      for band in bands:
         self.sources["BAND"].append_text(band)
      self.sources["BAND"].set_active(0) # Set an empty string as the default option.
      hbox_temp.pack_start(self.sources["BAND"], False, False, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      # MODE
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["MODE"])
      label.set_alignment(0, 0.5)
      label.set_width_chars(11)
      hbox_temp.pack_start(label, False, False, 6)
      modes = ["", "AM", "AMTORFEC", "ASCI", "ATV", "CHIP64", "CHIP128", "CLO", "CONTESTI", "CW", "DSTAR", "DOMINO", "DOMINOF", "FAX", "FM", "FMHELL", "FSK31", "FSK441", "GTOR", "HELL", "HELL80", "HFSK", "ISCAT", "JT44", "JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G", "JT65", "JT65A", "JT65B", "JT65C", "JT6M", "MFSK8", "MFSK16", "MT63", "OLIVIA", "PAC", "PAC2", "PAC3", "PAX", "PAX2", "PCW", "PKT", "PSK10", "PSK31", "PSK63", "PSK63F", "PSK125", "PSKAM10", "PSKAM31", "PSKAM50", "PSKFEC31", "PSKHELL", "Q15", "QPSK31", "QPSK63", "QPSK125", "ROS", "RTTY", "RTTYM", "SSB", "SSTV", "THRB", "THOR", "THRBX", "TOR", "V4", "VOI", "WINMOR", "WSPR"]
      self.sources["MODE"] = Gtk.ComboBoxText()
      for mode in modes:
         self.sources["MODE"].append_text(mode)
      self.sources["MODE"].set_active(0) # Set an empty string as the default option.
      hbox_temp.pack_start(self.sources["MODE"], False, False, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      # RST_SENT
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["RST_SENT"])
      label.set_alignment(0, 0.5)
      label.set_width_chars(11)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["RST_SENT"] = Gtk.Entry()
      self.sources["RST_SENT"].set_width_chars(15)
      hbox_temp.pack_start(self.sources["RST_SENT"], False, False, 6)

      # RST_RCVD
      label = Gtk.Label(AVAILABLE_FIELD_NAMES_FRIENDLY["RST_RCVD"])
      label.set_alignment(0, 0.5)
      label.set_width_chars(11)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["RST_RCVD"] = Gtk.Entry()
      self.sources["RST_RCVD"].set_width_chars(15)
      hbox_temp.pack_start(self.sources["RST_RCVD"], True, True, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      if(index is not None):
         # The record already exists, so display its current data in the input boxes.
         record = log.get_record_by_index(index)
         field_names = AVAILABLE_FIELD_NAMES_ORDERED
         for i in range(0, len(field_names)):
            if(field_names[i] == "BAND"):
               self.sources[field_names[i]].set_active(bands.index(record[field_names[i].lower()]))
            elif(field_names[i] == "MODE"):
               self.sources[field_names[i]].set_active(modes.index(record[field_names[i].lower()]))
            else:
               self.sources[field_names[i]].set_text(record[field_names[i].lower()])

      frame.add(vbox_inner)

      self.show_all()

      return

   def get_data(self, field_name):
      if(field_name == "BAND" or field_name == "MODE"):
         return self.sources[field_name].get_active_text()
      else:
         return self.sources[field_name].get_text()

   def lookup_callback(self, widget):
      # TODO: If a session doesn't already exist: Show a username and password dialog, and initiate a session.
      # Get the callsign-related data from the qrz.com database.
      print "Callsign lookup feature has not yet been implemented."
      return

