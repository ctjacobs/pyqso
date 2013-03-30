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
   
   def __init__(self, parent):
      logging.debug("New Toolbar instance created!")
      
      Gtk.HBox.__init__(self, spacing=2)

      # New log
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_NEW, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('New log')
      button.connect("clicked", parent.logbook.new_log)
      self.pack_start(button, False, False, 0)

      # Open log
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Open log')
      button.connect("clicked", parent.logbook.open_log)
      self.pack_start(button, False, False, 0)

      # Save log
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_FLOPPY, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Save log')
      button.connect("clicked", parent.logbook.save_log)
      self.pack_start(button, False, False, 0)

      # Close log
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Close log')
      button.connect("clicked", parent.logbook.close_log)
      self.pack_start(button, False, False, 0)

      self.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)

      # Add record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Add record')
      button.connect("clicked", parent.logbook.add_record_callback, parent)
      self.pack_start(button, False, False, 0)

      # Edit record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_EDIT, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Edit record')
      button.connect("clicked", parent.logbook.edit_record_callback, None, None, parent)
      self.pack_start(button, False, False, 0)

      # Delete record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Delete record')
      button.connect("clicked", parent.logbook.delete_record_callback, parent)
      self.pack_start(button, False, False, 0)

      self.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)

      # Search log
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_FIND, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Search log')
      button.connect("clicked", parent.logbook.search_log_callback)
      self.pack_start(button, False, False, 0)

      return
