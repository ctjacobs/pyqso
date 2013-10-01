#!/usr/bin/env python
# File: awards.py

#    Copyright (C) 2013 Christian Jacobs.

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

class Awards(Gtk.VBox):
   """ A tool for tracking progress towards an award. Currently this only supports the DXCC award. """
   
   def __init__(self, parent):
      """ Set up a table for progress tracking purposes. """
      #TODO: This only considers the DXCC award for now.
      logging.debug("New Awards instance created!")
         
      Gtk.VBox.__init__(self, spacing=2)

      self.parent = parent

      self.bands = ["70cm", "2m", "6m", "10m", "12m", "15m", "17m", "20m", "30m", "40m", "80m", "160m"]
      self.modes = ["Phone", "CW", "Digital", "Mixed"]
      
      data_types = [str] + [int]*len(self.bands)
      self.awards = Gtk.ListStore(*data_types)

      # The main table for the awards
      self.treeview = Gtk.TreeView(self.awards)
      # A separate, empty column just for the mode names
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Modes", renderer, text=0)
      column.set_clickable(False)
      self.treeview.append_column(column)
      # Now for all the bands...
      logging.debug("Initialising the columns in the awards table.")
      for i in range(0, len(self.bands)):
         renderer = Gtk.CellRendererText()
         column = Gtk.TreeViewColumn(self.bands[i], renderer, text=i+1)
         column.set_min_width(40)
         column.set_clickable(False)
         self.treeview.append_column(column)

      # Add a label to inform the user that this only considers the DXCC award for now.
      label = Gtk.Label(halign=Gtk.Align.START)
      label.set_markup("<span size=\"x-large\">%s</span>" % "DXCC Award")
      self.pack_start(label, False, False, 4)
      # Show the table in the Awards tab
      self.add(self.treeview)
      self.show_all()

      logging.debug("Awards table set up successfully.") 

      self.count()

      return

   def count(self):
      """ Update the table for progress tracking. """
      logging.debug("Counting the band/mode combinations for the awards table...")
      # Wipe everything and start again
      self.awards.clear()
      # For each mode, add a new list for holding the totals, and initialise the values to zero.
      count = []
      for i in range(0, len(self.bands)):
         count.append([0]*len(self.bands))

      for log in self.parent.logbook.logs:
         records = log.get_all_records()
         if(records is not None):
            for r in records:
               if(r["BAND"] is not None and r["MODE"] is not None):
                  if(r["BAND"].lower() in self.bands and r["MODE"] != ""):
                     band = self.bands.index(r["BAND"].lower())
                     # Phone modes
                     if(r["MODE"].upper() in ["FM", "AM", "SSB", "SSTV"]):
                        count[0][band] += 1
                     elif(r["MODE"].upper() == "CW"):
                        count[1][band] += 1
                     else: 
                        #FIXME: This assumes that all the other modes in the ADIF list are digital modes. Is this the case?
                        count[2][band] += 1
                     count[3][band] += 1 # Keep the total of each column in the "Mixed" mode
         else:
            logging.error("Could not update the awards table for '%s' because of a database error." % log.name)
      # Insert the rows containing the totals
      for i in range(0, len(self.modes)):
         self.awards.append([self.modes[i]] + count[i])
      logging.debug("Awards table updated.") 
      return

