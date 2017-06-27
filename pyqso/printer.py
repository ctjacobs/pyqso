#!/usr/bin/env python3

#    Copyright (C) 2017 Christian Thomas Jacobs.

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

from gi.repository import Gtk, Pango, PangoCairo
from pyqso.auxiliary_dialogs import error


class Printer(object):

    """ Handles the printing of one or more records to file or paper. """

    def __init__(self, application):
        """ Initialise the record printer.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.application = application

        self.action = Gtk.PrintOperationAction.PRINT_DIALOG
        self.operation = Gtk.PrintOperation()
        self.operation.set_default_page_setup(Gtk.PageSetup())
        self.operation.set_unit(Gtk.Unit.MM)

        self.operation.connect("begin_print", self.begin_print)
        self.operation.connect("draw_page", self.draw_page)

        return

    def print_records(self, records):
        """ Perform the print operation.

        :arg dict records: The records to be printed.
        """

        # Assemble the header and records into one string.
        self.text_to_print = "Callsign\t---\tDate\t---\tTime\t---\tFrequency\t---\tMode\n"
        for r in records:
            self.text_to_print += str(r["CALL"]) + "\t---\t" + str(r["QSO_DATE"]) + "\t---\t" + str(r["TIME_ON"]) + "\t---\t" + str(r["FREQ"]) + "\t---\t" + str(r["MODE"]) + "\n"

        result = self.operation.run(self.action, parent=self.application.window)
        if(result == Gtk.PrintOperationResult.ERROR):
            error(parent=self.application.window, message="Unable to print the log.")

        return result

    def begin_print(self, operation, context):
        """ Specify the layout/position/font of the text on the pages to be printed.

        :arg Gtk.PrintOperation operation: The printing API.
        :arg Gtk.PrintContext context: Used to draw/render the pages to print.
        """
        width = context.get_width()
        height = context.get_height()
        layout = context.create_pango_layout()
        layout.set_font_description(Pango.FontDescription("normal 10"))
        layout.set_width(int(width*Pango.SCALE))
        layout.set_text(self.text_to_print, -1)

        number_of_pages = 0
        page_height = 0
        for line in range(0, layout.get_line_count()):
            layout_line = layout.get_line(line)
            ink_rectangle, logical_rectangle = layout_line.get_extents()
            self.line_height = logical_rectangle.height/1024.0 + 3
            page_height += self.line_height
            if(page_height + self.line_height > height):
                number_of_pages += 1
                page_height = self.line_height
        operation.set_n_pages(number_of_pages + 1)
        self.text_to_print = self.text_to_print.split("\n")
        return

    def draw_page(self, operation, context, page_number):
        """ Render the QSO details on the page.

        :arg Gtk.PrintOperation operation: The printing API.
        :arg Gtk.PrintContext context: Used to draw/render the pages to print.
        :arg int page_number: The current page number.
        """
        cr = context.get_cairo_context()
        cr.set_source_rgb(0, 0, 0)
        layout = context.create_pango_layout()

        current_line_number = 0
        for line in self.text_to_print:
            layout.set_text(line, -1)
            cr.move_to(5, current_line_number*self.line_height)
            PangoCairo.update_layout(cr, layout)
            PangoCairo.show_layout(cr, layout)
            current_line_number += 1
            if(current_line_number*self.line_height > context.get_height()):
                for j in range(0, current_line_number):
                    self.text_to_print.pop(0)  # Remove what has been printed already before draw_page is called again
                break
        return
