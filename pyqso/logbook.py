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

from gi.repository import Gtk, GObject, Pango, PangoCairo
import logging
import sqlite3 as sqlite
from os.path import basename, getctime, getmtime, expanduser
import datetime
import ConfigParser

from adif import *
from log import *
from log_name_dialog import *
from auxiliary_dialogs import *

#import Hamlib

class Logbook(Gtk.Notebook):
   ''' A Logbook object can store multiple Log objects. '''
   
   def __init__(self, parent):

      Gtk.Notebook.__init__(self)

      self.parent = parent
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
         # PyQSO can't connect to the database.
         logging.exception(e)
         error(parent=self.parent, message="PyQSO cannot connect to the database. Check file permissions?")
         return

      # A stack of Log objects
      self.logs = []
      
      # For rendering the logs. One treeview and one treeselection per Log.
      self.treeview = []
      self.treeselection = []
      self.sorter = []
      self.filter = []
      self._create_summary_page()
      self._create_new_log_tab()

      # FIXME: This is an unfortunate work-around. If the area around the "+/New Log" button
      # is clicked, PyQSO will change to an empty page. This signal is used to stop this from happening. 
      self.connect("switch-page", self._on_switch_page)

      if(self.connection):
         context_id = self.parent.statusbar.get_context_id("Status")
         self.parent.statusbar.push(context_id, "Logbook: %s" % self.path)
         self.parent.toolbar.set_connect_button_sensitive(False)
         self.parent.menu.set_connect_item_sensitive(False)
         self.parent.menu.set_log_items_sensitive(True)
         self.parent.toolbar.filter_source.set_sensitive(True)

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

         context_id = self.parent.statusbar.get_context_id("Status")
         self.parent.statusbar.push(context_id, "Not connected to a Logbook.")
         self.parent.toolbar.set_connect_button_sensitive(True)
         self.parent.menu.set_connect_item_sensitive(True)
         self.parent.menu.set_log_items_sensitive(False)
         self.parent.toolbar.filter_source.set_sensitive(False)
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

      # Database name in large font at the top of the summary page
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
      t = datetime.fromtimestamp(getmtime(self.path)).strftime("%d %B %Y @ %H:%M")
      self.summary["DATE_MODIFIED"].set_label(str(t))
      return

   def _on_switch_page(self, widget, label, new_page):
      if(new_page == self.get_n_pages()-1): # The last (right-most) tab is the "New Log" tab.
         self.stop_emission("switch-page")
         
      # Disable the record buttons if a log page is not selected.
      if(new_page == 0):
         self.parent.toolbar.set_record_buttons_sensitive(False)
         self.parent.menu.set_record_items_sensitive(False)
      else:
         self.parent.toolbar.set_record_buttons_sensitive(True)
         self.parent.menu.set_record_items_sensitive(True)
      return

   def new_log(self, widget=None):
      if(self.connection is None):
         return
      exists = True
      dialog = LogNameDialog(self.parent)
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
               error(parent=self.parent, message="Database error. Try another log name.")
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

   def delete_log(self, widget, page=None):
      if(self.connection is None):
         return
         
      if(page is None):
         page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
         if(page_index == 0): # If we are on the Summary page...
            logging.debug("No log currently selected!")
            return
         else:
            page = self.get_nth_page(page_index) # Gets the Gtk.VBox of the selected tab in the logbook

      log_index = self.get_log_index(name=page.get_name())
      log = self.logs[log_index]
      
      # We also need the page's index in order to remove it using remove_page below.   
      # This may not be the same as what self.get_current_page() returns.  
      page_index = self.page_num(page)
            
      if(page_index == 0 or page_index == self.get_n_pages()-1): # Only the "New Log" tab is present (i.e. no actual logs in the logbook)
         logging.debug("No logs to delete!")
         return

      response = question(parent=self.parent, message="Are you sure you want to delete log %s?" % log.name)
      if(response == Gtk.ResponseType.YES):
         with self.connection:
            c = self.connection.cursor()
            c.execute("DROP TABLE %s" % log.name)

         self.logs.pop(log_index)
         # Remove the log from the renderers too
         self.treeview.pop(log_index)
         self.treeselection.pop(log_index)
         self.sorter.pop(log_index)
         self.filter.pop(log_index)
         # And finally remove the tab in the Logbook
         self.remove_page(page_index)

      self._update_summary()
      return

   def filter_log(self, widget, callsign):
      for i in range(0, len(self.filter)):
         self.filter[i].refilter()
      return

   def filter_by_callsign(self, model, iter, data):
      value = model.get_value(iter, 1)
      callsign = self.parent.toolbar.filter_source.get_text()
      
      if(callsign is None or callsign == ""):
         # If there is nothing to filter with, then show all the records!
         return True
      else:
         # We need this to be case insensitive
         return callsign.upper() in value or callsign.lower() in value

   def render_log(self, index):
      # Render the Log in the Gtk.Notebook.
      self.filter.append(self.logs[index].filter_new(root=None))
      # Set the callsign column as the column we want to filter by
      self.filter[index].set_visible_func(self.filter_by_callsign, data=None)
      self.sorter.append(Gtk.TreeModelSort(model=self.filter[index]))
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
      vbox.set_name(self.logs[index].name) # Set a name for the tab itself so we can match it up with the associated Log object later.
      vbox.pack_start(sw, True, True, 0)

      # Add a close button to the tab
      hbox = Gtk.HBox(False, 0)
      label = Gtk.Label(self.logs[index].name)
      hbox.pack_start(label, False, False, 0)
      icon = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
      button = Gtk.Button()
      button.set_relief(Gtk.ReliefStyle.NONE)
      button.set_focus_on_click(False)
      button.connect("clicked", self.delete_log, vbox)
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
      field_names = AVAILABLE_FIELD_NAMES_ORDERED
      for i in range(0, len(field_names)):
         renderer = Gtk.CellRendererText()
         column = Gtk.TreeViewColumn(AVAILABLE_FIELD_NAMES_FRIENDLY[field_names[i]], renderer, text=i+1)
         column.set_resizable(True)
         column.set_min_width(50)
         column.set_clickable(True)
         column.connect("clicked", self.sort_log, i+1)

         config = ConfigParser.ConfigParser()
         have_config = (config.read(expanduser('~/.pyqso.ini')) != [])
         if(have_config):
            column.set_visible(config.get("view", AVAILABLE_FIELD_NAMES_ORDERED[i].lower()) == "True")
         self.treeview[index].append_column(column)

      self.show_all()
      return

   def sort_log(self, widget, column_index):
      log_index = self.get_log_index()
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
         for i in range(0, len(AVAILABLE_FIELD_NAMES_ORDERED)):
            column = self.treeview[log_index].get_column(i)
            column.set_sort_indicator(False)
         column = self.treeview[log_index].get_column(column_index)
         column.set_sort_indicator(True)
      return
      
   def rename_log(self, widget=None):
      if(self.connection is None):
         return
      page_index = self.get_current_page()
      if(page_index == 0): # If we are on the Summary page...
         logging.debug("No log currently selected!")
         return
      page = self.get_nth_page(page_index) # Gets the Gtk.VBox of the selected tab in the logbook
      old_log_name = page.get_name()
      
      log_index = self.get_log_index(name=old_log_name)
      
      exists = True
      dialog = LogNameDialog(self.parent, title="Rename Log", name=old_log_name)
      while(exists):
         response = dialog.run()
         if(response == Gtk.ResponseType.OK):
            new_log_name = dialog.get_log_name()
            try:
               c = self.connection.cursor()
               query = "ALTER TABLE %s RENAME TO %s" % (old_log_name, new_log_name)
               c.execute(query)
               exists = False
            except sqlite.Error as e:
               logging.exception(e)
               # Data is not valid - inform the user.
               error(parent=self.parent, message="Database error. Try another log name.")
               exists = True
         else:
            dialog.destroy()
            return

      dialog.destroy()
      
      # Remember to change the Log object's name...
      self.logs[log_index].name = new_log_name
      
      # ...and the page's name
      page.set_name(self.logs[log_index].name)

      # ...and update the tab's label
      hbox = Gtk.HBox(False, 0)
      label = Gtk.Label(new_log_name)
      hbox.pack_start(label, False, False, 0)
      icon = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
      button = Gtk.Button()
      button.set_relief(Gtk.ReliefStyle.NONE)
      button.set_focus_on_click(False)
      button.connect("clicked", self.delete_log, page)
      button.add(icon)
      hbox.pack_start(button, False, False, 0)
      hbox.show_all()
      self.set_tab_label(page, hbox)
      
      # The number of logs will obviously stay the same, but
      # we want to update the logbook's modification date.
      self._update_summary()
      
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

      dialog = LogNameDialog(self.parent, title="Import Log")
      while(True):
         response = dialog.run()
         if(response == Gtk.ResponseType.OK):
            log_name = dialog.get_log_name()
            if(self.log_name_exists(log_name)):
               # Import into existing log
               exists = True
               l = self.logs[self.get_log_index(name=log_name)]
               response = question(parent=self.parent, message="Are you sure you want to import into an existing log?")
               if(response == Gtk.ResponseType.YES):
                  break
            else:
               # Create a new log with the name the user supplies
               exists = False
               try:
                  c = self.connection.cursor()
                  query = "CREATE TABLE %s (id INTEGER PRIMARY KEY AUTOINCREMENT" % log_name
                  for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
                     s = ", %s TEXT" % field_name.lower()
                     query = query + s
                  query = query + ")"
                  c.execute(query)
                  l = Log(self.connection, log_name)
                  break
               except sqlite.Error as e:
                  logging.exception(e)
                  # Data is not valid - inform the user.
                  error(parent=self.parent, message="Database error. Try another log name.")
         else:
            dialog.destroy()
            return
      
      dialog.destroy()

      adif = ADIF()
      records = adif.read(path)      
      print "Importing records..."
      for record in records:
         print record
         l.add_record(record)
      l.populate()

      if(not exists):
         self.logs.append(l)
         self.render_log(self.get_number_of_logs()-1)
      self._update_summary()
      
      return
      
   def export_log(self, widget=None):
      page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(page_index == 0): # If we are on the Summary page...
         logging.debug("No log currently selected!")
         return

      log_index = self.get_log_index()
      log = self.logs[log_index]

      dialog = Gtk.FileChooserDialog("Export Log to File",
                              None,
                              Gtk.FileChooserAction.SAVE,
                              (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                              Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
      dialog.set_do_overwrite_confirmation(True)
            
      response = dialog.run()
      if(response == Gtk.ResponseType.OK):
         path = dialog.get_filename()
      else:
         path = None
      dialog.destroy()
         
      if(path is None):
         logging.debug("No file path specified.")
      else:
         adif = ADIF()
         adif.write(log.get_all_records(), path)

      return

   def print_log(self, widget=None):
      page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
      if(page_index == 0): # If we are on the Summary page...
         logging.debug("No log currently selected!")
         return
      log_index = self.get_log_index()
      log = self.logs[log_index]

      self.text_to_print = "Callsign\t---\tDate\t---\tTime\t---\tFrequency\t---\tMode\n"
      records = log.get_all_records()
      for r in records:
         self.text_to_print += str(r["CALL"]) + "\t---\t" + str(r["QSO_DATE"]) + "\t---\t" + str(r["TIME_ON"]) + "\t---\t" + str(r["FREQ"]) + "\t---\t" + str(r["MODE"]) + "\n"

      action = Gtk.PrintOperationAction.PRINT_DIALOG
      operation = Gtk.PrintOperation()
      operation.set_default_page_setup(Gtk.PageSetup())
      operation.set_unit(Gtk.Unit.MM)

      operation.connect("begin_print", self.begin_print)
      operation.connect("draw_page", self.draw_page)
      result = operation.run(action, parent=self.parent)
      return
    
   def begin_print(self, operation, context):
      width = context.get_width()
      height = context.get_height()
      layout = context.create_pango_layout()
      layout.set_font_description(Pango.FontDescription("normal 10"))
      layout.set_width(int(width*Pango.SCALE))
      layout.set_text(self.text_to_print, -1)

      number_of_pages = 0
      page_height = 0
      for line in range(0, layout.get_line_count()):
         layout_line = layout.get_line(line)
         ink_rectangle, logical_rectangle = layout_line.get_extents()
         x_bearing, y_bearing, logical_rectangle_width, logical_rectangle_height = logical_rectangle.x, logical_rectangle.y, logical_rectangle.width, logical_rectangle.height
         self.line_height = logical_rectangle.height/1024.0 + 3
         page_height += self.line_height
         if(page_height + self.line_height > height):
            number_of_pages += 1
            page_height = self.line_height
      operation.set_n_pages(number_of_pages + 1)
      self.text_to_print = self.text_to_print.split("\n")
      return

   def draw_page(self, operation, context, page_number):
      cr = context.get_cairo_context()
      cr.set_source_rgb(0, 0, 0)
      layout = context.create_pango_layout()
 
      current_line_number = 0
      for line in self.text_to_print:
         layout.set_text(line, -1)  
         cr.move_to(5, current_line_number*self.line_height)
         PangoCairo.update_layout(cr, layout)
         PangoCairo.show_layout(cr, layout)
         current_line_number = current_line_number + 1
         if(current_line_number*self.line_height > context.get_height()):
            for j in range(0, current_line_number):
               self.text_to_print.pop(0) # Remove what has been printed already before draw_page is called again
            break
      return

   def add_record_callback(self, widget):
      log_index = self.get_log_index()
      log = self.logs[log_index]
      
      dialog = RecordDialog(parent=self.parent, log=log, index=None)
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
            field_names = AVAILABLE_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(adif.is_valid(field_names[i], fields_and_data[field_names[i]], AVAILABLE_FIELD_NAMES_TYPES[field_names[i]]))):
                  # Data is not valid - inform the user.
                  error(parent=self.parent, message="The data in field \"%s\" is not valid!" % field_names[i])
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
      log_index = self.get_log_index()
      log = self.logs[log_index]
      (sort_model, path) = self.treeselection[log_index].get_selected_rows() # Get the selected row in the log
      try:
         sort_iter = sort_model.get_iter(path[0])
         # Remember that the filter model is a child of the sort model...
         filter_model = sort_model.get_model()
         filter_iter = self.sorter[log_index].convert_iter_to_child_iter(sort_iter)
         # ...and the ListStore model (i.e. the log) is a child of the filter model.
         child_iter = self.filter[log_index].convert_iter_to_child_iter(filter_iter)
         row_index = log.get_value(child_iter,0)
      except IndexError:
         logging.debug("Trying to delete a record, but there are no records in the log!")
         return

      response = question(parent=self.parent, message = "Are you sure you want to delete record %d?" % row_index)
      if(response == Gtk.ResponseType.YES):
         # Deletes the record with index 'row_index' from the Records list.
         # 'iter' is needed to remove the record from the ListStore itself.
         log.delete_record(row_index, child_iter)
         self._update_summary()
      return

   def edit_record_callback(self, widget, path, view_column):
      # Note: the path and view_column arguments need to be passed in
      # since they associated with the row-activated signal.

      log_index = self.get_log_index()
      log = self.logs[log_index]

      (sort_model, path) = self.treeselection[log_index].get_selected_rows() # Get the selected row in the log
      try:
         sort_iter = sort_model.get_iter(path[0])
         # Remember that the filter model is a child of the sort model...
         filter_model = sort_model.get_model()
         filter_iter = self.sorter[log_index].convert_iter_to_child_iter(sort_iter)
         # ...and the ListStore model (i.e. the log) is a child of the filter model.
         child_iter = self.filter[log_index].convert_iter_to_child_iter(filter_iter)
         row_index = log.get_value(child_iter,0)
      except IndexError:
         logging.debug("Could not find the selected row's index!")
         return

      dialog = RecordDialog(parent=self.parent, log=self.logs[log_index], index=row_index)
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
            field_names = AVAILABLE_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(adif.is_valid(field_names[i], fields_and_data[field_names[i]], AVAILABLE_FIELD_NAMES_TYPES[field_names[i]]))):
                  # Data is not valid - inform the user.
                  error(parent=self.parent, message="The data in field \"%s\" is not valid!" % field_names[i])
                  all_valid = False
                  break # Don't check the other data until the user has fixed the current one.

            if(all_valid):
               for i in range(0, len(field_names)):
                  # All data has been validated, so we can go ahead and update the record.
                  # First update the record in the database... 
                  log.edit_record(row_index, field_names[i], fields_and_data[field_names[i]])
                  # ...and then in the ListStore
                  # (we add 1 onto the column_index here because we don't want to consider the index column)
                  log.set(child_iter, i+1, fields_and_data[field_names[i]])
               self._update_summary()

      dialog.destroy()
      return

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

   def get_log_index(self, name=None):
      if(name is None):
         # If no page name is supplied, then just use the currently selected page
         page_index = self.get_current_page() # Gets the index of the selected tab in the logbook
         if(page_index == 0 or page_index == self.get_n_pages()-1):
            # We either have the Summary page, or the "+" (add log) dummy page.
            logging.debug("No log currently selected!")
            return None
         name = self.get_nth_page(page_index).get_name()
      # If a page of the logbook (and therefore a Log object) gets deleted, 
      # then the page_index may not correspond to the index of the log in the self.logs list.
      # Therefore, we have to search for the tab with the same name as the log.
      for i in range(0, len(self.logs)):
         if(self.logs[i].name == name):
            log_index = i
            break
      return log_index

