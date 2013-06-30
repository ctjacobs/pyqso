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
import sys

class PreferencesDialog(Gtk.Dialog):
   
   def __init__(self, root_window):
      logging.debug("New PreferencesDialog instance created!")

      Gtk.Dialog.__init__(self, title="Preferences", parent=root_window, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      self.preferences = Gtk.Notebook()

      self.general = GeneralPage()
      self.preferences.insert_page(self.general, Gtk.Label("General"), 0)

      self.view = ViewPage()
      self.preferences.insert_page(self.view, Gtk.Label("View"), 1)

      self.vbox.pack_start(self.preferences, True, True, 2)
      self.show_all()

      return

   def commit(self):
      ''' Commits the user preferences to the configuration file. '''

      general_data = self.general.get_data()
      view_data = self.view.get_data()

      config = ConfigParser.ConfigParser()

      # General
      config.add_section("general")
      for key in general_data.keys():
         config.set("general", key.lower(), general_data[key])

      # View
      config.add_section("view")
      for key in view_data.keys():
         config.set("view", key.lower(), view_data[key])
      
      with open(os.path.expanduser('~/.pyqso.ini'), 'w') as f:
         config.write(f)

      return

class GeneralPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("New GeneralPage instance created!")

      Gtk.VBox.__init__(self, spacing=2)

      # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
      # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
      config = ConfigParser.ConfigParser()
      have_config = (config.read(os.path.expanduser('~/.pyqso.ini')) != [])

      self.sources = {}

      frame = Gtk.Frame()
      frame.set_label("Startup")
      hbox = Gtk.HBox()
      self.sources["SHOW_TOOLBOX"] = Gtk.CheckButton("Show toolbox by default")
      if(have_config):
         self.sources["SHOW_TOOLBOX"].set_active(config.get("general", "show_toolbox") == "True")
      else:
         self.sources["SHOW_TOOLBOX"].set_active(False)
      hbox.pack_start(self.sources["SHOW_TOOLBOX"], False, False, 2)
      frame.add(hbox)
      self.pack_start(frame, True, True, 2)

      frame = Gtk.Frame()
      frame.set_label("Login details (qrz.com)")
      inner_vbox = Gtk.VBox()

      hbox = Gtk.HBox()
      label = Gtk.Label("Username: ")
      label.set_width_chars(11)
      label.set_alignment(0, 0.5)
      hbox.pack_start(label, False, False, 2)
      self.sources["QRZ_USERNAME"] = Gtk.Entry()
      if(have_config):
         self.sources["QRZ_USERNAME"].set_text(config.get("general", "qrz_username"))
      hbox.pack_start(self.sources["QRZ_USERNAME"], False, False, 2)
      inner_vbox.pack_start(hbox, True, True, 2)

      hbox = Gtk.HBox()
      label = Gtk.Label("Password: ")
      label.set_width_chars(11)
      label.set_alignment(0, 0.5)
      hbox.pack_start(label, False, False, 2)
      self.sources["QRZ_PASSWORD"] = Gtk.Entry()
      self.sources["QRZ_PASSWORD"].set_visibility(False) # Mask the password with the "*" character.
      if(have_config):
         self.sources["QRZ_PASSWORD"].set_text(config.get("general", "qrz_password"))
      hbox.pack_start(self.sources["QRZ_PASSWORD"], False, False, 2)
      inner_vbox.pack_start(hbox, True, True, 2)

      frame.add(inner_vbox)
      self.pack_start(frame, True, True, 2)

      return

   def get_data(self):
      data = {}
      data["SHOW_TOOLBOX"] = self.sources["SHOW_TOOLBOX"].get_active()
      data["QRZ_USERNAME"] = self.sources["QRZ_USERNAME"].get_text()
      data["QRZ_PASSWORD"] = self.sources["QRZ_PASSWORD"].get_text()
      return data

class ViewPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("New ViewPage instance created!")

      Gtk.VBox.__init__(self, spacing=2)

      self.sources = {}

      self.label = Gtk.Label("Note: View-related changes will not take effect\nuntil PyQSO is restarted.")
      self.pack_start(self.label, True, True, 2)

      return

   def get_data(self):
      data = {}
      return data

