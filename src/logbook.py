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

from adif import *
from record import *
from record_dialog import *

class Logbook(Gtk.ListStore):
   
   def __init__(self):
            
      # FIXME: Allow the user to select the field names. By default, let's select them all.
      self.SELECTED_FIELD_NAMES_TYPES = AVAILABLE_FIELD_NAMES_TYPES
      self.SELECTED_FIELD_NAMES_ORDERED = ["CALL", "DATE", "TIME", "FREQ", "MODE"]
      self.SELECTED_FIELD_NAMES_FRIENDLY = {"CALL":"Callsign",
                                            "DATE":"Date",
                                            "TIME":"Time",
                                            "FREQ":"Frequency",
                                            "MODE":"Mode"}

      # The ListStore constructor needs to know the data types of the columns.
      # The index is always an integer. We will assume the ADIF fields are strings.
      data_types = [int] + [str]*len(self.SELECTED_FIELD_NAMES_ORDERED)
      
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

   def add_record_callback(self, widget, parent):

      dialog = RecordDialog(parent, index=None)
      all_valid = False # Are all the field entries valid?

      while(not all_valid): 
         # This while loop gives the user infinite attempts at giving valid data.
         # The add/edit record window will stay open until the user gives valid data,
         # or until the Cancel button is clicked.
         all_valid = True
         response = dialog.run() #FIXME: Is it ok to call .run() multiple times on the same RecordDialog object?
         if(response == Gtk.ResponseType.OK):
            fields_and_data = {}
            field_names = self.SELECTED_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(dialog.is_valid(field_names[i], fields_and_data[field_names[i]]))):
                  # Data is not valid - inform the user.
                  message = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "The data in field \"%s\" is not valid!" % field_names[i])
                  message.run()
                  message.destroy()
                  all_valid = False
                  break # Don't check the other data until the user has fixed the current one.

            if(all_valid):
               # All data has been validated, so we can go ahead and add the new record.
               logbook_entry = [len(self.records)] # Add the next available record index
               field_names = self.SELECTED_FIELD_NAMES_ORDERED
               for i in range(0, len(field_names)):
                  logbook_entry.append(fields_and_data[field_names[i]])
               self.append(logbook_entry)

               record = Record(fields_and_data)
               self.records.append(record)

               # Hopefully this won't change anything as check_consistency
               # is also called in delete_record, but let's keep it
               # here as a sanity check.
               self.check_consistency() 
               # Select the new Record's row in the treeview.
               parent.treeselection.select_path(self.get_number_of_records()-1)

      dialog.destroy()
      return
      
   def delete_record_callback(self, widget, parent):
      # Get the selected row in the logbook
      (model, path) = parent.treeselection.get_selected_rows()
      try:
         iter = model.get_iter(path[0])
         index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Trying to delete a record, but there are no records in the logbook!")
         return

      dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 
                                 "Are you sure you want to delete record %d?" % index)
      response = dialog.run()
      if(response == Gtk.ResponseType.YES):
         # Deletes the record with index 'index' from self.records.
         # 'iter' is needed to remove the record from the ListStore itself.
         self.records.pop(index)
         self.remove(iter)
         self.check_consistency()
         
      dialog.destroy()

      return

   def edit_record_callback(self, widget, path, view_column, parent):
      # Note: the path and view_column arguments need to be passed in
      # since they associated with the row-activated signal.

      # Get the selected row in the logbook
      (model, path) = parent.treeselection.get_selected_rows()
      try:
         iter = model.get_iter(path[0])
         row_index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Could not find the selected row's index!")
         return

      dialog = RecordDialog(parent, index=row_index)
      all_valid = False # Are all the field entries valid?

      while(not all_valid): 
         # This while loop gives the user infinite attempts at giving valid data.
         # The add/edit record window will stay open until the user gives valid data,
         # or until the Cancel button is clicked.
         all_valid = True
         response = dialog.run() #FIXME: Is it ok to call .run() multiple times on the same RecordDialog object?
         if(response == Gtk.ResponseType.OK):
            fields_and_data = {}
            field_names = self.SELECTED_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(dialog.is_valid(field_names[i], fields_and_data[field_names[i]]))):
                  # Data is not valid - inform the user.
                  message = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "The data in field \"%s\" is not valid!" % field_names[i])
                  message.run()
                  message.destroy()
                  all_valid = False
                  break # Don't check the other data until the user has fixed the current one.

            if(all_valid):
               for i in range(0, len(field_names)):
                  # All data has been validated, so we can go ahead and update the record.
                  # First update the Record object... 
                  self.records[row_index].set_data(field_names[i], fields_and_data[field_names[i]])
                  # ...and then the Logbook.
                  # (we add 1 onto the column_index here because we don't want to consider the index column)
                  self[row_index][i+1] = fields_and_data[field_names[i]]

      dialog.destroy()
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
         for field in self.SELECTED_FIELD_NAMES_ORDERED:
            logbook_entry.append(self.records[i].get_data(field))
         self.append(logbook_entry)
      
      return
      
      
