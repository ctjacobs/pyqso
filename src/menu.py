#!/usr/bin/env python
# File: menu.py

#    Copyright (C) 2012 Christian Jacobs.

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

class Menu(Gtk.MenuBar):
   
   def __init__(self, parent):
      logging.debug("New Menu instance created!")
      
      # First let's call the constructor of the super class (Gtk.MenuBar)
      Gtk.MenuBar.__init__(self)
      
      agrp = Gtk.AccelGroup()
      parent.add_accel_group(agrp)
      
      ###### FILE ######
      mitem_file = Gtk.MenuItem("Log")
      self.append(mitem_file)  
      subm_file = Gtk.Menu()
      mitem_file.set_submenu(subm_file)
    
      # New ADIF log
      mitem_new = Gtk.MenuItem("New Log")
      mitem_new.connect("activate", parent.logbook.new_log)
      key, mod = Gtk.accelerator_parse("<Control>N")
      mitem_new.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_file.append(mitem_new)
      
      # Open (for opening and reading ADIF files)
      mitem_open = Gtk.MenuItem("Open Log File...")
      mitem_open.connect("activate", parent.logbook.open_log, parent)
      key, mod = Gtk.accelerator_parse("<Control>O")
      mitem_open.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_file.append(mitem_open)
      
      # Save (for writing ADIF files)
      mitem_save = Gtk.MenuItem("Save Log File...")
      mitem_save.connect("activate", parent.logbook.save_log)
      key, mod = Gtk.accelerator_parse("<Control>S")
      mitem_save.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_file.append(mitem_save)

      # Save as (for writing ADIF files)
      mitem_save = Gtk.MenuItem("Save Log File As...")
      mitem_save.connect("activate", parent.logbook.save_log_as)
      key, mod = Gtk.accelerator_parse("<Shift><Control>S")
      mitem_save.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_file.append(mitem_save)

      # Close the current log
      mitem_close = Gtk.MenuItem("Close Log")
      mitem_close.connect("activate", parent.logbook.close_log, parent)
      key, mod = Gtk.accelerator_parse("<Control>W")
      mitem_close.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_file.append(mitem_close)
 
      subm_file.append(Gtk.SeparatorMenuItem())
        
      # Quit
      mitem_quit = Gtk.MenuItem("Quit")
      mitem_quit.connect("activate", Gtk.main_quit)
      key, mod = Gtk.accelerator_parse("<Control>Q")
      mitem_quit.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_file.append(mitem_quit)
      
      
      ###### LOG ######
      mitem_log = Gtk.MenuItem("Record")
      self.append(mitem_log)  
      subm_log = Gtk.Menu()
      mitem_log.set_submenu(subm_log)
      
      mitem_addrecord = Gtk.MenuItem("Add Record...")
      mitem_addrecord.connect("activate", parent.logbook.add_record_callback, parent)
      key, mod = Gtk.accelerator_parse("<Control>R")
      mitem_addrecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_log.append(mitem_addrecord)
      
      mitem_editrecord = Gtk.MenuItem("Edit Selected Record...")
      mitem_editrecord.connect("activate", parent.logbook.edit_record_callback, None, None, parent)
      key, mod = Gtk.accelerator_parse("<Control>E")
      mitem_editrecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_log.append(mitem_editrecord)

      mitem_deleterecord = Gtk.MenuItem("Delete Selected Record...")
      mitem_deleterecord.connect("activate", parent.logbook.delete_record_callback, parent)
      key, mod = Gtk.accelerator_parse("Delete")
      mitem_deleterecord.add_accelerator("activate", agrp, key, mod, Gtk.AccelFlags.VISIBLE)
      subm_log.append(mitem_deleterecord)
      
      
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
      
      return
      
