#!/usr/bin/env python3

#    Copyright (C) 2013 Christian T. Jacobs.

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

from gi.repository import Gtk
import logging
import configparser
import os.path
import base64
try:
   import Hamlib
   have_hamlib = True
except ImportError:
   logging.warning("Could not import the Hamlib module!")
   have_hamlib = False

from pyqso.adif import *

PREFERENCES_FILE = os.path.expanduser("~/.config/pyqso/preferences.ini")

class PreferencesDialog(Gtk.Dialog):
   """ A dialog to specify the PyQSO preferences. """

   def __init__(self, parent):
      """ Set up the various pages of the preferences dialog. """

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

      self.adif = ADIFPage()
      self.preferences.insert_page(self.adif, Gtk.Label("ADIF"), 2)
      
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
      adif_data = self.adif.get_data()

      config = configparser.ConfigParser()

      # General
      config.add_section("general")
      for key in list(general_data.keys()):
         config.set("general", key.lower(), str(general_data[key]))

      # View
      config.add_section("view")
      for key in list(view_data.keys()):
         config.set("view", key.lower(), str(view_data[key]))

      # ADIF
      config.add_section("adif")
      for key in list(adif_data.keys()):
         config.set("adif", key.lower(), str(adif_data[key]))
         
      # Hamlib
      config.add_section("hamlib")
      for key in list(hamlib_data.keys()):
         config.set("hamlib", key.lower(), str(hamlib_data[key]))
      
      # Records
      config.add_section("records")
      for key in list(records_data.keys()):
         config.set("records", key.lower(), str(records_data[key]))

      # Write the preferences to file.
      with open(os.path.expanduser(PREFERENCES_FILE), 'w') as f:
         config.write(f)

      return

