#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian Thomas Jacobs.

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

from gi.repository import Gtk, GObject, Gdk, GLib
import logging
import telnetlib3
import asyncio
from threading import Thread
import configparser
import os.path

from pyqso.telnet_connection_dialog import TelnetConnectionDialog
from pyqso.auxiliary_dialogs import error

BOOKMARKS_FILE = os.path.expanduser('~/.config/pyqso/bookmarks.ini')


class DXCluster:

    """ A tool for connecting to a DX cluster (specifically Telnet-based DX clusters). """

    def __init__(self, application):
        """ Set up the DX cluster, and set up a timer so that PyQSO can retrieve new data from the Telnet server every few seconds.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        logging.debug("Setting up the DX cluster...")

        self.application = application
        self.builder = self.application.builder
        self.thread = None
        self.telnet_reader = None
        self.telnet_writer = None

        # Connect signals.
        self.builder.get_object('mitem_new').connect('activate', self.connect_to_new_server)
        self.builder.get_object('mitem_disconnect').connect('activate', self.disconnect)
        self.builder.get_object('send').connect('clicked', self.send_command)
        self.builder.get_object('command').connect('key-press-event', self.on_command_key_press)

        # Get the text renderer and its buffer.
        self.renderer = self.builder.get_object('renderer')
        self.buffer = self.renderer.get_buffer()

        # Items whose sensitivity may change.
        self.items = {}
        self.items['CONNECT'] = self.builder.get_object('mitem_connect')
        self.items['DISCONNECT'] = self.builder.get_object('mitem_disconnect')
        self.items['SEND'] = self.builder.get_object('send')
        self.set_items_sensitive(True)

        self.populate_bookmarks()
        
        logging.debug("DX cluster ready.")

    def on_command_key_press(self, widget, event, data=None):
        """ If the Return key is pressed when the focus is on the command box, then send whatever command the user has entered. """
        if event.keyval == Gdk.KEY_Return:
            self.send_command()

    def connect_to_new_server(self, widget=None):
        """ Get Telnet server host and login details specified in the Gtk.Entry boxes in the Telnet connection dialog and attempt a connection. """

        # Get connection details.
        tcd = TelnetConnectionDialog(self.application)
        response = tcd.dialog.run()
        if response == Gtk.ResponseType.OK:
            host = tcd.host
            port = tcd.port
            username = tcd.username
            password = tcd.password
            bookmark = tcd.bookmark
            tcd.dialog.destroy()

            # Handle empty hostname.
            if not host:
                logging.error("No hostname specified.")
                return

            # Handle empty port number.
            if not port:
                logging.warning("No port specified. Assuming default port 23...")
                port = 23
            else:
                try:
                    # Cast port into an int.
                    port = int(port)
                except ValueError as e:
                    logging.error("Could not cast the DX cluster's port information to an integer.")
                    logging.exception(e)
                    return

            # Save the server details in a new bookmark, if desired.
            if bookmark:
                try:
                    config = configparser.ConfigParser()
                    config.read(BOOKMARKS_FILE)

                    # Use the host name as the bookmark's identifier.
                    if username:
                        bookmark_identifier = "%s@%s:%d" % (username, host, port)
                    else:
                        bookmark_identifier = "%s:%d" % (host, port)
                    logging.debug("Using %s as the bookmark identifier." % bookmark_identifier)

                    # Add bookmark.
                    try:
                        config.add_section(bookmark_identifier)
                    except configparser.DuplicateSectionError:
                        # If the hostname already exists, assume the user wants to update the port number, username and/or password.
                        logging.warning("Bookmark '%s' already exists. Over-writing existing details..." % (bookmark_identifier))
                    config.set(bookmark_identifier, 'host', host)
                    config.set(bookmark_identifier, 'port', str(port))
                    config.set(bookmark_identifier, 'username', username)
                    config.set(bookmark_identifier, 'password', password)

                    # Write the bookmarks to file.
                    if not os.path.exists(os.path.expanduser('~/.config/pyqso')):
                        os.makedirs(os.path.expanduser('~/.config/pyqso'))
                    with open(BOOKMARKS_FILE, 'w') as f:
                        config.write(f)

                    self.populate_bookmarks()
                except IOError:
                    # Maybe the bookmarks file could not be written to?
                    logging.error("Bookmark could not be saved. Check bookmarks file permissions. Proceeding with the server connection anyway...")

            # Attempt a connection with the server.
            self.connect(host, port, username, password)

        else:
            tcd.dialog.destroy()

    def populate_bookmarks(self):
        """ Populate the list of bookmarked Telnet servers in the menu. """

        # Get the bookmarks submenu.
        subm_bookmarks = self.builder.get_object('subm_bookmarks')

        config = configparser.ConfigParser()
        have_config = (config.read(BOOKMARKS_FILE) != [])

        if have_config:
            try:
                # Clear the menu of all current bookmarks.
                for i in subm_bookmarks.get_children():
                    subm_bookmarks.remove(i)

                # Add all bookmarks in the config file.
                for bookmark in config.sections():
                    mitem = Gtk.MenuItem(label=bookmark)
                    mitem.connect('activate', self.connect_to_bookmarked_server, bookmark)
                    subm_bookmarks.append(mitem)

            except Exception as e:
                logging.error("An error occurred whilst populating the DX cluster bookmarks menu.")
                logging.exception(e)

            self.builder.get_object('dx_cluster').show_all()  # Need to do this to update the bookmarks list in the menu.

    def connect_to_bookmarked_server(self, widget, name):
        """ Get Telnet server host and login details from an existing bookmark and attempt a connection.

        :arg str name: The name of the bookmark. This is the same as the server's hostname.
        """

        config = configparser.ConfigParser()
        have_config = (config.read(BOOKMARKS_FILE) != [])
        try:
            if not have_config:
                raise IOError("The bookmark's details could not be loaded.")

            host = config.get(name, 'host')
            port = int(config.get(name, 'port'))
            username = config.get(name, 'username')
            password = config.get(name, 'password')
            self.connect(host, port, username, password)

        except ValueError as e:
            # This exception may occur when casting the port (which is a str) to an int.
            logging.exception(e)
        except IOError as e:
            logging.exception(e)
        except Exception as e:
            logging.error("Could not connect to Telnet server '%s'." % name)
            logging.exception(e)

    def render(self, data):
        """ Add the text received from the Telnet server to the
        text buffer, and perform autoscrolling. """
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, data)
        end_mark = self.buffer.create_mark('end', end_iter)
        self.renderer.scroll_mark_onscreen(end_mark)

    async def telnet_shell(self, host, port, username, password):
        """ Receive and render text from the Telnet server. """
        while True:
            # Wait for data from the Telnet server.
            data = await self.telnet_reader.read(4096)
            if not data:
                break
            else:
                # Call the rendering method in the main Gtk loop,
                # rather than the asyncio loop.
                GLib.idle_add(self.render, data)

            # Responses to login/password prompts.
            if username and ("login: " in data):
                self.telnet_writer.write(username + '\n')
            if password and ("password: " in data):
                self.telnet_writer.write(password + '\n')

    def send_command(self, widget=None):
        """ Send the user-specified command in the Gtk.Entry box to the Telnet server. """
        command = self.builder.get_object('command')
        self.telnet_writer.write(command.get_text() + '\n')
        command.set_text("")

    def start_telnet(self, host, port, username, password):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Attempt connection to Telnet server.
        try:
            logging.debug("Attempting connection to Telnet server %s:%d..." % (host, port))
            self.telnet_reader, self.telnet_writer = loop.run_until_complete(telnetlib3.open_connection(host, port))
            logging.debug("Connection to %s:%d established." % (host, port))
        except Exception as e:
            logging.exception(e)
            message = "Could not create a connection to the Telnet server %s:%d. Check connection to the internet. Check connection details." % (host, port)
            GLib.idle_add(error, self.application.window, message)
            return

        # When successfully connected, disable the option to connect.
        GLib.idle_add(self.set_items_sensitive, False)

        # Run interactive shell.
        try:
            loop.run_until_complete(self.telnet_shell(host, port, username, password))
        except Exception as e:
            logging.exception(e)
            GLib.idle_add(error, self.application.window, "Exception occurred in Telnet shell.")

        # Clean up and re-enable the option to connect again.
        GLib.idle_add(self.set_items_sensitive, True)
        loop.close()

    def connect(self, host, port=23, username=None, password=None):
        """ Connect to a user-specified Telnet server.

        :arg str host: The Telnet server's hostname.
        :arg int port: The Telnet server's port number. If no port is specified, the default Telnet server port of 23 will be used.
        :arg str username: The user's username. This is an optional argument.
        :arg str password: The user's password. This is an optional argument.
        """

        # Handle empty host/port string (or the case where host/port are None).
        if not host:
            error(parent=self.application.window, message="Unable to connect to a DX cluster because no hostname was specified.")
            return
        if not port:
            logging.warning("No port specified. Assuming default port 23...")
            port = 23  # Use the default Telnet port.

        try:
            self.thread = Thread(target=self.start_telnet, args=(host, port, username, password))
            self.thread.setDaemon(True)  # Allows the thread to be stopped when the main Gtk thread is stopped.
            self.thread.start()
        except Exception as e:
            logging.exception(e)
            error(parent=self.application.window, message="Could not start Telnet.")
            return

    def disconnect(self, widget=None):
        """ Disconnect from a Telnet server. """
        self.telnet_writer.write("quit\n")
        self.telnet_writer.close()
        self.set_items_sensitive(True)

    def set_items_sensitive(self, sensitive):
        """ Enable/disable the relevant buttons for connecting/disconnecting from a DX cluster, so that users cannot click the connect button if PyQSO is already connected.

        :arg bool sensitive: If True, enable the Connect button and disable the Disconnect button. If False, vice versa.
        """
        self.items['CONNECT'].set_sensitive(sensitive)
        self.items['DISCONNECT'].set_sensitive(not sensitive)
        self.items['SEND'].set_sensitive(not sensitive)
