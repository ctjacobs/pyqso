#!/usr/bin/env python3

#    Copyright (C) 2019 Christian Thomas Jacobs.

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


class UpdateModesDialog:

    """ A handler for the Gtk.Dialog through which a user can specify a URL to an ADIF specification. """

    def __init__(self, application):
        """ Create and show the dialog to the user.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.builder = application.builder
        glade_file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "res", "pyqso.glade")
        self.builder.add_objects_from_file(glade_file_path, ("update_modes_dialog",))
        self.dialog = self.builder.get_object("update_modes_dialog")
        self.sources = {"URL": self.builder.get_object("adif_url_entry")}

        self.dialog.show_all()

        return

    @property
    def url(self):
        """ Return the URL of the ADIF specification's webpage.

        :returns: The URL of the ADIF specification's webpage.
        :rtype: str
        """
        return self.sources["URL"].get_text()

