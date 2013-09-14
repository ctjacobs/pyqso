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

      logging.debug("Setting up the toolbar...")   
      self.buttons = {}

      # Create/open logbook
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Create/Open Logbook')
      button.connect("clicked", parent.logbook.open)
      self.pack_start(button, False, False, 0)
      self.buttons["OPEN_LOGBOOK"] = button

      # Close logbook
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Close Logbook')
      button.connect("clicked", parent.logbook.close)
      self.pack_start(button, False, False, 0)
      self.buttons["CLOSE_LOGBOOK"] = button

      self.pack_start(Gtk.SeparatorToolItem(), False, False, 0)

      # Add record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Add record')
      button.connect("clicked", parent.logbook.add_record_callback)
      self.pack_start(button, False, False, 0)
      self.buttons["ADD_RECORD"] = button

      # Edit record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_EDIT, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Edit record')
      button.connect("clicked", parent.logbook.edit_record_callback, None, None)
      self.pack_start(button, False, False, 0)
      self.buttons["EDIT_RECORD"] = button

      # Delete record
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Delete record')
      button.connect("clicked", parent.logbook.delete_record_callback)
      self.pack_start(button, False, False, 0)
      self.buttons["DELETE_RECORD"] = button

      self.pack_start(Gtk.SeparatorToolItem(), False, False, 0)

      # Filter log
      label = Gtk.Label("Filter by callsign: ")
      self.pack_start(label, False, False, 0)
      self.filter_source = Gtk.Entry()
      self.filter_source.set_width_chars(11)
      self.filter_source.connect_after("changed", parent.logbook.filter_logs)
      self.pack_start(self.filter_source, False, False, 0)

      self.set_logbook_button_sensitive(True)
      self.set_record_buttons_sensitive(False)

      self.filter_source.set_sensitive(False)

      logging.debug("Toolbar ready!") 

      return

   def set_logbook_button_sensitive(self, sensitive):
      logging.debug("Setting the 'Create/Open Logbook' toolbar item's sensitivity to: %s..." % sensitive) 
      self.buttons["OPEN_LOGBOOK"].set_sensitive(sensitive)
      self.buttons["CLOSE_LOGBOOK"].set_sensitive(not sensitive)
      logging.debug("Set the 'Create/Open Logbook' toolbar item's sensitivity to: %s." % sensitive) 
      return

   def set_record_buttons_sensitive(self, sensitive):
      logging.debug("Setting record-related menu item sensitivity to: %s..." % sensitive) 
      for button_name in ["ADD_RECORD", "EDIT_RECORD", "DELETE_RECORD"]:
         self.buttons[button_name].set_sensitive(sensitive)
      logging.debug("Set record-related menu item sensitivity to: %s." % sensitive) 
      return



