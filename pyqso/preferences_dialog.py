#!/usr/bin/env python
# File: preferences_dialog.py

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

class PreferencesDialog(Gtk.Dialog):
   
   def __init__(self, root_window):
      logging.debug("New PreferencesDialog instance created!")

      Gtk.Dialog.__init__(self, title="Preferences", parent=root_window, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      self.preferences = Gtk.Notebook()

      self.visible_columns = Gtk.VBox()
      self.preferences.insert_page(self.visible_columns, Gtk.Label("Visible Columns"), 0)

      self.vbox.pack_start(self.preferences, True, True, 0)
      self.show_all()

      return

   def commit(self):
      # Commit the changes to the preferences.
      return
