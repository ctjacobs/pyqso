#!/usr/bin/env python
# File: toolbar.py

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

class Toolbar(Gtk.HBox):
   
   def __init__(self, parent, vbox_parent):
      logging.debug("New Toolbar instance created!")
      
      Gtk.HBox.__init__(self, spacing=2)

      # Add record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Add record')
      button.connect("clicked", parent.add_record_callback)
      self.pack_start(button, False, False, 0)

      # Edit record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_EDIT, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Edit record')
      button.connect("clicked", parent.update_record_callback)
      self.pack_start(button, False, False, 0)

      # Delete record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Delete record')
      button.connect("clicked", parent.delete_record_callback)
      self.pack_start(button, False, False, 0)

      vbox_parent.pack_start(self, False, False, 0)

      return
