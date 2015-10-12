#!/usr/bin/env python3

#    Copyright (C) 2012 Christian T. Jacobs.

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

class Menu(Gtk.MenuBar):
   """ The PyQSO menu bar along the top of the main window. """

   def __init__(self, parent):
      """ Set up all menu items and connect to the various functions. 
      
      :arg parent: The parent Gtk window.
      """

      logging.debug("New Menu instance created!")
      
      # First let's call the constructor of the super class (Gtk.MenuBar)
      Gtk.MenuBar.__init__(self)

      logging.debug("Setting up the menu bar...")      
      agrp = Gtk.AccelGroup()
      parent.add_accel_group(agrp)

      self.items = {}
      
      ###### LOGBOOK ######
      mitem_logbook = Gtk.MenuItem("Logbook")
      self.append(mitem_logbook)  
      subm_logbook = Gtk.Menu()
      mitem_logbook.set_submenu(subm_logbook)

      # Create logbook
      mitem_connect = Gtk.ImageMenuItem("Create a New Logbook...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_NEW, Gtk.IconSize.MENU)
      mitem_connect.set_image(icon)
      mitem_connect.connect("activate", parent.logbook.new)
      subm_logbook.append(mitem_connect)
      self.items["NEW_LOGBOOK"] = mitem_connect
          
      # Open logbook
      mitem_connect = Gtk.ImageMenuItem("Open an Existing Logbook...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.MENU)
      mitem_connect.set_image(icon)
      mitem_connect.connect("activate", parent.logbook.open)
      key, mod = Gtk.accelerator_parse("<Control>O")
      mitem_connect.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_connect)
      self.items["OPEN_LOGBOOK"] = mitem_connect

      # Close logbook
      mitem_disconnect = Gtk.ImageMenuItem("Close Logbook")
      mitem_disconnect.connect("activate", parent.logbook.close)
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
      mitem_disconnect.set_image(icon)
      key, mod = Gtk.accelerator_parse("<Control>W")
      mitem_disconnect.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_disconnect)
      self.items["CLOSE_LOGBOOK"] = mitem_disconnect

      subm_logbook.append(Gtk.SeparatorMenuItem())

      # New log
      mitem_new = Gtk.ImageMenuItem("New Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
      mitem_new.set_image(icon)
      mitem_new.connect("activate", parent.logbook.new_log)
      key, mod = Gtk.accelerator_parse("<Control>N")
      mitem_new.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_new)
      self.items["NEW_LOG"] = mitem_new

      # Delete the current log
      mitem_delete = Gtk.ImageMenuItem("Delete Selected Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.MENU)
      mitem_delete.set_image(icon)
      mitem_delete.connect("activate", parent.logbook.delete_log)
      subm_logbook.append(mitem_delete)
      self.items["DELETE_LOG"] = mitem_delete
      
      # Rename the current log
      mitem_rename = Gtk.ImageMenuItem("Rename Selected Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_EDIT, Gtk.IconSize.MENU)
      mitem_rename.set_image(icon)
      mitem_rename.connect("activate", parent.logbook.rename_log)
      subm_logbook.append(mitem_rename)
      self.items["RENAME_LOG"] = mitem_rename

      subm_logbook.append(Gtk.SeparatorMenuItem())

      # Import log
      mitem_import = Gtk.ImageMenuItem("Import Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_GO_FORWARD, Gtk.IconSize.MENU)
      mitem_import.set_image(icon)
      mitem_import.connect("activate", parent.logbook.import_log)
      subm_logbook.append(mitem_import)
      self.items["IMPORT_LOG"] = mitem_import

      # Export the current log
      mitem_export = Gtk.ImageMenuItem("Export Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_GO_BACK, Gtk.IconSize.MENU)
      mitem_export.set_image(icon)
      mitem_export.connect("activate", parent.logbook.export_log)
      subm_logbook.append(mitem_export)
      self.items["EXPORT_LOG"] = mitem_export
 
      subm_logbook.append(Gtk.SeparatorMenuItem())

      # Print log
      mitem_print = Gtk.ImageMenuItem("Print Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_PRINT, Gtk.IconSize.MENU)
      mitem_print.set_image(icon)
      mitem_print.connect("activate", parent.logbook.print_log)
      key, mod = Gtk.accelerator_parse("<Control>P")
      mitem_print.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_print)
      self.items["PRINT_LOG"] = mitem_print

      subm_logbook.append(Gtk.SeparatorMenuItem())

      # Quit
      mitem_quit = Gtk.ImageMenuItem("Quit")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_QUIT, Gtk.IconSize.MENU)
      mitem_quit.set_image(icon)
      mitem_quit.connect("activate", Gtk.main_quit)
      key, mod = Gtk.accelerator_parse("<Control>Q")
      mitem_quit.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_quit)
      self.items["QUIT"] = mitem_quit
      
      
      ###### RECORDS ######
      mitem_records = Gtk.MenuItem("Records")
      self.append(mitem_records)  
      subm_records = Gtk.Menu()
      mitem_records.set_submenu(subm_records)
      
      mitem_addrecord = Gtk.ImageMenuItem("Add Record...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
      mitem_addrecord.set_image(icon)
      mitem_addrecord.connect("activate", parent.logbook.add_record_callback)
      key, mod = Gtk.accelerator_parse("<Control>R")
      mitem_addrecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_records.append(mitem_addrecord)
      self.items["ADD_RECORD"] = mitem_addrecord
      
      mitem_editrecord = Gtk.ImageMenuItem("Edit Selected Record...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_EDIT, Gtk.IconSize.MENU)
      mitem_editrecord.set_image(icon)
      mitem_editrecord.connect("activate", parent.logbook.edit_record_callback, None, None)
      key, mod = Gtk.accelerator_parse("<Control>E")
      mitem_editrecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_records.append(mitem_editrecord)
      self.items["EDIT_RECORD"] = mitem_editrecord

      mitem_deleterecord = Gtk.ImageMenuItem("Delete Selected Record...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.MENU)
      mitem_deleterecord.set_image(icon)
      mitem_deleterecord.connect("activate", parent.logbook.delete_record_callback)
      key, mod = Gtk.accelerator_parse("Delete")
      mitem_deleterecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_records.append(mitem_deleterecord)
      self.items["DELETE_RECORD"] = mitem_deleterecord

      mitem_removeduplicates = Gtk.ImageMenuItem("Remove Duplicate Records")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_FIND_AND_REPLACE, Gtk.IconSize.MENU)
      mitem_removeduplicates.set_image(icon)
      mitem_removeduplicates.connect("activate", parent.logbook.remove_duplicates_callback)
      subm_records.append(mitem_removeduplicates)
      self.items["REMOVE_DUPLICATES"] = mitem_removeduplicates
      
      
      ###### VIEW ######
      mitem_view = Gtk.MenuItem("View")
      self.append(mitem_view)  
      subm_view = Gtk.Menu()
      mitem_view.set_submenu(subm_view)

      mitem_toolbox = Gtk.CheckMenuItem("Toolbox")
      config = configparser.ConfigParser()
      have_config = (config.read(os.path.expanduser('~/.pyqso.ini')) != [])
      (section, option) = ("general", "show_toolbox")
      if(have_config and config.has_option(section, option)):
         mitem_toolbox.set_active(config.get(section, option) == "True")
      else:
         mitem_toolbox.set_active(False) # Don't show the toolbox by default
      mitem_toolbox.connect("activate", parent.toolbox.toggle_visible_callback)
      subm_view.append(mitem_toolbox)
      self.items["TOOLBOX"] = mitem_toolbox

      mitem_preferences = Gtk.ImageMenuItem("Preferences...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_PREFERENCES, Gtk.IconSize.MENU)
      mitem_preferences.set_image(icon)
      mitem_preferences.connect("activate", parent.show_preferences)
      subm_view.append(mitem_preferences)
      self.items["PREFERENCES"] = mitem_preferences
            

      ###### HELP ######
      mitem_help = Gtk.MenuItem("Help")
      self.append(mitem_help)  
      subm_help = Gtk.Menu()
      mitem_help.set_submenu(subm_help)
      
      # About
      mitem_about = Gtk.ImageMenuItem("About PyQSO")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_ABOUT, Gtk.IconSize.MENU)
      mitem_about.set_image(icon)
      mitem_about.connect("activate", parent.show_about)
      subm_help.append(mitem_about)

      self.set_logbook_item_sensitive(True)
      self.set_log_items_sensitive(False)
      self.set_record_items_sensitive(False)
      
      logging.debug("Menu bar ready!") 

      return
      
   def set_logbook_item_sensitive(self, sensitive):
      """ Enable/disable logbook-related menu items.
      
      :arg bool sensitive: If True, enable the 'new logbook' and 'open logbook' menu items. If False, disable them.
      """
      logging.debug("Setting the 'Create/Open Logbook' menu item's sensitivity to: %s..." % sensitive) 
      self.items["NEW_LOGBOOK"].set_sensitive(sensitive)
      self.items["OPEN_LOGBOOK"].set_sensitive(sensitive)
      self.items["CLOSE_LOGBOOK"].set_sensitive(not sensitive)
      logging.debug("Set the 'Create/Open Logbook' menu item's sensitivity to: %s." % sensitive) 
      return

   def set_log_items_sensitive(self, sensitive):
      """ Enable/disable log-related menu items.
      
      :arg bool sensitive: If True, enable all the log-related menu items. If False, disable them all.
      """
      logging.debug("Setting log-related menu item sensitivity to: %s..." % sensitive) 
      for item_name in ["NEW_LOG", "DELETE_LOG", "RENAME_LOG", "IMPORT_LOG", "EXPORT_LOG", "PRINT_LOG"]:
         self.items[item_name].set_sensitive(sensitive)
      logging.debug("Set log-related menu item sensitivity to: %s." % sensitive) 
      return

   def set_record_items_sensitive(self, sensitive):
      """ Enable/disable record-related menu items.
      
      :arg bool sensitive: If True, enable all the record-related menu items. If False, disable them all.
      """
      logging.debug("Setting record-related menu item sensitivity to: %s..." % sensitive) 
      for item_name in ["ADD_RECORD", "EDIT_RECORD", "DELETE_RECORD", "REMOVE_DUPLICATES"]:
         self.items[item_name].set_sensitive(sensitive)
      logging.debug("Set record-related menu item sensitivity to: %s." % sensitive) 
      return

