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

from adif import AVAILABLE_FIELD_NAMES_TYPES

class DataEntryPanel(Gtk.VBox):
   
   def __init__(self, parent, hbox_parent):
      logging.debug("New DataEntryPanel instance created!")
      
      Gtk.VBox.__init__(self, spacing=2)

      self.sources = {}

      field_names = parent.logbook.SELECTED_FIELD_NAMES_TYPES.keys()
      for i in range(0, len(field_names)):
         hbox_temp = Gtk.HBox(spacing=2)
         hbox_temp.pack_start(Gtk.Label(field_names[i]), False, False, 0)
         self.sources[field_names[i]] = Gtk.Entry()
         hbox_temp.pack_start(self.sources[field_names[i]], True, True, 0)
         self.pack_start(hbox_temp, False, False, 0)

      self.store = Gtk.Button("Store Data")
      self.store.connect("clicked", parent.edit_record_callback)
      self.pack_start(self.store, expand=False, fill=True, padding=2)

      hbox_parent.pack_start(self, False, False, 0)

      return

   def enable(self):
      # Activates all text boxes and the "Store data" button
      keys = self.sources.keys()
      for i in range(0, len(keys)):
         self.sources[keys[i]].set_property("editable", True)
         self.sources[keys[i]].set_can_focus(True)
      self.store.set_sensitive(True)

   def disable(self):
      # Deactivates all text boxes and the "Store data" button
      keys = self.sources.keys()
      for i in range(0, len(keys)):
         self.sources[keys[i]].set_property("editable", False)
         self.sources[keys[i]].set_can_focus(False)
      self.store.set_sensitive(False)

