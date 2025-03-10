#!/usr/bin/env python3

#    Copyright (C) 2013-2018 Christian Thomas Jacobs.

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

from pyqso.dx_cluster import DXCluster
from pyqso.world_map import WorldMap
from pyqso.awards import Awards


class Toolbox:

    """ Contains a Gtk.Notebook full of amateur radio-related tools. """

    def __init__(self, application):
        """ Instantiate and insert the various tools into the toolbox.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.application = application
        self.builder = self.application.builder

        self.tools = self.builder.get_object("tools")

        self.dx_cluster = DXCluster(self.application)
        self.world_map = WorldMap(self.application)
        self.awards = Awards(self.application)

        self.tools.connect_after("switch-page", self.on_switch_page)

    def toggle_visible_callback(self, widget=None):
        """ Show/hide the toolbox. """
        toolbox_frame = self.builder.get_object("toolbox")
        toolbox_frame.set_visible(not toolbox_frame.get_visible())

    def on_switch_page(self, widget, label, new_page):
        """ Re-draw the WorldMap if the user switches to the World Map tab. """
        if widget.get_tab_label(label).get_text() == "World Map":
            self.world_map.draw()
