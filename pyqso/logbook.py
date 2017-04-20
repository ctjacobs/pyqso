#!/usr/bin/env python3

#    Copyright (C) 2012-2017 Christian Thomas Jacobs.

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
from os.path import expanduser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from pyqso.adif import *
from pyqso.cabrillo import *
from pyqso.log import *
from pyqso.auxiliary_dialogs import *
from pyqso.log_name_dialog import LogNameDialog
from pyqso.record_dialog import RecordDialog
from pyqso.cabrillo_export_dialog import CabrilloExportDialog
from pyqso.summary import Summary
from pyqso.blank import Blank
from pyqso.printer import Printer
from pyqso.compare import compare_date_and_time, compare_default


class Logbook:

    """ A Logbook object can store multiple Log objects. """

    def __init__(self, application):
        """ Create a new Logbook object and initialise the list of Logs.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.application = application
        self.builder = self.application.builder
        self.notebook = self.builder.get_object("logbook")
        self.connection = None
        self.logs = []
        logging.debug("New Logbook instance created!")
        return

    def new(self, widget=None):
        """ Create a new logbook, and open it. """

        # Get the new file's path from a dialog.
        dialog = Gtk.FileChooserDialog("Create a New SQLite Database File",
                                       self.application.window,
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

        if(path is None):  # If the Cancel button has been clicked, path will still be None
            logging.debug("No file path specified.")
            return
        else:
            # Clear the contents of the file, in case the file exists already.
            open(path, 'w').close()
            # Open the new logbook, ready for use.
            self.open(path=path)
        return

    def open(self, widget=None, path=None):
        """ Open a logbook, and render all the logs within it.

        :arg str path: An optional argument containing the database file location, if already known. If this is None, a file selection dialog will appear.
        """

        if(path is None):
            # If no path has been provided, get one from a "File Open" dialog.
            dialog = Gtk.FileChooserDialog("Open SQLite Database File",
                                           self.application.window,
                                           Gtk.FileChooserAction.OPEN,
                                           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

            response = dialog.run()
            if(response == Gtk.ResponseType.OK):
                path = dialog.get_filename()
            dialog.destroy()

            if(path is None):  # If the Cancel button has been clicked, path will still be None
                logging.debug("No file path specified.")
                return

        connected = self.db_connect(path)
        if(connected):
            # If the connection setup was successful, then open all the logs in the database

            self.path = path

            logging.debug("Retrieving all the logs in the logbook...")
            self.logs = self.get_logs()
            if(not self.logs):
                error(parent=self.application.window, message="Could not open logbook. Something went wrong when trying to retrieve the logs. Perhaps the logbook file is encrypted, corrupted, or in the wrong format?")
                return
            else:
                logging.debug("All logs retrieved successfully.")

            logging.debug("Rendering logs...")
            # For rendering the logs. One treeview and one treeselection per Log.
            self.treeview = []
            self.treeselection = []
            self.sorter = []
            self.filter = []
            self.summary = Summary(self.application)
            self.blank = Blank(self.application)

            # FIXME: This is an unfortunate work-around. If the area around the "+/New Log" button
            # is clicked, PyQSO will change to an empty page. This signal is used to stop this from happening.
            self.notebook.connect("switch-page", self.on_switch_page)

            for i in range(len(self.logs)):
                self.render_log(i)
            logging.debug("All logs rendered successfully.")

            self.summary.update()
            self.application.toolbox.awards.count(self)

            context_id = self.application.statusbar.get_context_id("Status")
            self.application.statusbar.push(context_id, "Logbook: %s" % self.path)
            self.application.toolbar.set_logbook_button_sensitive(False)
            self.application.menu.set_logbook_item_sensitive(False)
            self.application.menu.set_log_items_sensitive(True)
            self.application.toolbar.filter_source.set_sensitive(True)

            self.notebook.show_all()

        else:
            logging.debug("Not connected to a logbook. No logs were opened.")

        return

    def close(self, widget=None):
        """ Close the logbook that is currently open. """

        disconnected = self.db_disconnect()
        if(disconnected):
            logging.debug("Closing all logs in the logbook...")
            while(self.notebook.get_n_pages() > 0):
                # Once a page is removed, the other pages get re-numbered,
                # so a 'for' loop isn't the best option here.
                self.notebook.remove_page(0)
            logging.debug("All logs now closed.")

            context_id = self.application.statusbar.get_context_id("Status")
            self.application.statusbar.push(context_id, "No logbook is currently open.")
            self.application.toolbar.set_logbook_button_sensitive(True)
            self.application.menu.set_logbook_item_sensitive(True)
            self.application.menu.set_log_items_sensitive(False)
            self.application.toolbar.filter_source.set_sensitive(False)
        else:
            logging.debug("Unable to disconnect from the database. No logs were closed.")
        return

    def db_connect(self, path):
        """ Create an SQL database connection to the Logbook's data source.

        :arg str path: The path of the database file.
        """

        logging.debug("Attempting to connect to the logbook database...")
        # Try setting up the SQL database connection
        try:
            self.db_disconnect()  # Destroy any existing connections first.
            self.connection = sqlite.connect(path)
            self.connection.row_factory = sqlite.Row
        except sqlite.Error as e:
            # PyQSO can't connect to the database.
            logging.exception(e)
            error(parent=self.application.window, message="PyQSO cannot connect to the database. Check file permissions?")
            return False

        logging.debug("Database connection created successfully!")
        return True

    def db_disconnect(self):
        """ Destroy the connection to the Logbook's data source.

        :returns: True if the connection was successfully destroyed, and False otherwise.
        :rtype: bool
        """

        logging.debug("Cleaning up any existing database connections...")
        if(self.connection):
            try:
                self.connection.close()
            except sqlite.Error as e:
                logging.exception(e)
                return False
        else:
            logging.debug("Already disconnected. Nothing to do here.")
        return True

    def on_switch_page(self, widget, label, new_page):
        """ Handle a tab/page change, and enable/disable the relevant Record-related buttons. """

        if(new_page == self.notebook.get_n_pages()-1):  # The last (right-most) tab is the "New Log" tab.
            self.notebook.stop_emission("switch-page")

        # Disable the record buttons if a log page is not selected.
        if(new_page == 0):
            self.application.toolbar.set_record_buttons_sensitive(False)
            self.application.menu.set_record_items_sensitive(False)
        else:
            self.application.toolbar.set_record_buttons_sensitive(True)
            self.application.menu.set_record_items_sensitive(True)
        return

    def new_log(self, widget=None):
        """ Create a new log in the logbook. """

        if(self.connection is None):
            return
        exists = True
        ln = LogNameDialog(self.application)
        while(exists):
            response = ln.dialog.run()
            if(response == Gtk.ResponseType.OK):
                log_name = ln.name
                try:
                    with self.connection:
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
                    error(parent=ln.dialog, message="Database error. Try another log name.")
                    exists = True
            else:
                ln.dialog.destroy()
                return

        ln.dialog.destroy()

        l = Log(self.connection, log_name)  # Empty log
        l.populate()

        self.logs.append(l)
        self.render_log(self.log_count-1)
        self.summary.update()

        self.notebook.set_current_page(self.log_count)
        return

    def delete_log(self, widget, page=None):
        """ Delete the log that is currently selected in the logbook.

        :arg Gtk.Widget page: An optional argument corresponding to the currently-selected page/tab.
        """
        if(self.connection is None):
            return

        if(page is None):
            page_index = self.notebook.get_current_page()  # Gets the index of the selected tab in the logbook
            if(page_index == 0):  # If we are on the Summary page...
                logging.debug("No log currently selected!")
                return
            else:
                page = self.notebook.get_nth_page(page_index)  # Gets the Gtk.VBox of the selected tab in the logbook

        log_index = self.get_log_index(name=page.get_name())
        log = self.logs[log_index]

        # We also need the page's index in order to remove it using remove_page below.
        # This may not be the same as what get_current_page() returns.
        page_index = self.notebook.page_num(page)

        if(page_index == 0 or page_index == self.notebook.get_n_pages()-1):  # Only the "New Log" tab is present (i.e. no actual logs in the logbook)
            logging.debug("No logs to delete!")
            return

        response = question(parent=self.application.window, message="Are you sure you want to delete log %s?" % log.name)
        if(response == Gtk.ResponseType.YES):
            try:
                with self.connection:
                    c = self.connection.cursor()
                    c.execute("DROP TABLE %s" % log.name)
            except sqlite.Error as e:
                logging.exception(e)
                error(parent=self.application.window, message="Database error. Could not delete the log.")
                return

            self.logs.pop(log_index)
            # Remove the log from the renderers too
            self.treeview.pop(log_index)
            self.treeselection.pop(log_index)
            self.sorter.pop(log_index)
            self.filter.pop(log_index)
            # And finally remove the tab in the Logbook
            self.notebook.remove_page(page_index)

        self.summary.update()
        self.application.toolbox.awards.count(self)
        return

    def filter_logs(self, widget=None):
        """ Re-filter all the logs when the user-defined expression is changed. """
        for i in range(0, len(self.filter)):
            self.filter[i].refilter()
        return

    def filter_by_callsign(self, model, iter, data):
        """ Filter all the logs in the logbook by the callsign field, based on a user-defined expression.

        :arg Gtk.TreeModel model: The model used to filter the log data.
        :arg Gtk.TreeIter iter: A pointer to a particular row in the model.
        :arg data: The user-defined expression to filter by.
        :returns: True if a record matches the expression, or if there is nothing to filter. Otherwise, returns False.
        :rtype: bool
        """
        value = model.get_value(iter, 1)
        callsign = self.application.toolbar.filter_source.get_text()

        if(callsign is None or callsign == ""):
            # If there is nothing to filter with, then show all the records!
            return True
        else:
            # This should be case insensitive.
            # Also, we could use value[:][0:len(callsign))] if we wanted to match from the very start of each callsign.
            return callsign.upper() in value or callsign.lower() in value

    def render_log(self, index):
        """ Render a Log in the Gtk.Notebook.

        :arg int index: The index of the Log (in the list of Logs) to render.
        """
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
        vbox.set_name(self.logs[index].name)  # Set a name for the tab itself so we can match it up with the associated Log object later.
        vbox.pack_start(sw, True, True, 0)

        # Add a close button to the tab
        hbox = Gtk.HBox(False, 0)
        label = Gtk.Label(self.logs[index].name)
        hbox.pack_start(label, False, False, 0)
        hbox.show_all()

        self.notebook.insert_page(vbox, hbox, index+1)  # Append the new log as a new tab

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

            # Special cases
            if(field_names[i] == "NOTES"):
                # Give the 'Notes' column some extra space, since this is likely to contain some long sentences...
                column.set_min_width(300)
                # ... but don't let it automatically re-size itself.
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)

            column.connect("clicked", self.sort_log, i+1)

            config = configparser.ConfigParser()
            have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])
            (section, option) = ("view", AVAILABLE_FIELD_NAMES_ORDERED[i].lower())
            if(have_config and config.has_option(section, option)):
                column.set_visible(config.get(section, option) == "True")
            self.treeview[index].append_column(column)

        self.notebook.show_all()
        return

    def sort_log(self, widget, column_index):
        """ Sort the log (that is currently selected) with respect to a given field.

        :arg int column_index: The index of the column to sort by.
        """

        log_index = self.get_log_index()
        column = self.treeview[log_index].get_column(column_index)

        if(AVAILABLE_FIELD_NAMES_ORDERED[column_index-1] == "QSO_DATE"):
            # If the field being sorted is the QSO_DATE, then also sort by the TIME_ON field so we get the
            # correct chronological order.
            # Note: This assumes that the TIME_ON field is always immediately to the right of the QSO_DATE field.
            self.sorter[log_index].set_sort_func(column_index, compare_date_and_time, user_data=[column_index, column_index+1])
        else:
            self.sorter[log_index].set_sort_func(column_index, compare_default, user_data=column_index)

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
        """ Rename the log that is currently selected. """
        if(self.connection is None):
            return
        page_index = self.notebook.get_current_page()
        if(page_index == 0):  # If we are on the Summary page...
            logging.debug("No log currently selected!")
            return
        page = self.notebook.get_nth_page(page_index)  # Gets the Gtk.VBox of the selected tab in the logbook.
        old_log_name = page.get_name()

        log_index = self.get_log_index(name=old_log_name)

        success = False
        ln = LogNameDialog(self.application, title="Rename Log", name=old_log_name)
        while(not success):
            response = ln.dialog.run()
            if(response == Gtk.ResponseType.OK):
                new_log_name = ln.name
                success = self.logs[log_index].rename(new_log_name)
                if(success):
                    ln.dialog.destroy()
                else:
                    # Unsuccessful rename attempt. Inform the user.
                    error(parent=ln.dialog, message="Database error. Try another log name.")
            else:
                ln.dialog.destroy()
                return

        # Remember to change the page's name ...
        page.set_name(new_log_name)

        # ... and update the tab's label.
        hbox = Gtk.HBox(False, 0)
        label = Gtk.Label(new_log_name)
        hbox.pack_start(label, False, False, 0)
        hbox.show_all()
        self.notebook.set_tab_label(page, hbox)

        # The number of logs will obviously stay the same, but
        # we want to update the logbook's modification date.
        self.summary.update()

        return

    def import_log(self, widget=None):
        """ Import a log from an ADIF file. """
        dialog = Gtk.FileChooserDialog("Import ADIF Log File",
                                       self.application.window,
                                       Gtk.FileChooserAction.OPEN,
                                      (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                       Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        filter = Gtk.FileFilter()
        filter.set_name("All ADIF files (*.adi, *.ADI)")
        filter.add_pattern("*.adi")
        filter.add_pattern("*.ADI")
        dialog.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
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

        ln = LogNameDialog(self.application, title="Import Log")
        while(True):
            response = ln.dialog.run()
            if(response == Gtk.ResponseType.OK):
                log_name = ln.name
                if(self.log_name_exists(log_name)):
                    # Import into existing log
                    exists = True
                    l = self.logs[self.get_log_index(name=log_name)]
                    response = question(parent=ln.dialog, message="Are you sure you want to import into an existing log?")
                    if(response == Gtk.ResponseType.YES):
                        break
                elif(self.log_name_exists(log_name) is None):
                    # Could not determine if the log name exists. It's safer to stop here than to try to add a new log.
                    error(parent=ln.dialog, message="Database error. Could not check if the log name exists.")
                    ln.dialog.destroy()
                    return
                else:
                    # Create a new log with the name the user supplies
                    exists = False
                    try:
                        with self.connection:
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
                        error(parent=ln.dialog, message="Database error. Try another log name.")
            else:
                ln.dialog.destroy()
                return

        ln.dialog.destroy()

        adif = ADIF()
        logging.debug("Importing records from the ADIF file with path: %s" % path)
        records = adif.read(path)
        l.add_record(records)
        l.populate()

        if(not exists):
            self.logs.append(l)
            self.render_log(self.log_count-1)
        self.summary.update()
        self.application.toolbox.awards.count(self)

        return

    def export_log_adif(self, widget=None):
        """ Export the log (that is currently selected) to an ADIF file. """
        page_index = self.notebook.get_current_page()  # Gets the index of the selected tab in the logbook
        if(page_index == 0):  # If we are on the Summary page...
            logging.debug("No log currently selected!")
            return

        log_index = self.get_log_index()
        log = self.logs[log_index]

        dialog = Gtk.FileChooserDialog("Export Log as ADIF",
                                       self.application.window,
                                       Gtk.FileChooserAction.SAVE,
                                      (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                       Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_do_overwrite_confirmation(True)

        filter = Gtk.FileFilter()
        filter.set_name("All ADIF files (*.adi, *.ADI)")
        filter.add_pattern("*.adi")
        filter.add_pattern("*.ADI")
        dialog.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

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
            records = log.records
            if(records is not None):
                adif.write(records, path)
            else:
                error(self.application.window, "Could not retrieve the records from the SQL database. No records have been exported.")
        return

    def export_log_cabrillo(self, widget=None):
        """ Export the log (that is currently selected) to a Cabrillo file. """
        page_index = self.notebook.get_current_page()  # Gets the index of the selected tab in the logbook
        if(page_index == 0):  # If we are on the Summary page...
            logging.debug("No log currently selected!")
            return

        log_index = self.get_log_index()
        log = self.logs[log_index]

        dialog = Gtk.FileChooserDialog("Export Log as Cabrillo",
                                       self.application.window,
                                       Gtk.FileChooserAction.SAVE,
                                      (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                       Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_do_overwrite_confirmation(True)

        filter = Gtk.FileFilter()
        filter.set_name("All Cabrillo files (*.log, *.LOG)")
        filter.add_pattern("*.log")
        filter.add_pattern("*.LOG")
        dialog.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        response = dialog.run()
        if(response == Gtk.ResponseType.OK):
            path = dialog.get_filename()
        else:
            path = None
        dialog.destroy()

        if(path is None):
            logging.debug("No file path specified.")
        else:
            # Get Cabrillo-specific fields, such as the callsign used during a contest and the contest's name.
            ced = CabrilloExportDialog(self.application)
            response = ced.dialog.run()
            if(response == Gtk.ResponseType.OK):
                contest = ced.contest
                mycall = ced.mycall
            else:
                ced.dialog.destroy()
                return
            ced.dialog.destroy()

            cabrillo = Cabrillo()
            records = log.records
            if(records is not None):
                cabrillo.write(records, path, contest=contest, mycall=mycall)
            else:
                error(self.application.window, "Could not retrieve the records from the SQL database. No records have been exported.")
        return

    def print_log(self, widget=None):
        """ Print all the records in the log (that is currently selected).
        Note that only a few important fields are printed because of the restricted width of the page. """
        page_index = self.notebook.get_current_page()  # Gets the index of the selected tab in the logbook
        if(page_index == 0):  # If we are on the Summary page...
            logging.debug("No log currently selected!")
            return
        log_index = self.get_log_index()
        log = self.logs[log_index]
        records = log.records
        if(records is not None):
            printer = Printer(self.application)
            printer.print_records(records)
        else:
            error(self.application.window, "Could not retrieve the records from the SQL database. No records have been printed.")
        return

    def add_record_callback(self, widget):
        """ A callback function used to add a particular record/QSO. """
        # Get the log index
        try:
            log_index = self.get_log_index()
            if(log_index is None):
                raise ValueError("The log index could not be determined. Perhaps you tried adding a record when the Summary page was selected?")
        except ValueError as e:
            error(self.application.window, e)
            return
        log = self.logs[log_index]

        # Keep the dialog open after adding a record?
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])
        (section, option) = ("general", "keep_open")
        if(have_config and config.has_option(section, option)):
            keep_open = config.get("general", "keep_open") == "True"
        else:
            keep_open = False
        adif = ADIF()

        exit = False
        while not exit:
            rd = RecordDialog(application=self.application, log=log, index=None)

            all_valid = False  # Are all the field entries valid?

            # Shall we exit the while loop (and therefore close the Add Record dialog)?
            if keep_open:
                exit = False
            else:
                exit = True

            while not all_valid:
                # This while loop gives the user infinite attempts at giving valid data.
                # The add/edit record window will stay open until the user gives valid data,
                # or until the Cancel button is clicked.
                all_valid = True
                response = rd.dialog.run()
                if(response == Gtk.ResponseType.OK):
                    fields_and_data = {}
                    field_names = AVAILABLE_FIELD_NAMES_ORDERED
                    for i in range(0, len(field_names)):
                        # Validate user input.
                        fields_and_data[field_names[i]] = rd.get_data(field_names[i])
                        if(not(adif.is_valid(field_names[i], fields_and_data[field_names[i]], AVAILABLE_FIELD_NAMES_TYPES[field_names[i]]))):
                            # Data is not valid - inform the user.
                            error(parent=rd.dialog, message="The data in field \"%s\" is not valid!" % field_names[i])
                            all_valid = False
                            break  # Don't check the other data until the user has fixed the current one.

                    if(all_valid):
                        # All data has been validated, so we can go ahead and add the new record.
                        log.add_record(fields_and_data)
                        self.summary.update()
                        self.application.toolbox.awards.count(self)
                        # Select the new Record's row in the treeview.
                        record_count = log.record_count
                        if(record_count is not None):
                            self.treeselection[log_index].select_path(record_count)
                else:
                    exit = True
                    break
            rd.dialog.destroy()
        return

    def delete_record_callback(self, widget):
        """ A callback function used to delete a particular record/QSO. """

        # Get the log index
        try:
            log_index = self.get_log_index()
            if(log_index is None):
                raise ValueError("The log index could not be determined. Perhaps you tried deleting a record when the Summary page was selected?")
        except ValueError as e:
            error(self.application, e)
            return
        log = self.logs[log_index]

        (sort_model, path) = self.treeselection[log_index].get_selected_rows()  # Get the selected row in the log
        try:
            sort_iter = sort_model.get_iter(path[0])
            filter_iter = self.sorter[log_index].convert_iter_to_child_iter(sort_iter)
            # ...and the ListStore model (i.e. the log) is a child of the filter model.
            child_iter = self.filter[log_index].convert_iter_to_child_iter(filter_iter)
            row_index = log.get_value(child_iter, 0)
        except IndexError:
            logging.debug("Trying to delete a record, but there are no records in the log!")
            return

        response = question(parent=self.application.window, message="Are you sure you want to delete record %d?" % row_index)
        if(response == Gtk.ResponseType.YES):
            # Deletes the record with index 'row_index' from the Records list.
            # 'iter' is needed to remove the record from the ListStore itself.
            log.delete_record(row_index, iter=child_iter)
            self.summary.update()
            self.application.toolbox.awards.count(self)
        return

    def edit_record_callback(self, widget, path, view_column):
        """ A callback function used to edit a particular record/QSO.
        Note that the widget, path and view_column arguments are not used,
        but need to be passed in since they associated with the row-activated signal
        which is generated when the user double-clicks on a record. """

        # Get the log index
        try:
            log_index = self.get_log_index()
            if(log_index is None):
                raise ValueError("The log index could not be determined. Perhaps you tried editing a record when the Summary page was selected?")
        except ValueError as e:
            error(self.application, e)
            return
        log = self.logs[log_index]

        (sort_model, path) = self.treeselection[log_index].get_selected_rows()  # Get the selected row in the log
        try:
            sort_iter = sort_model.get_iter(path[0])
            filter_iter = self.sorter[log_index].convert_iter_to_child_iter(sort_iter)
            # ...and the ListStore model (i.e. the log) is a child of the filter model.
            child_iter = self.filter[log_index].convert_iter_to_child_iter(filter_iter)
            row_index = log.get_value(child_iter, 0)
        except IndexError:
            logging.debug("Could not find the selected row's index!")
            return

        rd = RecordDialog(application=self.application, log=self.logs[log_index], index=row_index)
        all_valid = False  # Are all the field entries valid?

        adif = ADIF()
        while(not all_valid):
            # This while loop gives the user infinite attempts at giving valid data.
            # The add/edit record window will stay open until the user gives valid data,
            # or until the Cancel button is clicked.
            all_valid = True
            response = rd.dialog.run()
            if(response == Gtk.ResponseType.OK):
                fields_and_data = {}
                field_names = AVAILABLE_FIELD_NAMES_ORDERED
                for i in range(0, len(field_names)):
                    # Validate user input.
                    fields_and_data[field_names[i]] = rd.get_data(field_names[i])
                    if(not(adif.is_valid(field_names[i], fields_and_data[field_names[i]], AVAILABLE_FIELD_NAMES_TYPES[field_names[i]]))):
                        # Data is not valid - inform the user.
                        error(parent=rd.dialog, message="The data in field \"%s\" is not valid!" % field_names[i])
                        all_valid = False
                        break  # Don't check the other fields until the user has fixed the current field's data.

                if(all_valid):
                    # All data has been validated, so we can go ahead and update the record.
                    record = log.get_record_by_index(row_index)
                    if(record is None):
                        message = "Could not retrieve record with row_index %d from the SQL database. The record has not been edited." % row_index
                        logging.error(message)
                        error(parent=rd.dialog, message=message)
                    else:
                        for i in range(0, len(field_names)):
                            # Check whether the data has actually changed. Database updates can be expensive.
                            if(record[field_names[i].lower()] != fields_and_data[field_names[i]]):
                                # Update the record in the database and then in the ListStore.
                                # We add 1 onto the column_index here because we don't want to consider the index column.
                                log.edit_record(row_index, field_names[i], fields_and_data[field_names[i]], iter=child_iter, column_index=i+1)
                        self.summary.update()
                        self.application.toolbox.awards.count(self)

        rd.dialog.destroy()
        return

    def remove_duplicates_callback(self, widget=None):
        """ Remove duplicate records in a log.
        Detecting duplicate records is done based on the CALL, QSO_DATE, TIME_ON, FREQ, and MODE fields. """
        logging.debug("Removing duplicate records...")

        log_index = self.get_log_index()
        log = self.logs[log_index]

        (number_of_duplicates, number_of_duplicates_removed) = log.remove_duplicates()
        info(self.application.window, "Found %d duplicate(s). Successfully removed %d duplicate(s)." % (number_of_duplicates, number_of_duplicates_removed))
        return

    @property
    def log_count(self):
        """ Return the total number of logs in the logbook.

        :returns: The total number of logs in the logbook.
        :rtype: int
        """
        return len(self.logs)

    @property
    def record_count(self):
        """ Return the total number of QSOs/records in the whole logbook.

        :returns: The total number of QSOs/records in the whole logbook.
        :rtype: int
        """
        return sum([log.record_count for log in self.logs])

    def log_name_exists(self, table_name):
        """ Determine whether a Log object with a given name exists in the SQL database.

        :arg str table_name: The name of the log (i.e. the name of the table in the SQL database).
        :returns: True if the log name already exists in the logbook; False if it does not already exist; None if there is a database error.
        :rtype: bool or None
        """
        try:
            with self.connection:
                c = self.connection.cursor()
                c.execute("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE name=?)", [table_name])
                exists = c.fetchone()
            if(exists[0] == 1):
                return True
            else:
                return False
        except (sqlite.Error, IndexError) as e:
            logging.exception(e)  # Database error. PyQSO could not check if the log name exists.
            return None

    def get_log_index(self, name=None):
        """ Given the name of a log, return its index in the list of Log objects.

        :arg str name: The name of the log. If None, use the name of the currently-selected log.
        :returns: The index of the named log in the list of Log objects.
        :rtype: int
        """
        if(name is None):
            # If no page name is supplied, then just use the currently selected page
            page_index = self.notebook.get_current_page()  # Gets the index of the selected tab in the logbook
            if(page_index == 0 or page_index == self.notebook.get_n_pages()-1):
                # We either have the Summary page, or the "+" (add log) blank/dummy page.
                logging.debug("No log currently selected!")
                return None
            name = self.notebook.get_nth_page(page_index).get_name()
        # If a page of the logbook (and therefore a Log object) gets deleted,
        # then the page_index may not correspond to the index of the log in the self.logs list.
        # Therefore, we have to search for the tab with the same name as the log.
        for i in range(0, len(self.logs)):
            if(self.logs[i].name == name):
                log_index = i
                break
        return log_index

    def get_logs(self):
        """ Retrieve all the logs in the logbook file, and create Log objects that represent them.

        :returns: A list containing all the logs in the logbook, or None if the retrieval was unsuccessful.
        :rtype: list
        """
        logs = []  # A fresh stack of Log objects
        try:
            with self.connection:
                c = self.connection.cursor()
                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT GLOB 'sqlite_*'")
                for name in c:
                    l = Log(self.connection, name[0])
                    l.populate()
                    logs.append(l)
        except (sqlite.Error, IndexError) as e:
            logging.exception(e)
            return None
        return logs