class GeneralPage(Gtk.VBox):
   """ The section of the preferences dialog containing general preferences. """

   def __init__(self):
      logging.debug("Setting up the General page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
      # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
      config = configparser.ConfigParser()
      have_config = (config.read(PREFERENCES_FILE) != [])

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
   """ The section of the preferences dialog containing view-related preferences. """

   def __init__(self):
      logging.debug("Setting up the View page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      config = configparser.ConfigParser()
      have_config = (config.read(PREFERENCES_FILE) != [])

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
   """ The section of the preferences dialog containing Hamlib-related preferences. """

   def __init__(self):
      logging.debug("Setting up the Hamlib page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      config = configparser.ConfigParser()
      have_config = (config.read(PREFERENCES_FILE) != [])

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
   """ The section of the preferences dialog containing record-related preferences. """

   def __init__(self):
      logging.debug("Setting up the Records page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
      # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
      config = configparser.ConfigParser()
      have_config = (config.read(PREFERENCES_FILE) != [])

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
      for mode in sorted(MODES.keys()):
         self.sources["DEFAULT_MODE"].append_text(mode)
      (section, option) = ("records", "default_mode")
      if(have_config and config.has_option(section, option)):
         mode = config.get(section, option)
      else:
         mode = ""
      self.sources["DEFAULT_MODE"].set_active(sorted(MODES.keys()).index(mode))
      self.sources["DEFAULT_MODE"].connect("changed", self._on_mode_changed)
      hbox_temp.pack_start(self.sources["DEFAULT_MODE"], False, False, 2)
      vbox.pack_start(hbox_temp, False, False, 2)

      # Submode
      hbox_temp = Gtk.HBox()
      label = Gtk.Label("Submode: ")
      label.set_width_chars(17)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 2)
      
      self.sources["DEFAULT_SUBMODE"] = Gtk.ComboBoxText()
      for submode in MODES[mode]:
         self.sources["DEFAULT_SUBMODE"].append_text(submode)
      (section, option) = ("records", "default_submode")
      if(have_config and config.has_option(section, option)):
         submode = config.get(section, option)
      else:
         submode = ""
      self.sources["DEFAULT_SUBMODE"].set_active(MODES[mode].index(submode))
      hbox_temp.pack_start(self.sources["DEFAULT_SUBMODE"], False, False, 2)
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

      # Callsign database
      hbox_temp = Gtk.HBox()
      label = Gtk.Label("Database: ")
      label.set_width_chars(17)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 2)
      
      self.sources["CALLSIGN_DATABASE"] = Gtk.ComboBoxText()
      callsign_database = ["", "qrz.com", "hamqth.com"]
      for database in callsign_database:
         self.sources["CALLSIGN_DATABASE"].append_text(database)
      (section, option) = ("records", "callsign_database")
      if(have_config and config.has_option(section, option)):
         self.sources["CALLSIGN_DATABASE"].set_active(callsign_database.index(config.get(section, option)))
      else:
         self.sources["CALLSIGN_DATABASE"].set_active(callsign_database.index(""))
      hbox_temp.pack_start(self.sources["CALLSIGN_DATABASE"], False, False, 2)
      vbox.pack_start(hbox_temp, False, False, 2)
      
      # Login details
      subframe = Gtk.Frame()
      subframe.set_label("Login details")
      inner_vbox = Gtk.VBox()

      hbox = Gtk.HBox()
      label = Gtk.Label("Username: ")
      label.set_width_chars(9)
      label.set_alignment(0, 0.5)
      hbox.pack_start(label, False, False, 2)
      self.sources["CALLSIGN_DATABASE_USERNAME"] = Gtk.Entry()
      (section, option) = ("records", "callsign_database_username")
      if(have_config and config.has_option(section, option)):
         self.sources["CALLSIGN_DATABASE_USERNAME"].set_text(config.get(section, option))
      hbox.pack_start(self.sources["CALLSIGN_DATABASE_USERNAME"], False, False, 2)
      inner_vbox.pack_start(hbox, False, False, 2)

      hbox = Gtk.HBox()
      label = Gtk.Label("Password: ")
      label.set_width_chars(9)
      label.set_alignment(0, 0.5)
      hbox.pack_start(label, False, False, 2)
      self.sources["CALLSIGN_DATABASE_PASSWORD"] = Gtk.Entry()
      self.sources["CALLSIGN_DATABASE_PASSWORD"].set_visibility(False) # Mask the password with the "*" character.
      (section, option) = ("records", "callsign_database_password")
      if(have_config and config.has_option(section, option)):
         password = base64.b64decode(config.get(section, option)).decode("utf-8")
         self.sources["CALLSIGN_DATABASE_PASSWORD"].set_text(password)
      hbox.pack_start(self.sources["CALLSIGN_DATABASE_PASSWORD"], False, False, 2)
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
      data["DEFAULT_SUBMODE"] = self.sources["DEFAULT_SUBMODE"].get_active_text()
      data["DEFAULT_POWER"] = self.sources["DEFAULT_POWER"].get_text()
      
      data["CALLSIGN_DATABASE"] = self.sources["CALLSIGN_DATABASE"].get_active_text()
      data["CALLSIGN_DATABASE_USERNAME"] = self.sources["CALLSIGN_DATABASE_USERNAME"].get_text()
      data["CALLSIGN_DATABASE_PASSWORD"] = base64.b64encode(self.sources["CALLSIGN_DATABASE_PASSWORD"].get_text().encode("utf-8")).decode('utf-8') # Need to convert from bytes to str here.
      data["IGNORE_PREFIX_SUFFIX"] = self.sources["IGNORE_PREFIX_SUFFIX"].get_active()
      return data

   def _on_mode_changed(self, combo):
      """ If the MODE field has changed its value, then fill the SUBMODE field with all the available SUBMODE options for that new MODE. """
      self.sources["DEFAULT_SUBMODE"].get_model().clear()
      mode = combo.get_active_text()
      for submode in MODES[mode]:
         self.sources["DEFAULT_SUBMODE"].append_text(submode)
      return
      
class ADIFPage(Gtk.VBox):
   """ The section of the preferences dialog containing ADIF-related preferences. """
   
   def __init__(self):
      logging.debug("Setting up the ADIF page of the preferences dialog...")

      Gtk.VBox.__init__(self, spacing=2)

      # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
      # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
      config = configparser.ConfigParser()
      have_config = (config.read(PREFERENCES_FILE) != [])

      self.sources = {}

      # Import frame
      frame = Gtk.Frame()
      frame.set_label("Import")
      vbox = Gtk.VBox()
      self.sources["MERGE_COMMENT"] = Gtk.CheckButton("Merge any text in the COMMENT field with the NOTES field.")
      (section, option) = ("adif", "merge_comment")
      if(have_config and config.has_option(section, option)):
         self.sources["MERGE_COMMENT"].set_active(config.get(section, option) == "True")
      else:
         self.sources["MERGE_COMMENT"].set_active(False)
      vbox.pack_start(self.sources["MERGE_COMMENT"], False, False, 2)

      frame.add(vbox)
      self.pack_start(frame, False, False, 2)
      
      logging.debug("ADIF page of the preferences dialog ready!")
      return

   def get_data(self):
      logging.debug("Retrieving data from the ADIF page of the preferences dialog...")
      data = {}
      data["MERGE_COMMENT"] = self.sources["MERGE_COMMENT"].get_active()
      return data

