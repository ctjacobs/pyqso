#!/usr/bin/env python
# File: telnet_connection_dialog.py

#    Copyright (C) 2013 Christian Jacobs.

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

from gi.repository import Gtk, GObject
import logging
import re
import calendar

class TelnetConnectionDialog(Gtk.Dialog):
   
   def __init__(self, root_window):
      logging.debug("New TelnetConnectionDialog instance created!")
      
      Gtk.Dialog.__init__(self, title="New Telnet Connection", parent=root_window, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      self.sources = {}

      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label("Host: ", halign=Gtk.Align.START)
      label.set_width_chars(12)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["HOST"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["HOST"], True, True, 6)
      self.vbox.pack_start(hbox_temp, False, False, 6)

      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label("Port: ", halign=Gtk.Align.START)
      label.set_width_chars(12)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["PORT"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["PORT"], True, True, 6)
      self.vbox.pack_start(hbox_temp, False, False, 6)

      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label("Username: ", halign=Gtk.Align.START)
      label.set_width_chars(12)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["USERNAME"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["USERNAME"], True, True, 6)
      self.vbox.pack_start(hbox_temp, False, False, 6)

      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label("Password: ", halign=Gtk.Align.START)
      label.set_width_chars(12)
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.sources["PASSWORD"] = Gtk.Entry()
      hbox_temp.pack_start(self.sources["PASSWORD"], True, True, 6)
      self.vbox.pack_start(hbox_temp, False, False, 6)

      self.show_all()
      return

   def get_connection_info(self):
      return self.sources


