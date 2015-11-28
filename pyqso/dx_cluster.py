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

from gi.repository import Gtk, GObject
import logging
import telnetlib
import unittest
import unittest.mock

from pyqso.telnet_connection_dialog import *

class DXCluster(Gtk.VBox):
   """ A tool for connecting to a DX cluster (specifically Telnet-based DX clusters). """
   
   def __init__(self, parent):
      """ Set up the DX cluster's Gtk.VBox, and set up a timer so that PyQSO can retrieve new data from the Telnet server every few seconds.
      
      :arg parent: The parent Gtk window.
      """
      logging.debug("Setting up the DX cluster...") 
      Gtk.VBox.__init__(self, spacing=2)

      self.connection = None
      self.parent = parent

      # Set up the menubar
      self.menubar = Gtk.MenuBar()
      
      self.items = {}
      
      ###### CONNECTION ######
      mitem_connection = Gtk.MenuItem("Connection")
      self.menubar.append(mitem_connection)  
      subm_connection = Gtk.Menu()
      mitem_connection.set_submenu(subm_connection)

      # Connect
      mitem_connect = Gtk.ImageMenuItem("Connect to Telnet Server...")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_CONNECT, Gtk.IconSize.MENU)
      mitem_connect.set_image(icon)
      mitem_connect.connect("activate", self.telnet_connect)
      subm_connection.append(mitem_connect)
      self.items["CONNECT"] = mitem_connect

      # Disconnect
      mitem_disconnect = Gtk.ImageMenuItem("Disconnect from Telnet Server")
      icon = Gtk.Image()
      icon.set_from_stock(Gtk.STOCK_DISCONNECT, Gtk.IconSize.MENU)
      mitem_disconnect.set_image(icon)
      mitem_disconnect.connect("activate", self.telnet_disconnect)
      subm_connection.append(mitem_disconnect)
      self.items["DISCONNECT"] = mitem_disconnect
      
      self.pack_start(self.menubar, False, False, 0)

      # A TextView object to display the output from the Telnet server.
      self.renderer = Gtk.TextView()
      self.renderer.set_editable(False)
      self.renderer.set_cursor_visible(False)
      sw = Gtk.ScrolledWindow()
      sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
      sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
      sw.add(self.renderer)
      self.buffer = self.renderer.get_buffer()
      self.pack_start(sw, True, True, 0)

      # Set up the command box.
      self.commandbox = Gtk.HBox(spacing=2)
      self.command = Gtk.Entry()
      self.commandbox.pack_start(self.command, True, True, 0)
      self.send = Gtk.Button(label="Send Command")
      self.send.connect("clicked", self.telnet_send_command)
      self.commandbox.pack_start(self.send, False, False, 0)
      self.pack_start(self.commandbox, False, False, 0)
      
      self.set_items_sensitive(True)
            
      self.show_all()

      logging.debug("DX cluster ready!") 

      return

   def telnet_connect(self, widget=None):
      """ Connect to a user-specified Telnet server, with the host and login details specified in the Gtk.Entry boxes in the TelnetConnectionDialog. """
      dialog = TelnetConnectionDialog(self.parent)
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
            self.connection.read_until("login: ".encode())
            self.connection.write((username + "\n").encode())
         if(password):
            self.connection.read_until("password: ".encode())
            self.connection.write((password + "\n").encode())
      except:
         logging.exception("Could not create a connection to the Telnet server")
         self.connection = None
         return

      self.set_items_sensitive(False)

      self.check_io_event = GObject.timeout_add(1000, self._on_telnet_io)

      return

   def telnet_disconnect(self, widget=None):
      """ Disconnect from a Telnet server and remove the I/O timer. """
      if(self.connection):
         self.connection.close()
      self.buffer.set_text("")
      self.connection = None
      self.set_items_sensitive(True)
      
      # Stop checking for server output once disconnected.
      try:
         GObject.source_remove(self.check_io_event)
      except AttributeError:
         # This may happen if a connection hasn't yet been established.
         pass

      return

   def telnet_send_command(self, widget=None):
      """ Send the user-specified command in the Gtk.Entry box to the Telnet server (if PyQSO is connected to one). """
      if(self.connection):
         self.connection.write((self.command.get_text() + "\n").encode())
         self.command.set_text("")
      return

   def _on_telnet_io(self):
      """ Retrieve any new data from the Telnet server and print it out in the Gtk.TextView widget.
      
      :returns: Always returns True to satisfy the GObject timer.
      :rtype: bool
      """
      if(self.connection):
         text = self.connection.read_very_eager().decode()
         try:
            text = text.replace("\u0007", "") # Remove the BEL Unicode character from the end of the line
         except UnicodeDecodeError:
            pass
            
         # Allow auto-scrolling to the new text entry if the focus is already at
         # the very end of the Gtk.TextView. Otherwise, don't auto-scroll
         # in case the user is reading something further up.
         # Note: This is based on the code from http://forums.gentoo.org/viewtopic-t-445598-view-next.html
         end_iter = self.buffer.get_end_iter()
         end_mark = self.buffer.create_mark(None, end_iter)
         self.renderer.move_mark_onscreen(end_mark)
         at_end = self.buffer.get_iter_at_mark(end_mark).equal(end_iter)
         self.buffer.insert(end_iter, text)
         if(at_end):
            end_mark = self.buffer.create_mark(None, end_iter)
            self.renderer.scroll_mark_onscreen(end_mark) 

      return True

   def set_items_sensitive(self, sensitive):
      """ Enable/disable the relevant buttons for connecting/disconnecting from a DX cluster, so that users cannot click the connect button if PyQSO is already connected.
      
      :arg bool sensitive: If True, enable the Connect button and disable the Disconnect button. If False, vice versa.
      """
      self.items["CONNECT"].set_sensitive(sensitive)
      self.items["DISCONNECT"].set_sensitive(not sensitive)
      self.send.set_sensitive(not sensitive)
      return

class TestDXCluster(unittest.TestCase):
   """ The unit tests for the DXCluster class. """

   def setUp(self):
      """ Set up the objects needed for the unit tests. """
      self.dxcluster = DXCluster(parent=None)

   def tearDown(self):
      """ Destroy any unit test resources. """
      pass

   def test_on_telnet_io(self):
      """ Check that the response from the Telnet server can be correctly decoded. """

      telnetlib.Telnet = unittest.mock.Mock(spec=telnetlib.Telnet)
      connection = telnetlib.Telnet("hello", "world")
      connection.read_very_eager.return_value = b"Test message from the Telnet server."
      self.dxcluster.connection = connection
      result = self.dxcluster._on_telnet_io()
      assert(result)
      
if(__name__ == '__main__'):
   unittest.main()
