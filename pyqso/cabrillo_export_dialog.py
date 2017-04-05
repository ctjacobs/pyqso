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
import logging


class CabrilloExportDialog:

    """ A handler for the Gtk.Dialog through which a user can specify Cabrillo log details. """

    def __init__(self, application):
        """ Create and show the Cabrillo export dialog to the user.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        logging.debug("Building new Cabrillo export dialog...")

        self.builder = application.builder
        glade_file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir, "res/pyqso.glade")
        self.builder.add_objects_from_file(glade_file_path, ("cabrillo_export_dialog",))
        self.dialog = self.builder.get_object("cabrillo_export_dialog")

        self.contest_combo = self.builder.get_object("cabrillo_export_contest_combo")
        self.mycall_entry = self.builder.get_object("cabrillo_export_mycall_entry")
        for contest in CONTESTS:
            self.contest_combo.append_text(contest)

        self.dialog.show_all()

        logging.debug("Cabrillo export dialog built.")

        return

    @property
    def contest(self):
        """ Return the name of the contest.

        :returns: The name of the contest.
        :rtype: str
        """
        return self.contest_combo.get_active_text()

    @property
    def mycall(self):
        """ Return the callsign used during the contest.

        :returns: The callsign used during the contest.
        :rtype: str
        """
        return self.mycall_entry.get_text()
