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

from pyqso.dx_cluster import *
from pyqso.grey_line import *
from pyqso.awards import *


class Toolbox:

    """ Contains a Gtk.Notebook full of amateur radio-related tools. """

    def __init__(self, parent, builder):
        """ Instantiate and insert the various tools into the toolbox.

        :arg parent: The parent Gtk window.
        :arg builder: The Gtk builder."""

        logging.debug("Setting up the toolbox...")

        self.parent = parent
        self.builder = builder

        self.tools = self.builder.get_object("tools")

        self.dx_cluster = DXCluster(self.parent, self.builder)
        self.grey_line = GreyLine(self.parent, self.builder)
        #self.awards = Awards(self.parent, self.builder)
                      
        self.tools.connect_after("switch-page", self._on_switch_page)

        logging.debug("Toolbox ready!")

        return

    def toggle_visible_callback(self, widget=None):
        """ Show/hide the toolbox. """
        self.set_visible(not self.get_visible())
        return

    def _on_switch_page(self, widget, label, new_page):
        """ Re-draw the Grey Line if the user switches to the grey line tab. """
        if(isinstance(label, GreyLine)):
            label.draw()  # Note that 'label' is actually a GreyLine object.
        return
