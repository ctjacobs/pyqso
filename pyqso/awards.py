#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian Thomas Jacobs.

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

from gi.repository import Gtk
import logging
import sqlite3 as sqlite


class Awards:

    """ A tool for tracking progress towards an award. Currently this only supports the DXCC award.
    For more information visit http://www.arrl.org/dxcc """

    def __init__(self, application):
        """ Set up a table for progress tracking purposes.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """
        # TODO: Add more awards. This only considers the DXCC award for now.
        logging.debug("Setting up awards table...")

        self.application = application
        self.builder = self.application.builder

        self.bands = ["70cm", "2m", "6m", "10m", "12m", "15m", "17m", "20m", "30m", "40m", "80m", "160m"]
        self.modes = ["Phone", "CW", "Digital", "Mixed"]

        data_types = [str] + [int]*len(self.bands)
        self.awards = Gtk.ListStore(*data_types)

        # The main table for the awards.
        self.treeview = Gtk.TreeView(model=self.awards)
        # A separate, empty column just for the mode names.
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

        # Show the table in the Awards tab.
        self.builder.get_object("awards").add(self.treeview)
        self.builder.get_object("awards").show_all()

        logging.debug("Awards table set up successfully.")

        self.count(self.application.logbook)

    def count(self, logbook):
        """ Update the table for progress tracking.

        :arg logbook: The logbook containing logs which in turn contain QSOs.
        :returns: A list of lists containing the QSO counts for different modes and bands.
        :rtype: list
        """

        logging.debug("Counting the band/mode combinations for the awards table...")

        # Wipe everything and start again.
        self.awards.clear()

        # For each mode, add a new list for holding the totals, and initialise the values to zero.
        count = []
        for i in range(0, len(self.bands)):
            count.append([0]*len(self.bands))

        for log in logbook.logs:
            try:
                records = log.records
                for r in records:
                    if r["BAND"] is not None and r["MODE"] is not None:
                        if r["BAND"].lower() in self.bands and r["MODE"] != "":
                            band = self.bands.index(r["BAND"].lower())
                            # Phone modes
                            if r["MODE"].upper() in ["FM", "AM", "SSB", "SSTV"]:
                                count[0][band] += 1
                            elif r["MODE"].upper() == "CW":
                                count[1][band] += 1
                            else:
                                # FIXME: This assumes that all the other modes in the ADIF list are digital modes. Is this the case?
                                count[2][band] += 1
                            count[3][band] += 1  # Keep the total of each column in the "Mixed" mode.

            except sqlite.Error as e:
                logging.error("Could not update the awards table for '%s' because of a database error." % log.name)
                logging.exception(e)

        # Insert the rows containing the totals.
        for i in range(0, len(self.modes)):
            self.awards.append([self.modes[i]] + count[i])

        logging.debug("Awards table updated.")
        return count
