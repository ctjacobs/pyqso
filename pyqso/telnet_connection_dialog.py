#!/usr/bin/env python3

#    Copyright (C) 2013 Christian T. Jacobs.

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

class TelnetConnectionDialog(Gtk.Dialog):
   """ A simple dialog through which users can specify host and login information for a Telnet server. 
   This can be used to connect to DX clusters. """
   
   def __init__(self, parent):
      """ Set up and show the Telnet connection dialog to the user.
      
      :arg parent: The parent Gtk window/dialog.
      """

      logging.debug("Setting up the Telnet connection dialog...")
      
      Gtk.Dialog.__init__(self, title="New Telnet Connection", parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

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
      self.sources["PASSWORD"].set_visibility(False) # Mask the password with the "*" character.
      hbox_temp.pack_start(self.sources["PASSWORD"], True, True, 6)
      self.vbox.pack_start(hbox_temp, False, False, 6)

      logging.debug("Telnet connection dialog ready!") 

      self.show_all()
      return

   def get_connection_info(self):
      """ Return the host and login information stored in the Gtk.Entry boxes.
      
      :returns: A dictionary of Telnet connection-related information (username, password, port, host).
      :rtype: dict
      """
      logging.debug("Returning Telnet connection information...") 
      return self.sources


