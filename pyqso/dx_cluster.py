#!/usr/bin/env python
# File: dx_cluster.py

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
import os
import os.path
import sys
import telnetlib

from pyqso.telnet_connection_dialog import *

# This will help Python find the PyQSO modules
# that need to be imported below.
pyqso_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir)
sys.path.insert(0, pyqso_path)

class DXCluster(Gtk.Window):
   
   def __init__(self):
         
      # Call the constructor of the super class (Gtk.Window)
      Gtk.Window.__init__(self, title="DX Cluster")
      self.set_size_request(600, 500)
      self.connect("delete-event", self.on_delete)

      possible_icon_paths = [os.path.join(pyqso_path, "icons", "log_64x64.png")]
      for icon_path in possible_icon_paths:
         try:
            self.set_icon_from_file(icon_path)
         except Exception, error:
            print error.message

      self.connection = None

      vbox_inner = Gtk.VBox(spacing=2)

      # Set up the toolbar
      self.toolbar = Gtk.HBox(spacing=2)
      self.buttons = {}
      # Connect
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_CONNECT, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Connect to Telnet server')
      button.connect("clicked", self.telnet_connect)
      self.toolbar.pack_start(button, False, False, 0)
      self.buttons["CONNECT"] = button

      # Disconnect
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_DISCONNECT, Gtk.IconSize.BUTTON)
      button = Gtk.Button()
      button.add(icon)
      button.set_tooltip_text('Disconnect from Telnet server')
      button.connect("clicked", self.telnet_disconnect)
      self.toolbar.pack_start(button, False, False, 0)
      self.buttons["DISCONNECT"] = button

      self.toolbar.pack_start(Gtk.SeparatorToolItem(), False, False, 0)

      self.command = Gtk.Entry()
      self.toolbar.pack_start(self.command, False, False, 0)
      self.send = Gtk.Button("Send Command")
      self.send.connect("clicked", self.telnet_send_command)
      self.toolbar.pack_start(self.send, False, False, 0)

      vbox_inner.pack_start(self.toolbar, False, False, 6)

      # A TextView object to display the output from the Telnet server.
      self.renderer = Gtk.TextView()
      self.renderer.set_editable(False)
      sw = Gtk.ScrolledWindow()
      sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
      sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
      sw.add(self.renderer)
      self.buffer = self.renderer.get_buffer()
      vbox_inner.pack_start(sw, True, True, 6)

      self.add(vbox_inner)

      self.set_connect_button_sensitive(True)

      self.show_all()

      return

   def telnet_connect(self, widget=None):

      dialog = TelnetConnectionDialog(self)
      response = dialog.run()
      if(response == Gtk.ResponseType.OK):
         connection_info = dialog.get_connection_info()
         host = connection_info["HOST"].get_text()
         port = connection_info["PORT"].get_text()
         username = connection_info["USERNAME"].get_text()
         password = connection_info["PASSWORD"].get_text()
         dialog.destroy()
      else:
         dialog.destroy()
         return

      if(host == ""):
         logging.error("No Telnet server specified.")
         return
      if(port == ""):
         port = 23 # The default Telnet port
      else:
         port = int(port)

      try:
         self.connection = telnetlib.Telnet(host, port)

         if(username):
            self.connection.read_until("login: ")
            self.connection.write(username + "\n")
         if(password):
            self.connection.read_until("password: ")
            self.connection.write(password + "\n")
      except:
         logging.exception("Could not create a connection to the Telnet server")
         self.connection = None
         return
  
      self.check_io_event = GObject.timeout_add(1000, self.on_telnet_io)

      self.set_connect_button_sensitive(False)

      return

   def telnet_disconnect(self, widget=None):
      if(self.connection):
         self.connection.close()
      self.buffer.set_text("")
      self.connection = None
      self.set_connect_button_sensitive(True)
      return

   def telnet_send_command(self, widget=None):
      if(self.connection):
         self.connection.write(self.command.get_text() + "\n")
         self.command.set_text("")
      return

   def on_telnet_io(self):
      if(self.connection):
         self.buffer.insert_at_cursor(self.connection.read_very_eager())
         self.renderer.scroll_to_mark(self.buffer.get_insert(), within_margin=0, use_align=False, xalign=0.5, yalign=0.5)
      return True
   
   def on_delete(self, widget, event):
      self.telnet_disconnect()
      GObject.source_remove(self.check_io_event)

   def set_connect_button_sensitive(self, sensitive):
      self.buttons["CONNECT"].set_sensitive(sensitive)
      self.buttons["DISCONNECT"].set_sensitive(not sensitive)
      self.send.set_sensitive(not sensitive)
      return

