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
import os.path


class LogNameDialog:

    """ A handler for the Gtk.Dialog through which a user can specify the name of a Log object. """

    def __init__(self, builder, title=None, name=None):
        """ Create and show the log name dialog to the user.

        :arg title: The title of the dialog. If this is None, it is assumed that a new log is going to be created.
        :arg name: The existing name of the Log object. Defaults to None if not specified (because the Log does not yet exist).
        """

        logging.debug("Building new log name dialog...")

        self.builder = builder
        self.builder.add_objects_from_file(os.path.abspath(os.path.dirname(__file__)) + "/glade/pyqso.glade", ("log_name_dialog",))
        self.dialog = self.builder.get_object("log_name_dialog")

        if(title is None):
            self.dialog.set_title("New Log")
        else:
            self.dialog.set_title(title)

        self.entry = self.builder.get_object("log_name_entry")
        if(name is not None):
            self.entry.set_text(name)

        self.dialog.show_all()

        logging.debug("Log name dialog built.")

        return

    @property
    def name(self):
        """ Return the log name specified in the Gtk.Entry box by the user.

        :returns: The log's name.
        :rtype: str
        """
        return self.entry.get_text()
