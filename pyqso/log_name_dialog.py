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

class LogNameDialog(Gtk.Dialog):
   """ A Gtk.Dialog where a user can specify the name of a Log object. """
   
   def __init__(self, parent, title=None, name=None):
      """ Create and show the log name dialog to the user.
      
      :arg parent: The parent Gtk window.
      :arg title: The title of the dialog. If this is None, it is assumed that a new log is going to be created.
      :arg name: The existing name of the Log object. Defaults to None if not specified (because the Log does not yet exist).
      """

      if(title is None):
         title = "New Log"
      else:
         title = title
      Gtk.Dialog.__init__(self, title=title, parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

      hbox_temp = Gtk.HBox(spacing=0)
      label = Gtk.Label("Log Name:")
      label.set_alignment(0, 0.5)
      hbox_temp.pack_start(label, False, False, 6)
      self.entry = Gtk.Entry()
      if(name is not None):
         self.entry.set_text(name)
      hbox_temp.pack_start(self.entry, False, False, 6)
      self.vbox.pack_start(hbox_temp, False, False, 6)

      self.show_all()

      logging.debug("New LogNameDialog instance created!")

      return

   def get_log_name(self):
      """ Return the log name specified in the Gtk.Entry box by the user.
      
      :returns: The log's name.
      :rtype: str
      """

      logging.debug("Retrieving the log name from the LogNameDialog...")
      return self.entry.get_text()


