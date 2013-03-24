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

class RecordDialog(Gtk.Dialog):
   
   def __init__(self, parent):
      logging.debug("New RecordDialog instance created!")
      
      Gtk.Dialog.__init__(self, title="Update Record")

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

      #hbox_parent.pack_start(self, False, False, 0)

      return

   def get_data(self, field_name):
      return self.sources[field_name].get_text()

   def set_data(self, field_name, data):
      if(data is None):
         self.sources[field_name].set_text("")
      else:
         self.sources[field_name].set_text(data)
      return


