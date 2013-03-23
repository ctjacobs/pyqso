#!/usr/bin/env python
# File: data_entry_panel.py

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

class DataEntryPanel(Gtk.VBox):
   
   def __init__(self, parent, hbox):
      logging.debug("New DataEntryPanel instance created!")
      
      Gtk.VBox.__init__(self, spacing=2)

      self.source_call = Gtk.Entry()
      temp_hbox = Gtk.HBox(spacing=2)
      temp_hbox.pack_start(Gtk.Label("Call: "), False, False, 2)
      temp_hbox.pack_start(self.source_call, expand=True, fill=True, padding=2)
      self.pack_start(temp_hbox, False, False, 0)

      self.source_date = Gtk.Entry()
      temp_hbox = Gtk.HBox(spacing=2)
      temp_hbox.pack_start(Gtk.Label("Date: "), False, False, 2)
      temp_hbox.pack_start(self.source_date, expand=True, fill=True, padding=2)
      self.pack_start(temp_hbox, False, False, 0)

      self.source_freq = Gtk.Entry()
      temp_hbox = Gtk.HBox(spacing=6)
      temp_hbox.pack_start(Gtk.Label("Freq.: "), False, False, 2)
      temp_hbox.pack_start(self.source_freq, expand=True, fill=True, padding=2)
      self.pack_start(temp_hbox, False, False, 0)

      self.sources = {"CALL":self.source_call,
                      "DATE":self.source_date,
                      "FREQ":self.source_freq}

      self.store = Gtk.Button("Store Data")
      self.store.connect("clicked", parent.edit_record_callback)
      self.pack_start(self.store, expand=False, fill=True, padding=2)

      hbox.pack_start(self, False, False, 0)

      return



