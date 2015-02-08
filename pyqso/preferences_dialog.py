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
import base64
from math import ceil
try:
   import Hamlib
   have_hamlib = True
except ImportError:
   logging.error("Could not import the Hamlib module!")
   have_hamlib = False

from pyqso.adif import AVAILABLE_FIELD_NAMES_FRIENDLY, AVAILABLE_FIELD_NAMES_ORDERED, MODES

class PreferencesDialog(Gtk.Dialog):
   
   def __init__(self, parent):
      logging.debug("Setting up the preferences dialog...")

      Gtk.Dialog.__init__(self, title="Preferences", parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      self.preferences = Gtk.Notebook()

      self.general = GeneralPage()
      self.preferences.insert_page(self.general, Gtk.Label("General"), 0)

      self.view = ViewPage()
      self.preferences.insert_page(self.view, Gtk.Label("View"), 1)

      self.hamlib = HamlibPage()
      self.preferences.insert_page(self.hamlib, Gtk.Label("Hamlib"), 2)

      self.records = RecordsPage()
      self.preferences.insert_page(self.records, Gtk.Label("Records"), 2)

      self.vbox.pack_start(self.preferences, True, True, 2)
      self.show_all()

      logging.debug("Preferences dialog ready!")

      return

   def commit(self):
      """ Commit the user preferences to the configuration file. """
      logging.debug("Committing the user preferences to the configuration file...")
      general_data = self.general.get_data()
      view_data = self.view.get_data()
      hamlib_data = self.hamlib.get_data()
      records_data = self.records.get_data()

      config = ConfigParser.ConfigParser()

      # General
      config.add_section("general")
      for key in general_data.keys():
         config.set("general", key.lower(), general_data[key])

      # View
      config.add_section("view")
      for key in view_data.keys():
         config.set("view", key.lower(), view_data[key])

      # Hamlib
      config.add_section("hamlib")
      for key in hamlib_data.keys():
         config.set("hamlib", key.lower(), hamlib_data[key])
      
      # Records
      config.add_section("records")
      for key in records_data.keys():
         config.set("records", key.lower(), records_data[key])

      with open(os.path.expanduser('~/.pyqso.ini'), 'w') as f:
         config.write(f)

      return

class GeneralPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("Setting up the General page of the preferences dialog...")

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
      (section, option) = ("general", "show_toolbox")
      if(have_config and config.has_option(section, option)):
         self.sources["SHOW_TOOLBOX"].set_active(config.get(section, option) == "True")
      else:
         self.sources["SHOW_TOOLBOX"].set_active(False)
      hbox.pack_start(self.sources["SHOW_TOOLBOX"], False, False, 2)
      frame.add(hbox)
      self.pack_start(frame, False, False, 2)

      logging.debug("General page of the preferences dialog ready!")
      return

   def get_data(self):
      logging.debug("Retrieving data from the General page of the preferences dialog...")
      data = {}
      data["SHOW_TOOLBOX"] = self.sources["SHOW_TOOLBOX"].get_active()
      return data

class ViewPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("Setting up the View page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      config = ConfigParser.ConfigParser()
      have_config = (config.read(os.path.expanduser('~/.pyqso.ini')) != [])

      self.sources = {}

      # Visible fields frame
      frame = Gtk.Frame()
      frame.set_label("Visible fields")

      # Divide the list of available field names up into multiple columns (of maximum length 'max_buttons_per_column')
      # so we don't make the Preferences dialog too long.      
      hbox = Gtk.HBox(spacing=2)
      max_buttons_per_column = 6
      number_of_columns = int( len(AVAILABLE_FIELD_NAMES_ORDERED)/max_buttons_per_column ) + 1 # Number of check buttons per column
      for i in range(0, number_of_columns):
         vbox = Gtk.VBox(spacing=2)
         for j in range(0, max_buttons_per_column):
            if(i*max_buttons_per_column + j >= len(AVAILABLE_FIELD_NAMES_ORDERED)):
               break
            field_name = AVAILABLE_FIELD_NAMES_ORDERED[i*max_buttons_per_column + j]
            button = Gtk.CheckButton(AVAILABLE_FIELD_NAMES_FRIENDLY[field_name ])
            if(have_config and config.has_option("view", field_name.lower())):
               button.set_active(config.get("view", field_name.lower()) == "True")
            else:
               button.set_active(True)
            self.sources[field_name] = button
            vbox.pack_start(button, False, False, 2)
         hbox.pack_start(vbox, False, False, 2)
      frame.add(hbox)
      self.pack_start(frame, False, False, 2)

      self.label = Gtk.Label("Note: View-related changes will not take effect\nuntil PyQSO is restarted.")
      self.pack_start(self.label, False, False, 2)

      logging.debug("View page of the preferences dialog ready!")
      return

   def get_data(self):
      logging.debug("Retrieving data from the View page of the preferences dialog...")
      data = {}
      for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
         data[field_name] = self.sources[field_name].get_active()
      return data

class HamlibPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("Setting up the Hamlib page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      config = ConfigParser.ConfigParser()
      have_config = (config.read(os.path.expanduser('~/.pyqso.ini')) != [])

      self.sources = {}

      frame = Gtk.Frame()
      frame.set_label("Hamlib support")

      vbox_inner = Gtk.VBox(spacing=2)

      self.sources["AUTOFILL"] = Gtk.CheckButton("Auto-fill Frequency field")
      (section, option) = ("hamlib", "autofill")
      if(have_config and config.has_option(section, option)):
         self.sources["AUTOFILL"].set_active(config.get(section, option) == "True")
      else:
         self.sources["AUTOFILL"].set_active(False)
      vbox_inner.pack_start(self.sources["AUTOFILL"], False, False, 2)

      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label("Model: ")
      label.set_alignment(0, 0.5)
      label.set_width_chars(17)
      hbox_temp.pack_start(label, False, False, 2)

      # Get the list of rig models
      models = ["RIG_MODEL_NONE"]
      if(have_hamlib):
         try:
            for item in dir(Hamlib):
               if(item.startswith("RIG_MODEL_")):
                  models.append(item)
         except:
            logging.error("Could not obtain rig models list via Hamlib!")
      else:
         logging.debug("Hamlib module not present. Could not obtain a list of rig models.")

      self.sources["RIG_MODEL"] = Gtk.ComboBoxText()
      for model in models:
         self.sources["RIG_MODEL"].append_text(model)
      (section, option) = ("hamlib", "rig_model")
      if(have_config and config.has_option("hamlib", "rig_model")):
         self.sources["RIG_MODEL"].set_active(models.index(config.get("hamlib", "rig_model")))
      else:
         self.sources["RIG_MODEL"].set_active(models.index("RIG_MODEL_NONE")) # Set to RIG_MODEL_NONE as the default option.
      hbox_temp.pack_start(self.sources["RIG_MODEL"], True, True, 2)
      vbox_inner.pack_start(hbox_temp, False, False, 2)

      # Path to rig
      hbox_temp = Gtk.HBox()
      label = Gtk.Label("Path to radio device: ")
      label.set_width_chars(17)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 2)
      self.sources["RIG_PATHNAME"] = Gtk.Entry()
      (section, option) = ("hamlib", "rig_pathname")
      if(have_config and config.has_option(section, option)):
         self.sources["RIG_PATHNAME"].set_text(config.get(section, option))
      hbox_temp.pack_start(self.sources["RIG_PATHNAME"], True, True, 2)
      vbox_inner.pack_start(hbox_temp, False, False, 2)

      frame.add(vbox_inner)
      self.pack_start(frame, True, True, 2)

      logging.debug("Hamlib page of the preferences dialog ready!")
      return

   def get_data(self):
      logging.debug("Retrieving data from the Hamlib page of the preferences dialog...")
      data = {}
      data["AUTOFILL"] = self.sources["AUTOFILL"].get_active()
      data["RIG_PATHNAME"] = self.sources["RIG_PATHNAME"].get_text()
      data["RIG_MODEL"] = self.sources["RIG_MODEL"].get_active_text()
      return data

class RecordsPage(Gtk.VBox):
   
   def __init__(self):
      logging.debug("Setting up the Records page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
      # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
      config = ConfigParser.ConfigParser()
      have_config = (config.read(os.path.expanduser('~/.pyqso.ini')) != [])

      self.sources = {}

      # Autocomplete frame
      frame = Gtk.Frame()
      frame.set_label("Autocomplete")
      vbox = Gtk.VBox()
      self.sources["AUTOCOMPLETE_BAND"] = Gtk.CheckButton("Autocomplete the Band field")
      (section, option) = ("records", "autocomplete_band")
      if(have_config and config.has_option(section, option)):
         self.sources["AUTOCOMPLETE_BAND"].set_active(config.get(section, option) == "True")
      else:
         self.sources["AUTOCOMPLETE_BAND"].set_active(True)
      vbox.pack_start(self.sources["AUTOCOMPLETE_BAND"], False, False, 2)

      self.sources["USE_UTC"] = Gtk.CheckButton("Use UTC when autocompleting the Date and Time")
      (section, option) = ("records", "use_utc")
      if(have_config and config.has_option(section, option)):
         self.sources["USE_UTC"].set_active(config.get(section, option) == "True")
      else:
         self.sources["USE_UTC"].set_active(True)
      vbox.pack_start(self.sources["USE_UTC"], False, False, 2)

      frame.add(vbox)
      self.pack_start(frame, False, False, 2)


      ## Default values frame
      frame = Gtk.Frame()
      frame.set_label("Default values")
      vbox = Gtk.VBox()
      
      # Mode
      hbox_temp = Gtk.HBox()
      label = Gtk.Label("Mode: ")
      label.set_width_chars(17)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 2)
      
      self.sources["DEFAULT_MODE"] = Gtk.ComboBoxText()
      for mode in MODES:
         self.sources["DEFAULT_MODE"].append_text(mode)
      (section, option) = ("records", "default_mode")
      if(have_config and config.has_option(section, option)):
         self.sources["DEFAULT_MODE"].set_active(MODES.index(config.get(section, option)))
      else:
         self.sources["DEFAULT_MODE"].set_active(MODES.index(""))
      hbox_temp.pack_start(self.sources["DEFAULT_MODE"], False, False, 2)
      vbox.pack_start(hbox_temp, False, False, 2)

      # Power
      hbox_temp = Gtk.HBox()
      label = Gtk.Label("TX Power (W): ")
      label.set_width_chars(17)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 2)
      
      self.sources["DEFAULT_POWER"] = Gtk.Entry()
      (section, option) = ("records", "default_power")
      if(have_config and config.has_option(section, option)):
         self.sources["DEFAULT_POWER"].set_text(config.get(section, option))
      else:
         self.sources["DEFAULT_POWER"].set_text("")
      hbox_temp.pack_start(self.sources["DEFAULT_POWER"], False, False, 2)
      vbox.pack_start(hbox_temp, False, False, 2)
      
      frame.add(vbox)
      self.pack_start(frame, False, False, 2)
      
      
      # Callsign lookup frame
      frame = Gtk.Frame()
      frame.set_label("Callsign lookup")
      vbox = Gtk.VBox()

      subframe = Gtk.Frame()
      subframe.set_label("Login details (qrz.com)")
      inner_vbox = Gtk.VBox()

      hbox = Gtk.HBox()
      label = Gtk.Label("Username: ")
      label.set_width_chars(9)
      label.set_alignment(0, 0.5)
      hbox.pack_start(label, False, False, 2)
      self.sources["QRZ_USERNAME"] = Gtk.Entry()
      (section, option) = ("records", "qrz_username")
      if(have_config and config.has_option(section, option)):
         self.sources["QRZ_USERNAME"].set_text(config.get(section, option))
      hbox.pack_start(self.sources["QRZ_USERNAME"], False, False, 2)
      inner_vbox.pack_start(hbox, False, False, 2)

      hbox = Gtk.HBox()
      label = Gtk.Label("Password: ")
      label.set_width_chars(9)
      label.set_alignment(0, 0.5)
      hbox.pack_start(label, False, False, 2)
      self.sources["QRZ_PASSWORD"] = Gtk.Entry()
      self.sources["QRZ_PASSWORD"].set_visibility(False) # Mask the password with the "*" character.
      (section, option) = ("records", "qrz_password")
      if(have_config and config.has_option(section, option)):
         self.sources["QRZ_PASSWORD"].set_text(base64.b64decode(config.get(section, option)))
      hbox.pack_start(self.sources["QRZ_PASSWORD"], False, False, 2)
      inner_vbox.pack_start(hbox, False, False, 2)

      label = Gtk.Label("Warning: Login details are currently stored as\nBase64-encoded plain text in the configuration file.")
      inner_vbox.pack_start(label, False, False, 2)

      subframe.add(inner_vbox)
      vbox.pack_start(subframe, False, False, 2)

      self.sources["IGNORE_PREFIX_SUFFIX"] = Gtk.CheckButton("Ignore callsign prefixes and/or suffixes")
      (section, option) = ("records", "ignore_prefix_suffix")
      if(have_config and config.has_option(section, option)):
         self.sources["IGNORE_PREFIX_SUFFIX"].set_active(config.get(section, option) == "True")
      else:
         self.sources["IGNORE_PREFIX_SUFFIX"].set_active(True)
      vbox.pack_start(self.sources["IGNORE_PREFIX_SUFFIX"], False, False, 2)
      
      frame.add(vbox)
      self.pack_start(frame, False, False, 2)
      
      logging.debug("Records page of the preferences dialog ready!")
      return

   def get_data(self):
      logging.debug("Retrieving data from the Records page of the preferences dialog...")
      data = {}
      data["AUTOCOMPLETE_BAND"] = self.sources["AUTOCOMPLETE_BAND"].get_active()
      data["USE_UTC"] = self.sources["USE_UTC"].get_active()
      
      data["DEFAULT_MODE"] = self.sources["DEFAULT_MODE"].get_active_text()
      data["DEFAULT_POWER"] = self.sources["DEFAULT_POWER"].get_text()
      
      data["QRZ_USERNAME"] = self.sources["QRZ_USERNAME"].get_text()
      data["QRZ_PASSWORD"] = base64.b64encode(self.sources["QRZ_PASSWORD"].get_text())
      data["IGNORE_PREFIX_SUFFIX"] = self.sources["IGNORE_PREFIX_SUFFIX"].get_active()
      return data

