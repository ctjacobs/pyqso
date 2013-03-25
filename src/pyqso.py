#!/usr/bin/env python
# File: pyqso.py

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
import optparse

# PyQSO modules
from adif import *
from logbook import *
from menu import *
from toolbar import *
from record_dialog import *
   
# The PyQSO application class
class PyQSO(Gtk.Window):
   
   def __init__(self):
         
      # Call the constructor of the super class (Gtk.Window)
      Gtk.Window.__init__(self, title="PyQSO (development version)")
      
      self.set_size_request(500, 300)
      self.set_position(Gtk.WindowPosition.CENTER)
      # Kills the application if the close button is clicked on the main window itself. 
      self.connect("delete-event", Gtk.main_quit)
      
      vbox_outer = Gtk.VBox()
      self.add(vbox_outer)
      
      # Create a Logbook so we can add/remove/edit Record objects
      self.logbook = Logbook()

      # Set up menu and tool bars
      menu = Menu(self, vbox_outer)
      toolbar = Toolbar(self, vbox_outer)

      # Render the logbook
      self.treeview = Gtk.TreeView(self.logbook)
      self.treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
      self.treeview.connect("row-activated", self.edit_record_callback)
      self.treeselection = self.treeview.get_selection()
      self.treeselection.set_mode(Gtk.SelectionMode.SINGLE)
      # Allow the Logbook to be scrolled up/down
      sw = Gtk.ScrolledWindow()
      sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
      sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
      sw.add(self.treeview)
      vbox_outer.pack_start(sw, True, True, 0)

      # The first column of the logbook will always be the unique record index.
      # Let's append this separately to the field names.
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Index", renderer, text=0)
      column.set_resizable(True)
      column.set_min_width(50)
      self.treeview.append_column(column)
         
      # Set up column names for each selected field
      field_names = self.logbook.SELECTED_FIELD_NAMES_ORDERED
      for i in range(0, len(field_names)):
         renderer = Gtk.CellRendererText()
         column = Gtk.TreeViewColumn(self.logbook.SELECTED_FIELD_NAMES_FRIENDLY[field_names[i]], renderer, text=i+1)
         column.set_resizable(True)
         column.set_min_width(50)
         self.treeview.append_column(column)
      
      self.statusbar = Gtk.Statusbar()
      context_id = self.statusbar.get_context_id("Status")
      vbox_outer.pack_start(self.statusbar, False, False, 0)

      self.show_all()
      
      return
      
   def add_record_callback(self, widget):

      dialog = RecordDialog(self, index=None)
      all_valid = False # Are all the field entries valid?

      while(not all_valid): 
         # This while loop gives the user infinite attempts at giving valid data.
         # The add/edit record window will stay open until the user gives valid data,
         # or until the Cancel button is clicked.
         all_valid = True
         response = dialog.run() #FIXME: Is it ok to call .run() multiple times on the same RecordDialog object?
         if(response == Gtk.ResponseType.OK):
            fields_and_data = {}
            field_names = self.logbook.SELECTED_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(dialog.is_valid(field_names[i], fields_and_data[field_names[i]]))):
                  # Data is not valid - inform the user.
                  message = Gtk.MessageDialog(self, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "The data in field \"%s\" is not valid!" % field_names[i])
                  message.run()
                  message.destroy()
                  all_valid = False
                  break # Don't check the other data until the user has fixed the current one.

            if(all_valid):
               # All data has been validated, so we can go ahead and add the new record.
               self.logbook.add_record(fields_and_data)
               # Select the new Record's row in the treeview.
               self.treeselection.select_path(self.logbook.get_number_of_records()-1)

      dialog.destroy()
      return
      
   def delete_record_callback(self, widget):
      # Get the selected row in the logbook
      (model, path) = self.treeselection.get_selected_rows()
      try:
         iter = model.get_iter(path[0])
         index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Trying to delete a record, but there are no records in the logbook!")
         return

      dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                 Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 
                                 "Are you sure you want to delete record %d?" % index)
      response = dialog.run()
      if(response == Gtk.ResponseType.YES):
         self.logbook.delete_record(iter, index)
         
      dialog.destroy()

      return

   def edit_record_callback(self, widget, path, view_column):
      # Note: the path and view_column arguments need to be passed in
      # since they associated with the row-activated signal.

      # Get the selected row in the logbook
      (model, path) = self.treeselection.get_selected_rows()
      try:
         iter = model.get_iter(path[0])
         row_index = model.get_value(iter,0)
      except IndexError:
         logging.debug("Could not find the selected row's index!")
         return

      dialog = RecordDialog(self, index=row_index)
      all_valid = False # Are all the field entries valid?

      while(not all_valid): 
         # This while loop gives the user infinite attempts at giving valid data.
         # The add/edit record window will stay open until the user gives valid data,
         # or until the Cancel button is clicked.
         all_valid = True
         response = dialog.run() #FIXME: Is it ok to call .run() multiple times on the same RecordDialog object?
         if(response == Gtk.ResponseType.OK):
            fields_and_data = {}
            field_names = self.logbook.SELECTED_FIELD_NAMES_ORDERED
            for i in range(0, len(field_names)):
               #TODO: Validate user input!
               fields_and_data[field_names[i]] = dialog.get_data(field_names[i])
               if(not(dialog.is_valid(field_names[i], fields_and_data[field_names[i]]))):
                  # Data is not valid - inform the user.
                  message = Gtk.MessageDialog(self, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 
                                    "The data in field \"%s\" is not valid!" % field_names[i])
                  message.run()
                  message.destroy()
                  all_valid = False
                  break # Don't check the other data until the user has fixed the current one.

            if(all_valid):
               # All data has been validated, so we can go ahead and update the record.
               # First update the Record object... 
               self.logbook.records[row_index].set_data(field_names[i], fields_and_data[field_names[i]])
               # ...and then the Logbook.
               # (we add 1 onto the column_index here because we don't want to consider the index column)
               self.logbook[row_index][i+1] = fields_and_data[field_names[i]]

      dialog.destroy()
      return

   def show_about(self, widget):
      about = Gtk.AboutDialog()
      about.set_program_name("PyQSO")
      about.set_version("Development version")
      about.set_authors(["Christian Jacobs"])
      about.set_license('''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.''')
      about.set_comments("PyQSO: A Python-based contact logging tool for amateur radio operators")
      about.run()
      about.destroy()
      return

      
if(__name__ == '__main__'):
   # Get any command line arguments
   parser = optparse.OptionParser()
   parser.add_option('-l', '--log', action="store_true", default=False, help='Enable logging. All log messages will be written to pyqso.log.')
   (options, args) = parser.parse_args()

   # Set up debugging output
   if(options.log):
      logging.basicConfig(level=logging.DEBUG, filename="pyqso.log", 
                        format="%(asctime)s %(levelname)s: %(message)s", 
                        datefmt="%Y-%m-%d %H:%M:%S")

   application = PyQSO() # Populate the main window and show it
   Gtk.main() # Start up the event loop!

