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
import sys
import sqlite3 as sqlite
from os.path import basename, getctime, getmtime
import datetime

from adif import *
from log import *
from new_log_dialog import *

class Logbook(Gtk.Notebook):
   ''' A Logbook object can store multiple Log objects. '''
   
   def __init__(self, root_window):

      Gtk.Notebook.__init__(self)

      self.root_window = root_window
      self.connection = None
      self.summary = {}

      logging.debug("New Logbook instance created!")
      
   def db_connect(self, widget=None, path=None):
      ''' Creates an SQL database connection to the Logbook's data source '''

      if(path is None):
         # If no path has been provided, get one from a "File Open" dialog.
         dialog = Gtk.FileChooserDialog("Open SQLite Database File",
                                    None,
                                    Gtk.FileChooserAction.OPEN,
                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
         filter = Gtk.FileFilter()
         filter.set_name("All SQLite Database files")
         filter.add_pattern("*.db")
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
         else:
            self.path = path
      else:
         # Use existing user input
         self.path = path

      # Try setting up the SQL database connection
      if(self.connection):
         # Destroy any existing connections first.
         self.db_disconnect()
      try:
         self.connection = sqlite.connect(self.path)
         self.connection.row_factory = sqlite.Row
      except sqlite.Error as e:
         logging.exception(e)
         sys.exit(1) # PyQSO can't connect to the database. This error is fatal.

      # A stack of Log objects
      self.logs = []
      
      # For rendering the logs. One treeview and one treeselection per Log.
      self.treeview = []
      self.treeselection = []
      self.sorter = []
      self._create_summary_page()
      self._create_new_log_tab()

      # FIXME: This is an unfortunate work-around. If the area around the "+/New Log" button
      # is clicked, PyQSO will change to an empty page. This signal is used to stop this from happening. 
      self.connect("switch-page", self._on_switch_page)

      if(self.connection):
         context_id = self.root_window.statusbar.get_context_id("Status")
         self.root_window.statusbar.push(context_id, "Logbook: %s" % self.path)
         self.root_window.toolbar.set_connect_button_sensitive(False)
         self.root_window.menu.set_connect_item_sensitive(False)
         self.root_window.menu.set_log_items_sensitive(True)

      self.open_logs()

      self.show_all()

      return
         
   def db_disconnect(self, widget=None):
      if(self.connection):
         try:
            self.connection.close()
            self.connection = None
         except sqlite.Error as e:
            logging.exception(e)

         context_id = self.root_window.statusbar.get_context_id("Status")
         self.root_window.statusbar.push(context_id, "Not connected to a Logbook.")
         self.root_window.toolbar.set_connect_button_sensitive(True)
         self.root_window.menu.set_connect_item_sensitive(True)
         self.root_window.menu.set_log_items_sensitive(False)
      else:
         logging.error("Already disconnected. Nothing to do here.")

      while(self.get_n_pages() > 0):
         # Once a page is removed, the other pages get re-numbered,
         # so a 'for' loop isn't the best option here.
         self.remove_page(0)

      return

   def _create_new_log_tab(self):
      # Create a blank page in the Notebook for the "+" (New Log) tab
      blank_treeview = Gtk.TreeView([])
      # Allow the Log to be scrolled up/down
      sw = Gtk.ScrolledWindow()
      sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
      sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
      sw.add(blank_treeview)
      vbox = Gtk.VBox()
      vbox.pack_start(sw, True, True, 0)

      # Add a "+" button to the tab
      hbox = Gtk.HBox(False, 0)
      icon = Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
      button = Gtk.Button()
      button.set_relief(Gtk.ReliefStyle.NONE)
      button.set_focus_on_click(False)
      button.connect("clicked", self.new_log)
      button.add(icon)
      button.set_tooltip_text('New Log')
      hbox.pack_start(button, False, False, 0)
      hbox.show_all()
      vbox.show_all()

      self.insert_page(vbox, hbox, 1)
      self.show_all()
      self.set_current_page(0)
      return

   def _create_summary_page(self):

      vbox = Gtk.VBox()

      hbox = Gtk.HBox()
      label = Gtk.Label(halign=Gtk.Align.START)
      label.set_markup("<span size=\"x-large\">%s</span>" % basename(self.path))
      hbox.pack_start(label, False, False, 6)
      vbox.pack_start(hbox, False, False, 2)

      hbox = Gtk.HBox()
      label = Gtk.Label("Number of logs: ", halign=Gtk.Align.START)
      hbox.pack_start(label, False, False, 6)
      self.summary["NUMBER_OF_LOGS"] = Gtk.Label("0")
      hbox.pack_start(self.summary["NUMBER_OF_LOGS"], False, False, 2)
      vbox.pack_start(hbox, False, False, 2)

      hbox = Gtk.HBox()
      label = Gtk.Label("Date modified: ", halign=Gtk.Align.START)
      hbox.pack_start(label, False, False, 6)
      self.summary["DATE_MODIFIED"] = Gtk.Label("0")
      hbox.pack_start(self.summary["DATE_MODIFIED"], False, False, 2)
      vbox.pack_start(hbox, False, False, 2)

      hbox = Gtk.HBox(False, 0)
      label = Gtk.Label("Summary  ")
      icon = Gtk.Image.new_from_stock(Gtk.STOCK_INDEX, Gtk.IconSize.MENU)
      hbox.pack_start(label, False, False, 0)
      hbox.pack_start(icon, False, False, 0)
      hbox.show_all()

      self.insert_page(vbox, hbox, 0) # Append the new log as a new tab
      self.show_all()

      return

   def _update_summary(self):
      self.summary["NUMBER_OF_LOGS"].set_label(str(self.get_number_of_logs()))
      self.summary["DATE_MODIFIED"].set_label(str(datetime.fromtimestamp(getmtime(self.path))))
      return

   def _on_switch_page(self, widget, label, new_page):
      if(new_page == self.get_n_pages()-1): # The last (right-most) tab is the "New Log" tab.
         self.stop_emission("switch-page")
      if(new_page == 0):
         self.root_window.toolbar.set_record_buttons_sensitive(False)
         self.root_window.menu.set_record_items_sensitive(False)
      else:
         self.root_window.toolbar.set_record_buttons_sensitive(True)
         self.root_window.menu.set_record_items_sensitive(True)
      return

   def new_log(self, widget=None):
      if(self.connection is None):
         return
      exists = True
      dialog = NewLogDialog(self.root_window)
      while(exists):
         response = dialog.run()
         if(response == Gtk.ResponseType.OK):
            log_name = dialog.get_log_name()
            try:
               c = self.connection.cursor()
               query = "CREATE TABLE %s (id INTEGER PRIMARY KEY AUTOINCREMENT" % log_name
               for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
                  s = ", %s TEXT" % field_name.lower()
                  query = query + s
               query = query + ")"
               c.execute(query)
               exists = False
            except sqlite.Error as e:
               logging.exception(e)
               # Data is not valid - inform the user.
               message = Gtk.MessageDialog(self.root_window, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "Database error. Try another log name.")
               message.run()
               message.destroy()
               exists = True
         else:
            dialog.destroy()
            return

      dialog.destroy()

      l = Log(self.connection, log_name) # Empty log
      l.populate()

      self.logs.append(l)
      self.render_log(self.get_number_of_logs()-1)
      self._update_summary()

      self.set_current_page(self.get_number_of_logs())
      return

   def open_logs(self):
      with self.connection:
         c = self.connection.cursor()
         c.execute("SELECT name FROM sqlite_master WHERE type='table'")
         names = c.fetchall()

      for name in names:
         if(name[0][0:7] == "sqlite_"):
            continue # Skip SQLite internal tables
         l = Log(self.connection, name[0])
         l.populate()
         self.logs.append(l)
         self.render_log(self.get_number_of_logs()-1)       

      self._update_summary()  
      return

   def delete_log(self, widget, page_index=None):
      if(self.connection is None):
         return
      if(page_index is None):
         page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
      log_index = page_index - 1

      if(page_index == 0 or page_index == self.get_n_pages()-1): # Only the "New Log" tab is present (i.e. no actual logs in the logbook)
         logging.debug("No logs to delete!")
         return
      log = self.logs[log_index]

      dialog = Gtk.MessageDialog(self.root_window, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                              Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 
                              "Are you sure you want to delete log %s?" % log.name)
      response = dialog.run()
      dialog.destroy()
      if(response == Gtk.ResponseType.YES):
         with self.connection:
            c = self.connection.cursor()
            c.execute("DROP TABLE %s" % log.name)

         self.logs.pop(log_index)
         # Remove the log from the renderers too
         self.treeview.pop(log_index)
         self.treeselection.pop(log_index)
         self.sorter.pop(log_index)
         # And finally remove the tab in the Logbook
         self.remove_page(page_index)

      self._update_summary()
      return

   def render_log(self, index):
      # Render the Log
      self.sorter.append(Gtk.TreeModelSort(model=self.logs[index]))
      self.sorter[index].set_sort_column_id(0, Gtk.SortType.ASCENDING)
      self.treeview.append(Gtk.TreeView(self.sorter[index]))
      self.treeview[index].set_grid_lines(Gtk.TreeViewGridLines.BOTH)
      self.treeview[index].connect("row-activated", self.edit_record_callback)
      self.treeselection.append(self.treeview[index].get_selection())
      self.treeselection[index].set_mode(Gtk.SelectionMode.SINGLE)
      # Allow the Log to be scrolled up/down
      sw = Gtk.ScrolledWindow()
      sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
      sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
      sw.add(self.treeview[index])
      vbox = Gtk.VBox()
      vbox.pack_start(sw, True, True, 0)

      # Add a close button to the tab
      hbox = Gtk.HBox(False, 0)
      label = Gtk.Label(self.logs[index].name)
      hbox.pack_start(label, False, False, 0)
      icon = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
      button = Gtk.Button()
      button.set_relief(Gtk.ReliefStyle.NONE)
      button.set_focus_on_click(False)
      button.connect("clicked", self.delete_log, index+1)
      button.add(icon)
      hbox.pack_start(button, False, False, 0)
      hbox.show_all()

      self.insert_page(vbox, hbox, index+1) # Append the new log as a new tab

      # The first column of the logbook will always be the unique record index.
      # Let's append this separately to the field names.
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Index", renderer, text=0)
      column.set_resizable(True)
      column.set_min_width(50)
      column.set_clickable(True)
      column.set_sort_order(Gtk.SortType.ASCENDING)
      column.set_sort_indicator(True)
      column.connect("clicked", self.sort_log, 0)
      self.treeview[index].append_column(column)
         
      # Set up column names for each selected field
      field_names = self.logs[index].SELECTED_FIELD_NAMES_ORDERED
      for i in range(0, len(field_names)):
         renderer = Gtk.CellRendererText()
         column = Gtk.TreeViewColumn(self.logs[index].SELECTED_FIELD_NAMES_FRIENDLY[field_names[i]], renderer, text=i+1)
         column.set_resizable(True)
         column.set_min_width(50)
         column.set_clickable(True)
         column.connect("clicked", self.sort_log, i+1)
         self.treeview[index].append_column(column)

      self.show_all()
      return

   def sort_log(self, widget, column_index):
      log_index = self.get_current_page()-1
      column = self.treeview[log_index].get_column(column_index)

      # If we are operating on the currently-sorted column...
      if(self.sorter[log_index].get_sort_column_id()[0] == column_index):
         order = column.get_sort_order()
         # ...then check if we need to reverse the order of searching.
         if(order == Gtk.SortType.ASCENDING):
            self.sorter[log_index].set_sort_column_id(column_index, Gtk.SortType.DESCENDING)
            column.set_sort_order(Gtk.SortType.DESCENDING)
         else:
            self.sorter[log_index].set_sort_column_id(column_index, Gtk.SortType.ASCENDING)
            column.set_sort_order(Gtk.SortType.ASCENDING)
      else:
         # Otherwise, change to the new sorted column. Default to ASCENDING order.
         self.sorter[log_index].set_sort_column_id(column_index, Gtk.SortType.ASCENDING)
         column.set_sort_order(Gtk.SortType.ASCENDING)

         # Show an arrow pointing in the direction of the sorting.
         # (First we need to remove the arrow from the previously-sorted column.
         # Since we don't know which one that was, just remove the arrow from all columns
         # and start again. This only loops over a few dozen columns at most, so
         # hopefully it won't take too much time.)
         for i in range(0, len(self.logs[log_index].SELECTED_FIELD_NAMES_ORDERED)):
            column = self.treeview[log_index].get_column(i)
            column.set_sort_indicator(False)
         column = self.treeview[log_index].get_column(column_index)
         column.set_sort_indicator(True)
      return

   def import_log(self, widget=None):
      dialog = Gtk.FileChooserDialog("Import ADIF Log File",
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

      log_name = basename(path)
      try:
         c = self.connection.cursor()
         query = "CREATE TABLE %s (id INTEGER PRIMARY KEY AUTOINCREMENT" % log_name
         for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
            s = ", %s TEXT" % field_name.lower()
            query = query + s
         query = query + ")"
         c.execute(query)
      except sqlite.Error as e:
         logging.exception(e)
         # Data is not valid - inform the user.
         message = Gtk.MessageDialog(self.root_window, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "Database error. Try another log name.")
         message.run()
         message.destroy()
         return
      
      adif = ADIF()
      records = adif.read(path)
      
      l = Log(self.connection, log_name)
      for record in records:
         print record
         l.add_record(record)
      l.populate()

      self.logs.append(l)
      self.render_log(self.get_number_of_logs()-1)
      self._update_summary()
      
      return
      
   def export_log(self, widget=None):

      page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(page_index == 0 or page_index == self.get_n_pages()-1):
         logging.debug("Tried to add a record, but no log present!")
         return
      log_index = page_index - 1

      log = self.logs[log_index]

      dialog = Gtk.FileChooserDialog("Export Log to File",
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
      adif.write(log.get_all_records(), path)

      return

   def add_record_callback(self, widget):

      page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(page_index == 0 or page_index == self.get_n_pages()-1):
         logging.debug("Tried to add a record, but no log present!")
         return
      log_index = page_index - 1
      log = self.logs[log_index]
      dialog = RecordDialog(root_window=self.root_window, log=log, index=None)
      all_valid = False # Are all the field entries valid?

      adif = ADIF()

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
               if(not(adif.is_valid(field_names[i], fields_and_data[field_names[i]], log.SELECTED_FIELD_NAMES_TYPES[field_names[i]]))):
                  # Data is not valid - inform the user.
                  message = Gtk.MessageDialog(self.root_window, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "The data in field \"%s\" is not valid!" % field_names[i])
                  message.run()
                  message.destroy()
                  all_valid = False
                  break # Don't check the other data until the user has fixed the current one.

            if(all_valid):
               # All data has been validated, so we can go ahead and add the new record.
               log.add_record(fields_and_data)
               self._update_summary()
               # Select the new Record's row in the treeview.
               self.treeselection[log_index].select_path(log.get_number_of_records())

      dialog.destroy()
      return
      
   def delete_record_callback(self, widget):
      page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(page_index == 0 or page_index == self.get_n_pages()-1):
         logging.debug("Tried to delete a record, but no log present!")
         return
      log_index = page_index - 1
      (model, path) = self.treeselection[log_index].get_selected_rows() # Get the selected row in the log
      try:
         iter = model.get_iter(path[0])
         index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Trying to delete a record, but there are no records in the log!")
         return

      dialog = Gtk.MessageDialog(self.root_window, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 
                                 "Are you sure you want to delete record %d?" % index)
      response = dialog.run()
      if(response == Gtk.ResponseType.YES):
         # Deletes the record with index 'index' from the Records list.
         # 'iter' is needed to remove the record from the ListStore itself.
         self.logs[log_index].delete_record(index, iter)
         self._update_summary()
         
      dialog.destroy()
      return

   def edit_record_callback(self, widget, path, view_column):
      # Note: the path and view_column arguments need to be passed in
      # since they associated with the row-activated signal.

      page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(page_index == 0 or page_index == self.get_n_pages()-1):
         logging.debug("Tried to edit a record, but no log present!")
         return
      log_index = page_index - 1
      
      log = self.logs[log_index]

      (model, path) = self.treeselection[log_index].get_selected_rows() # Get the selected row in the log
      try:
         iter = model.get_iter(path[0])
         row_index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Could not find the selected row's index!")
         return

      dialog = RecordDialog(root_window=self.root_window, log=self.logs[log_index], index=row_index)
      all_valid = False # Are all the field entries valid?

      adif = ADIF()

      while(not all_valid): 
         # This while loop gives the user infinite attempts at giving valid data.
         # The add/edit record window will stay open until the user gives valid data,
         # or until the Cancel button is clicked.
         all_valid = True
         response = dialog.run() #FIXME: Is it ok to call .run() multiple times on the same RecordDialog object?
         if(response == Gtk.ResponseType.OK):
            fields_and_data = {}
            field_names = self.logs[log_index].SELECTED_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(adif.is_valid(field_names[i], fields_and_data[field_names[i]], self.logs[log_index].SELECTED_FIELD_NAMES_TYPES[field_names[i]]))):
                  # Data is not valid - inform the user.
                  message = Gtk.MessageDialog(self.root_window, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "The data in field \"%s\" is not valid!" % field_names[i])
                  message.run()
                  message.destroy()
                  all_valid = False
                  break # Don't check the other data until the user has fixed the current one.

            if(all_valid):
               for i in range(0, len(field_names)):
                  # All data has been validated, so we can go ahead and update the record.
                  # First update the record in the database... 
                  log.edit_record(row_index, field_names[i], fields_and_data[field_names[i]])
                  # ...and then in the ListStore
                  # (we add 1 onto the column_index here because we don't want to consider the index column)
                  log.set(iter, i+1, fields_and_data[field_names[i]])
                  self._update_summary()

      dialog.destroy()
      return

   def search_log_callback(self, widget):
      print "Search feature has not yet been implemented."

   def get_number_of_logs(self):
      return len(self.logs)

   def log_name_exists(self, table_name):
      with self.connection:
         c = self.connection.cursor()
         c.execute("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE name=?)", [table_name])
         exists = c.fetchone()
         if(exists[0] == 1):
            return True
      return False

