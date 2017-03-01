#!/usr/bin/env python3

#    Copyright (C) 2012-2017 Christian T. Jacobs.

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
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os.path


class Menu:

    """ The PyQSO menu bar along the top of the main window. """

    def __init__(self, parent):
        """ Set up all menu items and connect to the various functions.

        :arg parent: The parent Gtk window.
        :arg builder: The Gtk builder.
        """

        logging.debug("Setting up the menu bar...")

        self.parent = parent
        self.builder = parent.builder

        # Collect Gtk menu items and connect signals.
        self.items = {}

        # New logbook
        self.items["NEW_LOGBOOK"] = self.builder.get_object("mitem_new_logbook")
        self.items["NEW_LOGBOOK"].connect("activate", parent.logbook.new)

        # Open logbook
        self.items["OPEN_LOGBOOK"] = self.builder.get_object("mitem_open_logbook")
        self.items["OPEN_LOGBOOK"].connect("activate", parent.logbook.open)

        # Close logbook
        self.items["CLOSE_LOGBOOK"] = self.builder.get_object("mitem_close_logbook")
        self.items["CLOSE_LOGBOOK"].connect("activate", parent.logbook.close)

        # New log
        self.items["NEW_LOG"] = self.builder.get_object("mitem_new_log")
        self.items["NEW_LOG"].connect("activate", parent.logbook.new_log)

        # Delete the current log
        self.items["DELETE_LOG"] = self.builder.get_object("mitem_delete_log")
        self.items["DELETE_LOG"].connect("activate", parent.logbook.delete_log)

        # Rename the current log
        self.items["RENAME_LOG"] = self.builder.get_object("mitem_rename_log")
        self.items["RENAME_LOG"].connect("activate", parent.logbook.rename_log)

        # Import log
        self.items["IMPORT_LOG"] = self.builder.get_object("mitem_import_log")
        self.items["IMPORT_LOG"].connect("activate", parent.logbook.import_log)

        # Export the current log
        self.items["EXPORT_LOG"] = self.builder.get_object("mitem_export_log")
        self.items["EXPORT_LOG"].connect("activate", parent.logbook.export_log)

        # Print log
        self.items["PRINT_LOG"] = self.builder.get_object("mitem_print_log")
        self.items["PRINT_LOG"].connect("activate", parent.logbook.print_log)

        # Quit
        self.items["QUIT"] = self.builder.get_object("mitem_quit")
        self.items["QUIT"].connect("activate", Gtk.main_quit)

        # Add record
        self.items["ADD_RECORD"] = self.builder.get_object("mitem_add_record")
        self.items["ADD_RECORD"].connect("activate", parent.logbook.add_record_callback)

        # Edit selected record
        self.items["EDIT_RECORD"] = self.builder.get_object("mitem_edit_record")
        self.items["EDIT_RECORD"].connect("activate", parent.logbook.edit_record_callback)

        # Delete selected record
        self.items["DELETE_RECORD"] = self.builder.get_object("mitem_delete_record")
        self.items["DELETE_RECORD"].connect("activate", parent.logbook.delete_record_callback)

        # Remove duplicates
        self.items["REMOVE_DUPLICATES"] = self.builder.get_object("mitem_remove_duplicates")
        self.items["REMOVE_DUPLICATES"].connect("activate", parent.logbook.remove_duplicates_callback)

        # View toolbox
        self.items["TOOLBOX"] = self.builder.get_object("mitem_toolbox")
        config = configparser.ConfigParser()
        have_config = (config.read(os.path.expanduser('~/.config/pyqso/preferences.ini')) != [])
        (section, option) = ("general", "show_toolbox")
        if(have_config and config.has_option(section, option)):
            self.items["TOOLBOX"].set_active(config.get(section, option) == "True")
        else:
            self.items["TOOLBOX"].set_active(False)  # Don't show the toolbox by default
        self.items["TOOLBOX"].connect("activate", parent.toolbox.toggle_visible_callback)

        # Preferences
        self.items["PREFERENCES"] = self.builder.get_object("mitem_preferences")
        self.items["PREFERENCES"].connect("activate", parent.show_preferences)

        # About
        self.items["ABOUT"] = self.builder.get_object("mitem_about")
        self.items["ABOUT"].connect("activate", parent.show_about)

        self.set_logbook_item_sensitive(True)
        self.set_log_items_sensitive(False)
        self.set_record_items_sensitive(False)

        logging.debug("Menu bar ready!")

        return

    def set_logbook_item_sensitive(self, sensitive):
        """ Enable/disable logbook-related menu items.

        :arg bool sensitive: If True, enable the 'new logbook' and 'open logbook' menu items. If False, disable them.
        """
        logging.debug("Setting the 'Create/Open Logbook' menu item's sensitivity to: %s..." % sensitive)
        self.items["NEW_LOGBOOK"].set_sensitive(sensitive)
        self.items["OPEN_LOGBOOK"].set_sensitive(sensitive)
        self.items["CLOSE_LOGBOOK"].set_sensitive(not sensitive)
        logging.debug("Set the 'Create/Open Logbook' menu item's sensitivity to: %s." % sensitive)
        return

    def set_log_items_sensitive(self, sensitive):
        """ Enable/disable log-related menu items.

        :arg bool sensitive: If True, enable all the log-related menu items. If False, disable them all.
        """
        logging.debug("Setting log-related menu item sensitivity to: %s..." % sensitive)
        for item_name in ["NEW_LOG", "DELETE_LOG", "RENAME_LOG", "IMPORT_LOG", "EXPORT_LOG", "PRINT_LOG"]:
            self.items[item_name].set_sensitive(sensitive)
        logging.debug("Set log-related menu item sensitivity to: %s." % sensitive)
        return

    def set_record_items_sensitive(self, sensitive):
        """ Enable/disable record-related menu items.

        :arg bool sensitive: If True, enable all the record-related menu items. If False, disable them all.
        """
        logging.debug("Setting record-related menu item sensitivity to: %s..." % sensitive)
        for item_name in ["ADD_RECORD", "EDIT_RECORD", "DELETE_RECORD", "REMOVE_DUPLICATES"]:
            self.items[item_name].set_sensitive(sensitive)
        logging.debug("Set record-related menu item sensitivity to: %s." % sensitive)
        return
