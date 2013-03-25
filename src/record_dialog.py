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

from adif import AVAILABLE_FIELD_NAMES_TYPES
from callsign_lookup import *

class RecordDialog(Gtk.Dialog):
   
   def __init__(self, parent, index=None):
      logging.debug("New RecordDialog instance created!")
      
      if(index is not None):
         title = "Edit Record %d" % index
      else:
         title = "Add Record"
      Gtk.Dialog.__init__(self, title=title, parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      frame = Gtk.Frame()
      label = Gtk.Label("QSO Data")
      frame.set_label_widget(label)
      self.vbox.add(frame)
      vbox_inner = Gtk.VBox(spacing=2)

      # Create label:entry pairs and store them in a dictionary
      self.sources = {}

      # CALL
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(parent.logbook.SELECTED_FIELD_NAMES_FRIENDLY["CALL"])
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["CALL"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["CALL"], True, True, 6)
      lookup = Gtk.Button("Lookup") # Looks up the callsign on qrz.com for more details.
      lookup.connect("clicked", self.lookup_callback)
      hbox_temp.pack_start(lookup, True, True, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      # DATE
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(parent.logbook.SELECTED_FIELD_NAMES_FRIENDLY["DATE"])
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["DATE"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["DATE"], True, True, 6)

      # TIME
      label = Gtk.Label(parent.logbook.SELECTED_FIELD_NAMES_FRIENDLY["TIME"])
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["TIME"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["TIME"], True, True, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      # FREQ
      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label(parent.logbook.SELECTED_FIELD_NAMES_FRIENDLY["FREQ"])
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["FREQ"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["FREQ"], True, True, 6)

      # MODE
      label = Gtk.Label(parent.logbook.SELECTED_FIELD_NAMES_FRIENDLY["MODE"])
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["MODE"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["MODE"], True, True, 6)
      vbox_inner.pack_start(hbox_temp, False, False, 6)

      if(index is not None):
         # The record already exists, so display its current data in the input boxes.
         record = parent.logbook.get_record(index)
         field_names = parent.logbook.SELECTED_FIELD_NAMES_ORDERED
         for i in range(0, len(field_names)):
            self.sources[field_names[i]].set_text(record.get_data(field_names[i]))

      frame.add(vbox_inner)

      self.show_all()

      return

   def get_data(self, field_name):
      return self.sources[field_name].get_text()

   def is_valid(self, field_name, data):
      if(field_name == "FREQ"):
         return True

      else:
         return True

   def lookup_callback(self, widget):
      # TODO: If a session doesn't already exist: Show a username and password dialog, and initiate a session.
      # Get the callsign-related data from the qrz.com database.
      return

