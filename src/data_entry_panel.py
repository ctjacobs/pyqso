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

      # Create label:entry pairs and store them in a dictionary
      self.sources = {}
      field_names = parent.logbook.SELECTED_FIELD_NAMES_TYPES.keys()
      for i in range(0, len(field_names)):
         hbox_temp = Gtk.HBox(spacing=2)
         hbox_temp.pack_start(Gtk.Label(field_names[i]), False, False, 0)
         self.sources[field_names[i]] = Gtk.Entry()
         hbox_temp.pack_start(self.sources[field_names[i]], True, True, 0)
         self.pack_start(hbox_temp, False, False, 0)

      self.update = Gtk.Button("Update Record")
      self.update.connect("clicked", parent.update_record_callback)
      self.pack_start(self.update, expand=False, fill=True, padding=2)

      hbox_parent.pack_start(self, False, False, 0)

      return

   def get_data(self, field_name):
      return self.sources[field_name].get_text()

   def set_data(self, field_name, data):
      if(data is None):
         self.sources[field_name].set_text("")
      else:
         self.sources[field_name].set_text(data)
      return

   def enable(self):
      # Activates all Entry widgets and the update button
      keys = self.sources.keys()
      for i in range(0, len(keys)):
         self.sources[keys[i]].set_property("editable", True)
         self.sources[keys[i]].set_can_focus(True)
      self.update.set_sensitive(True)

   def disable(self):
      # Deactivates all Entry widgets and the update button
      keys = self.sources.keys()
      for i in range(0, len(keys)):
         self.sources[keys[i]].set_property("editable", False)
         self.sources[keys[i]].set_can_focus(False)
      self.update.set_sensitive(False)

