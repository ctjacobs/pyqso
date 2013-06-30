#!/usr/bin/env python
# logbook: menu.py

#    Copyright (C) 2012 Christian Jacobs.

#    This logbook is part of PyQSO.

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

class Menu(Gtk.MenuBar):
   
   def __init__(self, parent):
      logging.debug("New Menu instance created!")
      
      # First let's call the constructor of the super class (Gtk.MenuBar)
      Gtk.MenuBar.__init__(self)
      
      agrp = Gtk.AccelGroup()
      parent.add_accel_group(agrp)

      self.items = {}
      
      ###### LOGBOOK ######
      mitem_logbook = Gtk.MenuItem("Logbook")
      self.append(mitem_logbook)  
      subm_logbook = Gtk.Menu()
      mitem_logbook.set_submenu(subm_logbook)
    
      # Connect
      mitem_connect = Gtk.ImageMenuItem("Connect to Logbook...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_CONNECT, Gtk.IconSize.MENU)
      mitem_connect.set_image(icon)
      mitem_connect.connect("activate", parent.logbook.db_connect)
      key, mod = Gtk.accelerator_parse("<Control>O")
      mitem_connect.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_connect)
      self.items["CONNECT"] = mitem_connect

      # Disconnect
      mitem_disconnect = Gtk.ImageMenuItem("Disconnect from Logbook")
      mitem_disconnect.connect("activate", parent.logbook.db_disconnect)
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_DISCONNECT, Gtk.IconSize.MENU)
      mitem_disconnect.set_image(icon)
      key, mod = Gtk.accelerator_parse("<Control>W")
      mitem_disconnect.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_disconnect)
      self.items["DISCONNECT"] = mitem_disconnect

      subm_logbook.append(Gtk.SeparatorMenuItem())

      # New log
      mitem_new = Gtk.ImageMenuItem("New Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
      mitem_new.set_image(icon)
      mitem_new.connect("activate", parent.logbook.new_log)
      subm_logbook.append(mitem_new)
      self.items["NEW_LOG"] = mitem_new

      # Delete the current log
      mitem_delete = Gtk.ImageMenuItem("Delete Selected Log")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
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
      
      
      ###### VIEW ######
      mitem_view = Gtk.MenuItem("View")
      self.append(mitem_view)  
      subm_view = Gtk.Menu()
      mitem_view.set_submenu(subm_view)

      mitem_toolbox = Gtk.CheckMenuItem("Toolbox")
      config = ConfigParser.ConfigParser()
      have_config = (config.read(os.path.expanduser('~/.pyqso.ini')) != [])
      if(have_config):
         mitem_toolbox.set_active(config.get("general", "show_toolbox") == "True")
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

      self.set_connect_item_sensitive(True)
      self.set_log_items_sensitive(False)
      self.set_record_items_sensitive(False)
      
      return
      
   def set_connect_item_sensitive(self, sensitive):
      self.items["CONNECT"].set_sensitive(sensitive)
      self.items["DISCONNECT"].set_sensitive(not sensitive)
      return

   def set_log_items_sensitive(self, sensitive):
      for item_name in ["NEW_LOG", "DELETE_LOG", "RENAME_LOG", "IMPORT_LOG", "EXPORT_LOG"]:
         self.items[item_name].set_sensitive(sensitive)
      return

   def set_record_items_sensitive(self, sensitive):
      for item_name in ["ADD_RECORD", "EDIT_RECORD", "DELETE_RECORD"]:
         self.items[item_name].set_sensitive(sensitive)
      return

