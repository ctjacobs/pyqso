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
from data_entry_panel import *
   
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
      
      # Create a new Logbook so we can add/remove/edit Record objects
      self.logbook = Logbook()

      # Set up menu bar and populate it
      menu = Menu(self, vbox_outer)

      # Under the menu, we want the data entry panel on the left and the logbook on the right.
      hbox = Gtk.HBox()
      vbox_outer.pack_start(hbox, True, True, 0)
      
      self.data_entry_panel = DataEntryPanel(self, hbox)
      self.data_entry_panel.disable()

      # Render the logbook
      self.treeview = Gtk.TreeView(self.logbook)
      self.treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
      # Allow the Logbook to be scrolled up/down
      sw = Gtk.ScrolledWindow()
      sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
      sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
      sw.add(self.treeview)
      hbox.pack_start(sw, True, True, 0)

      # The first column of the logbook will always be the unique record index.
      # Let's append this separately to the field names.
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("INDEX", renderer, text=0)
      column.set_resizable(True)
      column.set_min_width(50)
      self.treeview.append_column(column)
         
      # Set up column names for each selected field
      field_names = self.logbook.SELECTED_FIELD_NAMES_TYPES.keys()
      for i in range(0, len(field_names)):
         renderer = Gtk.CellRendererText()
         column = Gtk.TreeViewColumn(field_names[i], renderer, text=i+1)
         column.set_resizable(True)
         column.set_min_width(50)
         self.treeview.append_column(column)
      
      self.show_all()
      
      return
      
   def add_record_callback(self, widget):
      self.logbook.add_record()
      return
      
   def delete_record_callback(self, widget):
      # Get the selected row in the logbook and delete it.
      selection = self.treeview.get_selection()
      selection.set_mode(Gtk.SelectionMode.SINGLE)
      (model, path) = selection.get_selected_rows()
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

   def edit_record_callback(self, widget):
      
      #TODO: Validate user input!

      selection = self.treeview.get_selection()
      selection.set_mode(Gtk.SelectionMode.SINGLE)
      (model, path) = selection.get_selected_rows()
      iter = model.get_iter(path[0])
      row_index = model.get_value(iter,0)

      field_names = self.logbook.SELECTED_FIELD_NAMES_TYPES.keys()
      for column_index in range(0, len(field_names)):
         data = self.data_entry_panel.sources[field_names[column_index]].get_text()
         # First update the Record object... 
         # (we add 1 onto the column_index here because we don't want to consider the index column)
         column_name = self.treeview.get_column(column_index+1).get_title()
         self.logbook.records[row_index].set_field(column_name, data)
         # ...and then the Logbook.
         self.logbook[row_index][column_index+1] = data
      
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

