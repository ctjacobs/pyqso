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

import ConfigParser
import os.path

class PreferencesDialog(Gtk.Dialog):
   
   def __init__(self, root_window):
      logging.debug("New PreferencesDialog instance created!")

      Gtk.Dialog.__init__(self, title="Preferences", parent=root_window, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      # Get any application-specific preferences from the configuration file
      config = ConfigParser.ConfigParser()
      have_config = (config.read(os.path.expanduser('~/.pyqso.cfg')) != [])

      self.preferences = Gtk.Notebook()

      self.general = GeneralPage()
      self.preferences.insert_page(self.general, Gtk.Label("General"), 0)

      self.view = Gtk.VBox()
      self.preferences.insert_page(self.view, Gtk.Label("View"), 1)

      self.vbox.pack_start(self.preferences, True, True, 2)
      self.show_all()

      return

   def commit(self):
      # Commit the changes to the preferences.
      return

class GeneralPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("New GeneralPage instance created!")

      Gtk.VBox.__init__(self, spacing=2)

      self.sources = {}

      frame = Gtk.Frame()
      frame.set_label("Startup")
      hbox = Gtk.HBox()
      self.sources["SHOW_TOOLBOX"] = Gtk.CheckButton("Show toolbox by default")
      self.sources["SHOW_TOOLBOX"].set_active(False)
      hbox.pack_start(self.sources["SHOW_TOOLBOX"], False, False, 2)
      frame.add(hbox)
      self.pack_start(frame, True, True, 2)

      frame = Gtk.Frame()
      frame.set_label("Callsign lookup (using qrz.com)")
      inner_vbox = Gtk.VBox()

      hbox = Gtk.HBox()
      hbox.pack_start(Gtk.Label("Username: "), False, False, 2)
      self.sources["QRZ_USERNAME"] = Gtk.Entry()
      hbox.pack_start(self.sources["QRZ_USERNAME"], False, False, 2)
      inner_vbox.pack_start(hbox, True, True, 2)

      hbox = Gtk.HBox()
      hbox.pack_start(Gtk.Label("Password: "), False, False, 2)
      self.sources["QRZ_PASSWORD"] = Gtk.Entry()
      hbox.pack_start(self.sources["QRZ_PASSWORD"], False, False, 2)
      inner_vbox.pack_start(hbox, True, True, 2)

      frame.add(inner_vbox)
      self.pack_start(frame, True, True, 2)

      return

class ViewPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("New ViewPage instance created!")

      Gtk.VBox.__init__(self, spacing=2)

      self.label = Gtk.Label("Hello")
      self.pack_start(self.label, True, True, 2)

      return

