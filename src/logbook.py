#!/usr/bin/env python 
# File: logbook.py

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

from record import *
from adif import *

class Logbook(Gtk.ListStore):
   
   def __init__(self):
            
      # FIXME: Allow the user to select the field names. By default, let's select them all.
      self.SELECTED_FIELD_NAMES_TYPES = AVAILABLE_FIELD_NAMES_TYPES 
      
      # The ListStore constructor needs to know the data types of the columns.
      # The index is always an integer. We will assume the ADIF fields are strings.
      data_types = [int]
      for key in self.SELECTED_FIELD_NAMES_TYPES.keys():
         data_types.append(str)
      
      # Call the constructor of the super class (Gtk.ListStore)
      Gtk.ListStore.__init__(self, *data_types)
      
      # Begin with no records.
      self.records = []
      
      logging.debug("New Logbook instance created!")
      

   def new_log(self, widget):
      self.records = []
      self.populate()
      return

   def open_log(self, widget):
      dialog = Gtk.FileChooserDialog("Open File",
                                    None,
                                    Gtk.FileChooserAction.OPEN,
                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
      filter = Gtk.FileFilter()
      filter.set_name("All ADIF files")
      filter.add_pattern("*.adi")
      dialog.add_filter(filter)
      
      response = dialog.run()
      if(response == Gtk.ResponseType.OK):
         path = dialog.get_filename()
      else:
         path = None
      dialog.destroy()
      
      if(path is None):
         logging.debug("No file path specified.")
         return
      
      adif = ADIF()
      self.records = adif.read(path)
      self.populate()
      
      return
      
   def save_log(self, widget):
      dialog = Gtk.FileChooserDialog("Save File",
                              None,
                              Gtk.FileChooserAction.SAVE,
                              (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                              Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
                              
      response = dialog.run()
      if(response == Gtk.ResponseType.OK):
         path = dialog.get_filename()
      else:
         path = None
      dialog.destroy()
      
      if(path is None):
         logging.debug("No file path specified.")
         return
         
      adif = ADIF()
      adif.write(self.records, path)
      
      return

   def add_record(self, fields_and_data):
      # Adds a record to the end of the logbook
      # using data from the fields_and_data dictionary.

      logbook_entry = [len(self.records)] # Add the next available record index
      field_names = self.SELECTED_FIELD_NAMES_TYPES.keys()
      for i in range(0, len(field_names)):
         logbook_entry.append(fields_and_data[field_names[i]])
      self.append(logbook_entry)

      record = Record(fields_and_data)
      self.records.append(record)

      # Hopefully this won't change anything as check_consistency
      # is also called in delete_record, but let's keep it
      # here as a sanity check.
      self.check_consistency() 
      
      return
      
   def delete_record(self, iter, index):
      # Deletes the record with index 'index' from self.records.
      # 'iter' is needed to remove the record from the ListStore itself.
      self.records.pop(index)
      self.remove(iter)
      self.check_consistency()
      return

   def get_number_of_records(self):
      return len(self.records)

   def get_record(self, index):
      return self.records[index]
      
   def check_consistency(self):
      # Make sure all the record indices are consecutive and 
      # correctly ordered.
      for i in range(0, len(self.records)):
         if(self[i][0] != i):
            self[i][0] = i
      return
         
   def populate(self):
      # Remove everything that is rendered already and start afresh
      self.clear()
      
      for i in range(0, len(self.records)):
         logbook_entry = [] # Create a new logbook entry
         # First append the unique index given to the record.
         logbook_entry.append(i)
         for field in self.SELECTED_FIELD_NAMES_TYPES.keys():
            logbook_entry.append(self.records[i].get_data(field))
         self.append(logbook_entry)
      
      return
      
      
