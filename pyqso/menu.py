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
      mitem_connect = Gtk.MenuItem("Connect to Logbook...")
      mitem_connect.connect("activate", parent.logbook.db_connect)
      key, mod = Gtk.accelerator_parse("<Control>O")
      mitem_connect.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_connect)
      self.items["CONNECT"] = mitem_connect

      # Disconnect
      mitem_disconnect = Gtk.MenuItem("Disconnect from Logbook")
      mitem_disconnect.connect("activate", parent.logbook.db_disconnect)
      key, mod = Gtk.accelerator_parse("<Control>W")
      mitem_disconnect.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_logbook.append(mitem_disconnect)
      self.items["DISCONNECT"] = mitem_disconnect

      subm_logbook.append(Gtk.SeparatorMenuItem())

      # New log
      mitem_new = Gtk.MenuItem("New Log")
      mitem_new.connect("activate", parent.logbook.new_log)
      subm_logbook.append(mitem_new)
      self.items["NEW_LOG"] = mitem_new

      # Delete the current log
      mitem_delete = Gtk.MenuItem("Delete Log")
      mitem_delete.connect("activate", parent.logbook.delete_log)
      subm_logbook.append(mitem_delete)
      self.items["DELETE_LOG"] = mitem_delete

      subm_logbook.append(Gtk.SeparatorMenuItem())

      # Import log
      mitem_import = Gtk.MenuItem("Import Log")
      mitem_import.connect("activate", parent.logbook.import_log)
      subm_logbook.append(mitem_import)
      self.items["IMPORT_LOG"] = mitem_import

      # Export the current log
      mitem_export = Gtk.MenuItem("Export Log")
      mitem_export.connect("activate", parent.logbook.export_log)
      subm_logbook.append(mitem_export)
      self.items["EXPORT_LOG"] = mitem_export
 
      subm_logbook.append(Gtk.SeparatorMenuItem())

      # Quit
      mitem_quit = Gtk.MenuItem("Quit")
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
      
      mitem_addrecord = Gtk.MenuItem("Add Record...")
      mitem_addrecord.connect("activate", parent.logbook.add_record_callback)
      key, mod = Gtk.accelerator_parse("<Control>R")
      mitem_addrecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_records.append(mitem_addrecord)
      self.items["ADD_RECORD"] = mitem_addrecord
      
      mitem_editrecord = Gtk.MenuItem("Edit Selected Record...")
      mitem_editrecord.connect("activate", parent.logbook.edit_record_callback, None, None)
      key, mod = Gtk.accelerator_parse("<Control>E")
      mitem_editrecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_records.append(mitem_editrecord)
      self.items["EDIT_RECORD"] = mitem_editrecord

      mitem_deleterecord = Gtk.MenuItem("Delete Selected Record...")
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
      
            
      ###### HELP ######
      mitem_help = Gtk.MenuItem("Help")
      self.append(mitem_help)  
      subm_help = Gtk.Menu()
      mitem_help.set_submenu(subm_help)
      
      # About
      mitem_about = Gtk.MenuItem("About PyQSO")
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
      for item_name in ["NEW_LOG", "DELETE_LOG", "IMPORT_LOG", "EXPORT_LOG"]:
         self.items[item_name].set_sensitive(sensitive)
      return

   def set_record_items_sensitive(self, sensitive):
      for item_name in ["ADD_RECORD", "EDIT_RECORD", "DELETE_RECORD"]:
         self.items[item_name].set_sensitive(sensitive)
      return

