#!/usr/bin/env python 
# File: auxiliary_dialogs.py

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

def error(parent, message):
   """ Display an error message. """
   logging.error(message)
   dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message, title="Error")
   dialog.run()
   dialog.destroy()
   return

def info(parent, message):
   """ Display some information. """
   logging.debug(message)
   dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.INFO, Gtk.ButtonsType.OK, message, title="Information")
   dialog.run()
   dialog.destroy()
   return
   
def question(parent, message):
   """ Ask the user a question. The dialog comes with 'Yes' and 'No' response buttons. """
   dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.DESTROY_WITH_PARENT,
                              Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 
                              message, title="Question")
   response = dialog.run()
   dialog.destroy()
   return response
