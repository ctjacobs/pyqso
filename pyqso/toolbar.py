#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian T. Jacobs.

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


class Toolbar:

    """ The toolbar underneath the menu bar. """

    def __init__(self, parent):
        """ Set up the various buttons in the toolbar, and connect to their corresponding functions. """

        logging.debug("Setting up the toolbar...")

        self.buttons = {}

        # Create logbook
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_NEW, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(icon)
        button.set_tooltip_text('Create a New Logbook')
        button.connect("clicked", parent.logbook.new)
        self.pack_start(button, False, False, 0)
        self.buttons["NEW_LOGBOOK"] = button

        # Open logbook
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(icon)
        button.set_tooltip_text('Open an Existing Logbook')
        button.connect("clicked", parent.logbook.open)
        self.pack_start(button, False, False, 0)
        self.buttons["OPEN_LOGBOOK"] = button

        # Close logbook
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(icon)
        button.set_tooltip_text('Close Logbook')
        button.connect("clicked", parent.logbook.close)
        self.pack_start(button, False, False, 0)
        self.buttons["CLOSE_LOGBOOK"] = button

        self.pack_start(Gtk.SeparatorToolItem(), False, False, 0)

        # Add record
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(icon)
        button.set_tooltip_text('Add Record')
        button.connect("clicked", parent.logbook.add_record_callback)
        self.pack_start(button, False, False, 0)
        self.buttons["ADD_RECORD"] = button

        # Edit record
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_EDIT, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(icon)
        button.set_tooltip_text('Edit Record')
        button.connect("clicked", parent.logbook.edit_record_callback, None, None)
        self.pack_start(button, False, False, 0)
        self.buttons["EDIT_RECORD"] = button

        # Delete record
        icon = Gtk.Image()
        icon.set_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.add(icon)
        button.set_tooltip_text('Delete Record')
        button.connect("clicked", parent.logbook.delete_record_callback)
        self.pack_start(button, False, False, 0)
        self.buttons["DELETE_RECORD"] = button

        self.pack_start(Gtk.SeparatorToolItem(), False, False, 0)

        # Filter log
        label = Gtk.Label("Filter by callsign: ")
        self.pack_start(label, False, False, 0)
        self.filter_source = Gtk.Entry()
        self.filter_source.set_width_chars(11)
        self.filter_source.connect_after("changed", parent.logbook.filter_logs)
        self.pack_start(self.filter_source, False, False, 0)

        self.set_logbook_button_sensitive(True)
        self.set_record_buttons_sensitive(False)

        self.filter_source.set_sensitive(False)

        logging.debug("Toolbar ready!")

        return

    def set_logbook_button_sensitive(self, sensitive):
        """ Enable/disable logbook-related toolbar items.

        :arg bool sensitive: If True, enable the 'new logbook' and 'open logbook' toolbar items. If False, disable them.
        """
        logging.debug("Setting logbook-related toolbar item sensitivity to: %s..." % sensitive)
        self.buttons["NEW_LOGBOOK"].set_sensitive(sensitive)
        self.buttons["OPEN_LOGBOOK"].set_sensitive(sensitive)
        self.buttons["CLOSE_LOGBOOK"].set_sensitive(not sensitive)
        logging.debug("Set logbook-related toolbar item sensitivity to: %s." % sensitive)
        return

    def set_record_buttons_sensitive(self, sensitive):
        """ Enable/disable record-related toolbar items.

        :arg bool sensitive: If True, enable all the record-related toolbar items. If False, disable them all.
        """
        logging.debug("Setting record-related toolbar item sensitivity to: %s..." % sensitive)
        for button_name in ["ADD_RECORD", "EDIT_RECORD", "DELETE_RECORD"]:
            self.buttons[button_name].set_sensitive(sensitive)
        logging.debug("Set record-related toolbar item sensitivity to: %s." % sensitive)
        return
