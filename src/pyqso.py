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
      self.logbook.new_log() # Create a new log by default.

      # Set up menu and tool bars
      # These classes depend on the Logbook class,
      # so pack the logbook after the menu and toolbar.
      menu = Menu(self)
      vbox_outer.pack_start(menu, False, False, 0)
      toolbar = Toolbar(self)
      vbox_outer.pack_start(toolbar, False, False, 0)
      
      vbox_outer.pack_start(self.logbook, True, True, 0)

      self.statusbar = Gtk.Statusbar()
      context_id = self.statusbar.get_context_id("Status")
      vbox_outer.pack_start(self.statusbar, False, False, 0)

      self.show_all()
      
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

