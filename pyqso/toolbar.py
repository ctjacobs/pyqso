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

import logging


class Toolbar:

    """ The toolbar underneath the menu bar. """

    def __init__(self, parent, builder):
        """ Set up the various buttons in the toolbar, and connect to their corresponding functions. """

        logging.debug("Setting up the toolbar...")

        self.parent = parent
        self.builder = builder

        self.buttons = {}

        # Create logbook
        self.buttons["NEW_LOGBOOK"] = self.builder.get_object("toolbar_new_logbook")
        self.buttons["NEW_LOGBOOK"].connect("clicked", parent.logbook.new)

        # Open logbook
        self.buttons["OPEN_LOGBOOK"] = self.builder.get_object("toolbar_open_logbook")
        self.buttons["OPEN_LOGBOOK"].connect("clicked", parent.logbook.open)

        # Close logbook
        self.buttons["CLOSE_LOGBOOK"] = self.builder.get_object("toolbar_close_logbook")
        self.buttons["CLOSE_LOGBOOK"].connect("clicked", parent.logbook.close)

        # Add record
        self.buttons["ADD_RECORD"] = self.builder.get_object("toolbar_add_record")
        self.buttons["ADD_RECORD"].connect("clicked", parent.logbook.add_record_callback)

        # Edit record
        self.buttons["EDIT_RECORD"] = self.builder.get_object("toolbar_edit_record")
        self.buttons["EDIT_RECORD"].connect("clicked", parent.logbook.edit_record_callback, None, None)

        # Delete record
        self.buttons["DELETE_RECORD"] = self.builder.get_object("toolbar_delete_record")
        self.buttons["DELETE_RECORD"].connect("clicked", parent.logbook.delete_record_callback)

        # Filter log
        self.buttons["DELETE_RECORD"] = self.builder.get_object("toolbar_delete_record")
        self.buttons["DELETE_RECORD"].connect("clicked", parent.logbook.delete_record_callback)

        self.filter_source = self.builder.get_object("filter_source")
        self.filter_source.connect_after("changed", parent.logbook.filter_logs)

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
