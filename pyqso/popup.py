#!/usr/bin/env python3

#    Copyright (C) 2018 Christian Thomas Jacobs.

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


class Popup:

    """ The popup menu that appears when a QSO record is right-clicked. """

    def __init__(self, application):
        """ Set up popup menu items. """

        self.application = application
        self.builder = self.application.builder

        self.menu = self.builder.get_object("popup")

        # Collect Gtk menu items and connect signals.
        self.items = {}

        # Plot selected QSO on the world map.
        self.items["PINPOINT"] = self.builder.get_object("mitem_pinpoint")
        self.items["PINPOINT"].connect("activate", self.application.logbook.pinpoint_callback)

        self.items["COPY"] = self.builder.get_object("mitem_copy")
        self.items["COPY"].connect("activate", self.application.logbook.copy_callback)

        self.items["PASTE"] = self.builder.get_object("mitem_paste")
        self.items["PASTE"].connect("activate", self.application.logbook.paste_callback)
