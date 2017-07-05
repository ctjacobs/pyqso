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

import logging
import os.path


class CalendarDialog:

    """ Handler for a simple dialog containing a Gtk.Calendar widget. Using this ensures the date is in the correct YYYYMMDD format required by ADIF. """

    def __init__(self, application):
        """ Set up the calendar widget and show it to the user.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.builder = application.builder
        glade_file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "res", "pyqso.glade")
        self.builder.add_objects_from_file(glade_file_path, ("calendar_dialog",))
        self.dialog = self.builder.get_object("calendar_dialog")
        self.calendar = self.builder.get_object("calendar")
        self.dialog.show_all()

        return

    @property
    def date(self):
        """ Return the date from the Gtk.Calendar widget in YYYYMMDD format.

        :returns: The date from the calendar in YYYYMMDD format.
        :rtype: str
        """
        logging.debug("Retrieving the date from the calendar...")
        (year, month, day) = self.calendar.get_date()
        # If necessary, add on leading zeros so the YYYYMMDD format is followed.
        if(month + 1 < 10):
            month = "0" + str(month + 1)  # Note: the months start from an index of 0 when retrieved from the calendar widget.
        else:
            month += 1
        if(day < 10):
            day = "0" + str(day)
        date = str(year) + str(month) + str(day)
        return date
