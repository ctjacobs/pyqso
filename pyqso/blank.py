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

from gi.repository import Gtk


class Blank(object):
    def __init__(self, application):
        """ Create a blank page in the Gtk.Notebook for the "+" (New Log) tab.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.application = application

        blank_treeview = Gtk.TreeView()

        # Allow the Log to be scrolled up/down
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(blank_treeview)
        page = Gtk.VBox()
        page.pack_start(sw, True, True, 0)

        # Add a "+" button to the tab
        tab = Gtk.HBox(False, 0)
        icon = Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.connect("clicked", self.application.logbook.new_log)
        button.add(icon)
        button.set_tooltip_text('New Log')
        tab.pack_start(button, False, False, 0)

        tab.show_all()
        page.show_all()

        self.application.logbook.notebook.insert_page(page, tab, 1)
        self.application.logbook.notebook.set_current_page(0)

        return
