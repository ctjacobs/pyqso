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
   
   def __init__(self, parent, index=None):
      logging.debug("New RecordDialog instance created!")
      
      Gtk.Dialog.__init__(self, title="Add/Edit Record", parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      frame = Gtk.Frame()
      label = Gtk.Label("QSO Data")
      frame.set_label_widget(label)
      self.vbox.add(frame)

      # Create label:entry pairs and store them in a dictionary
      self.sources = {}
      field_names = parent.logbook.SELECTED_FIELD_NAMES_TYPES.keys()
      vbox_inner = Gtk.VBox(spacing=2)
      for i in range(0, len(field_names)):
         vbox_temp = Gtk.VBox(spacing=0)
         label = Gtk.Label(field_names[i])
         label.set_alignment(0, 0.5)
         vbox_temp.pack_start(label, False, False, 0)
         self.sources[field_names[i]] = Gtk.Entry()

         if(index is not None):
            record = parent.logbook.get_record(index)
            self.sources[field_names[i]].set_text(record.get_data(field_names[i]))

         vbox_temp.pack_start(self.sources[field_names[i]], True, True, 0)
         vbox_inner.pack_start(vbox_temp, False, False, 0)
      frame.add(vbox_inner)

      self.show_all()

      return

   def get_data(self, field_name):
      return self.sources[field_name].get_text()

   def set_data(self, field_name, data):
      if(data is None):
         self.sources[field_name].set_text("")
      else:
         self.sources[field_name].set_text(data)
      return


