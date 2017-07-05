#!/usr/bin/env python3

#    Copyright (C) 2017 Christian Thomas Jacobs.

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

import os


class TelnetConnectionDialog:

    """ A handler for the Gtk.Dialog through which a user can specify Telnet connection details. """

    def __init__(self, application):
        """ Create and show the Telnet connection dialog to the user.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.builder = application.builder
        glade_file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir, "res", "pyqso.glade")
        self.builder.add_objects_from_file(glade_file_path, ("telnet_connection_dialog",))
        self.dialog = self.builder.get_object("telnet_connection_dialog")
        self.sources = {"HOST": self.builder.get_object("host_entry"),
                        "PORT": self.builder.get_object("port_entry"),
                        "USERNAME": self.builder.get_object("username_entry"),
                        "PASSWORD": self.builder.get_object("password_entry"),
                        "BOOKMARK": self.builder.get_object("bookmark_checkbox")}

        self.dialog.show_all()

        return

    @property
    def host(self):
        """ Return the Telnet server's host name.

        :returns: The server's host name.
        :rtype: str
        """
        return self.sources["HOST"].get_text()

    @property
    def port(self):
        """ Return the Telnet server's port number (as a string).

        :returns: The server's port number (as a string).
        :rtype: str
        """
        return self.sources["PORT"].get_text()

    @property
    def username(self):
        """ Return the user's username.

        :returns: The user's username.
        :rtype: str
        """
        return self.sources["USERNAME"].get_text()

    @property
    def password(self):
        """ Return the user's password.

        :returns: The user's password.
        :rtype: str
        """
        return self.sources["PASSWORD"].get_text()

    @property
    def bookmark(self):
        """ Return True if a new bookmark should be created, otherwise return False.

        :returns: True if a new bookmark should be created, otherwise False.
        :rtype: bool
        """
        return self.sources["BOOKMARK"].get_active()
