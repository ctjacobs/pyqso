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

from gi.repository import Gtk, GObject, Gdk
import logging
import telnetlib
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
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
        self.connection = None

        # Connect signals.
        self.builder.get_object("mitem_new").connect("activate", self.new_server)
        self.builder.get_object("mitem_disconnect").connect("activate", self.telnet_disconnect)
        self.builder.get_object("send").connect("clicked", self.telnet_send_command)
        self.builder.get_object("command").connect("key-release-event", self.on_command_key_press)

        # Get the text renderer and its buffer.
        self.renderer = self.builder.get_object("renderer")
        self.buffer = self.renderer.get_buffer()

        # Items whose sensitivity may change.
        self.items = {}
        self.items["CONNECT"] = self.builder.get_object("mitem_connect")
        self.items["DISCONNECT"] = self.builder.get_object("mitem_disconnect")
        self.items["SEND"] = self.builder.get_object("send")
        self.set_items_sensitive(True)

        self.populate_bookmarks()

        logging.debug("DX cluster ready!")

        return

    def on_command_key_press(self, widget, event, data=None):
        """ If the Return key is pressed when the focus is on the command box, then send whatever command the user has entered. """
        if(event.keyval == Gdk.KEY_Return):
            self.telnet_send_command()
        return

    def new_server(self, widget=None):
        """ Get Telnet server host and login details specified in the Gtk.Entry boxes in the Telnet connection dialog and attempt a connection. """

        # Get connection details.
        tcd = TelnetConnectionDialog(self.application)
        response = tcd.dialog.run()
        if(response == Gtk.ResponseType.OK):
            host = tcd.host
            port = tcd.port
            username = tcd.username
            password = tcd.password
            bookmark = tcd.bookmark
            tcd.dialog.destroy()

            # Handle empty hostname.
            if(not host):
                logging.error("No hostname specified.")
                return

            # Handle empty port number.
            if(not port):
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
            if(bookmark):
                try:
                    config = configparser.ConfigParser()
                    config.read(BOOKMARKS_FILE)

                    # Use the host name as the bookmark's identifier.
                    if(username):
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
                    config.set(bookmark_identifier, "host", host)
                    config.set(bookmark_identifier, "port", str(port))
                    config.set(bookmark_identifier, "username", username)
                    config.set(bookmark_identifier, "password", password)

                    # Write the bookmarks to file.
                    if not os.path.exists(os.path.expanduser('~/.config/pyqso')):
                        os.makedirs(os.path.expanduser('~/.config/pyqso'))
                    with open(BOOKMARKS_FILE, 'w') as f:
                        config.write(f)

                    self.populate_bookmarks()

                except IOError:
                    # Maybe the bookmarks file could not be written to?
                    logging.error("Bookmark could not be saved. Check bookmarks file permissions? Going ahead with the server connection anyway...")

            # Attempt a connection with the server.
            self.telnet_connect(host, port, username, password)

        else:
            tcd.dialog.destroy()
        return

    def populate_bookmarks(self):
        """ Populate the list of bookmarked Telnet servers in the menu. """

        # Get the bookmarks submenu.
        subm_bookmarks = self.builder.get_object("subm_bookmarks")

        config = configparser.ConfigParser()
        have_config = (config.read(BOOKMARKS_FILE) != [])

        if(have_config):
            try:
                # Clear the menu of all current bookmarks.
                for i in subm_bookmarks.get_children():
                    subm_bookmarks.remove(i)

                # Add all bookmarks in the config file.
                for bookmark in config.sections():
                    mitem = Gtk.MenuItem(label=bookmark)
                    mitem.connect("activate", self.bookmarked_server, bookmark)
                    subm_bookmarks.append(mitem)

            except Exception as e:
                logging.error("An error occurred whilst populating the DX cluster bookmarks menu.")
                logging.exception(e)

            self.builder.get_object("dx_cluster").show_all()  # Need to do this to update the bookmarks list in the menu.

        return

    def bookmarked_server(self, widget, name):
        """ Get Telnet server host and login details from an existing bookmark and attempt a connection.

        :arg str name: The name of the bookmark. This is the same as the server's hostname.
        """

        config = configparser.ConfigParser()
        have_config = (config.read(BOOKMARKS_FILE) != [])
        try:
            if(not have_config):
                raise IOError("The bookmark's details could not be loaded.")

            host = config.get(name, "host")
            port = int(config.get(name, "port"))
            username = config.get(name, "username")
            password = config.get(name, "password")
            self.telnet_connect(host, port, username, password)

        except ValueError as e:
            # This exception may occur when casting the port (which is a str) to an int.
            logging.exception(e)
        except IOError as e:
            logging.exception(e)
        except Exception as e:
            logging.error("Could not connect to Telnet server '%s'." % name)
            logging.exception(e)

        return

    def telnet_connect(self, host, port=23, username=None, password=None):
        """ Connect to a user-specified Telnet server.

        :arg str host: The Telnet server's hostname.
        :arg int port: The Telnet server's port number. If no port is specified, the default Telnet server port of 23 will be used.
        :arg str username: The user's username. This is an optional argument.
        :arg str password: The user's password. This is an optional argument.
        """

        # Handle empty host/port string (or the case where host/port are None).
        if(not host):
            message = "Unable to connect to a DX cluster because no hostname was specified."
            logging.error(message)
            error(parent=self.application.window, message=message)
            return
        if(not port):
            logging.warning("No port specified. Assuming default port 23...")
            port = 23  # Use the default Telnet port.

        try:
            logging.debug("Attempting connection to Telnet server %s:%d..." % (host, port))
            self.connection = telnetlib.Telnet(host, port)
            assert(self.connection)

            if(username):
                self.connection.read_until("login: ".encode())
                self.connection.write((username + "\n").encode())
            if(password):
                self.connection.read_until("password: ".encode())
                self.connection.write((password + "\n").encode())
        except Exception as e:
            message = "Could not create a connection to the Telnet server %s:%d. Check connection to the internets? Check connection details?" % (host, port)
            logging.error(message)
            logging.exception(e)
            error(parent=self.application.window, message=message)
            self.connection = None
            return

        logging.debug("Connection to %s:%d established." % (host, port))

        self.set_items_sensitive(False)

        self.check_io_event = GObject.timeout_add(1000, self.on_telnet_io)

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
            command = self.builder.get_object("command")
            self.connection.write((command.get_text() + "\n").encode())
            command.set_text("")
        return

    def on_telnet_io(self):
        """ Retrieve any new data from the Telnet server and print it out in the Gtk.TextView widget.

        :returns: Always returns True to satisfy the GObject timer.
        :rtype: bool
        """
        if(self.connection):
            text = self.connection.read_very_eager()
            text = text.decode("ascii", "replace")  # Replace any characters that cannot be decoded with a replacement marker.
            try:
                text = text.replace("\u0007", "")  # Remove the BEL Unicode character from the end of the line
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
        self.items["SEND"].set_sensitive(not sensitive)
        return
