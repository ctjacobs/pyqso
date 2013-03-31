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
from os.path import basename

from adif import *
from log import *

class Logbook(Gtk.Notebook):
   ''' A Logbook object can store multiple Log objects. '''
   
   def __init__(self):

      Gtk.Notebook.__init__(self)
            
      # A stack of Log objects
      self.logs = []

      # For rendering the logs. One treeview and one treeselection per Log.
      self.treeview = []
      self.treeselection = []
      
      logging.debug("New Logbook instance created!")
     
   def new_log(self, widget=None):
      l = Log() # Empty log
      self.logs.append(l)
      self.render_log(l)
      return

   def open_log(self, widget, parent):
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

      for log in self.logs:
         if(log.path == path):
            dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                 "Log %s is already open." % path)
            response = dialog.run()
            dialog.destroy()
            return
      
      adif = ADIF()
      records = adif.read(path)
      
      l = Log(records, path, basename(path))
      self.logs.append(l)
      self.render_log(l)
      
      return
      
   def save_log(self, widget=None):
      current = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(current == -1):
         logging.debug("No log files to save!")
         return

      log = self.logs[current]
      if(log.path is None):
         self.save_log_as()  
      else:
         # Log is already saved somewhere.
         adif = ADIF()
         adif.write(log.records, log.path)
         if(log.modified):
            log.name = basename(log.path)
            self.set_tab_label_text(self.get_nth_page(current), log.name)
            log.set_modified(False)
      return

   def save_log_as(self, widget=None):

      current = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(current == -1):
         logging.debug("No log files to save!")
         return

      log = self.logs[current]

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
      adif.write(log.records, path)

      if(log.modified):
         log.path = path
         log.name = basename(log.path)
         self.set_tab_label_text(self.get_nth_page(current), log.name)
         log.set_modified(False)
      return

   def close_log(self, widget, parent):
      current = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(current == -1):
         logging.debug("No log files to close!")
         return
      log = self.logs[current]

      if(log.modified):
         dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 
                                 "Log %s is not saved. Are you sure you want to close it?" % log.name[0:len(log.name)-1]) # Here we ignore the * at the end of the log's name.
         response = dialog.run()
         dialog.destroy()
         if(response == Gtk.ResponseType.NO):
            return

      self.logs.pop(current)
      # Remove the log from the renderers too
      self.treeview.pop(current)
      self.treeselection.pop(current)
      # And finally remove the tab in the Logbook
      self.remove_page(current)

      return

   def render_log(self, log):
      # Render the Log
      current = self.get_number_of_logs()-1
      #sorter = Gtk.TreeModelSort(model=log) #FIXME: Get sorted columns working!
      #sorter.set_sort_column_id(1, Gtk.SortType.ASCENDING)
      #self.treeview.append(Gtk.TreeView(sorter))
      self.treeview.append(Gtk.TreeView(log))
      self.treeview[current].set_grid_lines(Gtk.TreeViewGridLines.BOTH)
      #FIXME: Ideally we want the parent window to be passed in to self.edit_record_callback.
      self.treeview[current].connect("row-activated", self.edit_record_callback, None)
      self.treeselection.append(self.treeview[current].get_selection())
      self.treeselection[current].set_mode(Gtk.SelectionMode.SINGLE)
      # Allow the Log to be scrolled up/down
      sw = Gtk.ScrolledWindow()
      sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
      sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
      sw.add(self.treeview[current])
      vbox = Gtk.VBox()
      vbox.pack_start(sw, True, True, 0)
      self.append_page(vbox, Gtk.Label(self.logs[current].name)) # Append the new log as a new tab

      # The first column of the logbook will always be the unique record index.
      # Let's append this separately to the field names.
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Index", renderer, text=0)
      column.set_resizable(True)
      column.set_min_width(50)
      self.treeview[current].append_column(column)
         
      # Set up column names for each selected field
      field_names = self.logs[current].SELECTED_FIELD_NAMES_ORDERED
      for i in range(0, len(field_names)):
         renderer = Gtk.CellRendererText()
         column = Gtk.TreeViewColumn(self.logs[current].SELECTED_FIELD_NAMES_FRIENDLY[field_names[i]], renderer, text=i+1)
         column.set_resizable(True)
         column.set_min_width(50)
         self.treeview[current].append_column(column)

      self.show_all()

   def add_record_callback(self, widget, parent):

      current = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(current == -1):
         logging.debug("Tried to add a record, but no log present!")
         return
      log = self.logs[current]
      dialog = RecordDialog(root_window=parent, log=log, index=None)
      all_valid = False # Are all the field entries valid?

      while(not all_valid): 
         # This while loop gives the user infinite attempts at giving valid data.
         # The add/edit record window will stay open until the user gives valid data,
         # or until the Cancel button is clicked.
         all_valid = True
         response = dialog.run() #FIXME: Is it ok to call .run() multiple times on the same RecordDialog object?
         if(response == Gtk.ResponseType.OK):
            fields_and_data = {}
            field_names = log.SELECTED_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(dialog.is_valid(field_names[i], fields_and_data[field_names[i]], log.SELECTED_FIELD_NAMES_TYPES[field_names[i]]))):
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
               log_entry = [log.get_number_of_records()] # Add the next available record index
               field_names = log.SELECTED_FIELD_NAMES_ORDERED
               for i in range(0, len(field_names)):
                  log_entry.append(fields_and_data[field_names[i]])
               log.append(log_entry)
               log.add_record(fields_and_data)
               # Select the new Record's row in the treeview.
               self.treeselection[current].select_path(log.get_number_of_records()-1)
               self.set_tab_label_text(self.get_nth_page(current), log.name)

      dialog.destroy()
      return
      
   def delete_record_callback(self, widget, parent):
      current = self.get_current_page() # Get the selected log
      if(current == -1):
         logging.debug("Tried to delete a record, but no log present!")
         return
      (model, path) = self.treeselection[current].get_selected_rows() # Get the selected row in the log
      try:
         iter = model.get_iter(path[0])
         index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Trying to delete a record, but there are no records in the log!")
         return

      dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 
                                 "Are you sure you want to delete record %d?" % index)
      response = dialog.run()
      if(response == Gtk.ResponseType.YES):
         # Deletes the record with index 'index' from the Records list.
         # 'iter' is needed to remove the record from the ListStore itself.
         self.logs[current].delete_record(index, iter)
         
      dialog.destroy()
      self.set_tab_label_text(self.get_nth_page(current), self.logs[current].name)
      return

   def edit_record_callback(self, widget, path, view_column, parent):
      # Note: the path and view_column arguments need to be passed in
      # since they associated with the row-activated signal.

      current = self.get_current_page() # Get the selected log
      if(current == -1):
         logging.debug("Tried to edit a record, but no log present!")
         return
      
      log = self.logs[current]

      (model, path) = self.treeselection[current].get_selected_rows() # Get the selected row in the log
      try:
         iter = model.get_iter(path[0])
         row_index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Could not find the selected row's index!")
         return

      dialog = RecordDialog(root_window=parent, log=self.logs[current], index=row_index)
      all_valid = False # Are all the field entries valid?

      while(not all_valid): 
         # This while loop gives the user infinite attempts at giving valid data.
         # The add/edit record window will stay open until the user gives valid data,
         # or until the Cancel button is clicked.
         all_valid = True
         response = dialog.run() #FIXME: Is it ok to call .run() multiple times on the same RecordDialog object?
         if(response == Gtk.ResponseType.OK):
            fields_and_data = {}
            field_names = self.logs[current].SELECTED_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(dialog.is_valid(field_names[i], fields_and_data[field_names[i]], self.logs[current].SELECTED_FIELD_NAMES_TYPES[field_names[i]]))):
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
                  log.edit_record(row_index, field_names[i], fields_and_data[field_names[i]])
                  # ...and then the Logbook.
                  # (we add 1 onto the column_index here because we don't want to consider the index column)
                  log[row_index][i+1] = fields_and_data[field_names[i]]
                  self.set_tab_label_text(self.get_nth_page(current), log.name)

      dialog.destroy()
      return

   def search_log_callback(self, widget):
      print "Search feature has not yet been implemented."

   def get_number_of_logs(self):
      return len(self.logs)

      
