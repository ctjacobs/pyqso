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

from gi.repository import Gtk
import logging
from os.path import basename, getmtime, expanduser
from datetime import datetime, date
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
try:
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['font.size'] = 10.0
    from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter, MonthLocator
    have_matplotlib = True
except ImportError as e:
    logging.warning(e)
    logging.warning("Could not import matplotlib, so you will not be able to plot annual logbook statistics. Check that all the PyQSO dependencies are satisfied.")
    have_matplotlib = False


class Summary(object):

    def __init__(self, logbook):
        """ Create a summary page containing the number of logs in the logbook, and the logbook's modification date. """

        self.logbook = logbook

        vbox = Gtk.VBox()

        # Database name in large font at the top of the summary page
        hbox = Gtk.HBox()
        label = Gtk.Label(halign=Gtk.Align.START)
        label.set_markup("<span size=\"x-large\">%s</span>" % basename(self.path))
        hbox.pack_start(label, False, False, 6)
        vbox.pack_start(hbox, False, False, 4)

        hbox = Gtk.HBox()
        label = Gtk.Label("Number of logs: ", halign=Gtk.Align.START)
        hbox.pack_start(label, False, False, 6)
        self.summary["LOG_COUNT"] = Gtk.Label("0")
        hbox.pack_start(self.summary["LOG_COUNT"], False, False, 4)
        vbox.pack_start(hbox, False, False, 4)

        hbox = Gtk.HBox()
        label = Gtk.Label("Total number of QSOs: ", halign=Gtk.Align.START)
        hbox.pack_start(label, False, False, 6)
        self.summary["QSO_COUNT"] = Gtk.Label("0")
        hbox.pack_start(self.summary["QSO_COUNT"], False, False, 4)
        vbox.pack_start(hbox, False, False, 4)

        hbox = Gtk.HBox()
        label = Gtk.Label("Date modified: ", halign=Gtk.Align.START)
        hbox.pack_start(label, False, False, 6)
        self.summary["DATE_MODIFIED"] = Gtk.Label("0")
        hbox.pack_start(self.summary["DATE_MODIFIED"], False, False, 4)
        vbox.pack_start(hbox, False, False, 4)

        hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(hseparator, False, False, 4)

        # Yearly statistics
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])
        (section, option) = ("general", "show_yearly_statistics")
        if(have_config and config.has_option(section, option)):
            if(config.get("general", "show_yearly_statistics") == "True" and have_matplotlib):
                hbox = Gtk.HBox()
                label = Gtk.Label("Display statistics for year: ", halign=Gtk.Align.START)
                hbox.pack_start(label, False, False, 6)
                self.summary["YEAR_SELECT"] = Gtk.ComboBoxText()
                min_year, max_year = self._find_year_bounds()
                if min_year and max_year:
                    for year in range(max_year, min_year-1, -1):
                        self.summary["YEAR_SELECT"].append_text(str(year))
                self.summary["YEAR_SELECT"].append_text("")
                self.summary["YEAR_SELECT"].connect("changed", self._on_year_changed)
                hbox.pack_start(self.summary["YEAR_SELECT"], False, False, 6)
                vbox.pack_start(hbox, False, False, 4)

                self.summary["YEARLY_STATISTICS"] = Figure()
                canvas = FigureCanvas(self.summary["YEARLY_STATISTICS"])
                canvas.set_size_request(800, 250)
                canvas.show()
                vbox.pack_start(canvas, True, True, 4)

        # Summary tab label and icon.
        hbox = Gtk.HBox(False, 0)
        label = Gtk.Label("Summary  ")
        icon = Gtk.Image.new_from_stock(Gtk.STOCK_INDEX, Gtk.IconSize.MENU)
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(icon, False, False, 0)
        hbox.show_all()

        self.notebook.insert_page(vbox, hbox, 0)  # Append as a new tab
        self.notebook.show_all()

        return

    def on_year_changed(self, combo):
        """ Re-plot the statistics for the year selected by the user. """

        # Clear figure
        self.summary["YEARLY_STATISTICS"].clf()
        self.summary["YEARLY_STATISTICS"].canvas.draw()

        # Get year to show statistics for.
        year = combo.get_active_text()
        try:
            year = int(year)
        except ValueError:
            # Empty year string.
            return

        # Number of contacts made each month
        contact_count_plot = self.summary["YEARLY_STATISTICS"].add_subplot(121)
        contact_count = self._get_annual_contact_count(year)

        # x-axis formatting based on the date
        contact_count_plot.bar(list(contact_count.keys()), list(contact_count.values()), color="k", width=15, align="center")
        formatter = DateFormatter("%b")
        contact_count_plot.xaxis.set_major_formatter(formatter)
        month_locator = MonthLocator()
        contact_count_plot.xaxis.set_major_locator(month_locator)
        contact_count_plot.set_ylabel("Number of QSOs")

        # Set x-axis upper limit based on the current month.
        contact_count_plot.xaxis_date()
        contact_count_plot.set_xlim([date(year-1, 12, 16), date(year, 12, 15)])  # Make a bit of space either side of January and December of the selected year.

        # Pie chart of all the modes used.
        mode_count_plot = self.summary["YEARLY_STATISTICS"].add_subplot(122)
        mode_count = self._get_annual_mode_count(year)
        (patches, texts, autotexts) = mode_count_plot.pie(list(mode_count.values()), labels=mode_count.keys(), autopct='%1.1f%%', shadow=False)
        for p in patches:
            # Make the patches partially transparent.
            p.set_alpha(0.75)
        mode_count_plot.set_title("Modes used")

        self.summary["YEARLY_STATISTICS"].canvas.draw()

        return

    def find_year_bounds(self):
        """ Find the years of the oldest and newest QSOs across all logs in the logbook. """

        c = self.logbook.connection.cursor()
        max_years = []
        min_years = []
        for log in self.logbook.logs:
            query = "SELECT min(QSO_DATE), max(QSO_DATE) FROM %s" % (log.name)
            c.execute(query)
            years = c.fetchone()
            if years[0] and years[1]:
                min_years.append(int(years[0][:4]))
                max_years.append(int(years[1][:4]))

        if len(min_years) == 0 or max_years == 0:
            return None, None
        else:
            # Return the min and max across all logs.
            return min(min_years), max(max_years)

    def get_annual_contact_count(self, year):
        """ Find the total number of contacts made in each month in the specified year. """

        contact_count = {}
        c = self.logbook.connection.cursor()

        for log in self.logbook.logs:
            query = "SELECT QSO_DATE, count(QSO_DATE) FROM %s WHERE QSO_DATE >= %d0101 AND QSO_DATE < %d0101 GROUP by QSO_DATE" % (log.name, year, year+1)
            c.execute(query)
            xy = c.fetchall()

            for i in range(len(xy)):
                date_str = xy[i][0]
                y = int(date_str[0:4])
                m = int(date_str[4:6])
                date = datetime(y, m, 1)  # Collect all contacts together by month.
                if date in contact_count.keys():
                    contact_count[date] += xy[i][1]
                else:
                    contact_count[date] = xy[i][1]

        return contact_count

    def get_annual_mode_count(self, year):
        """ Find the total number of contacts made with each mode in a specified year. """

        mode_count = {}

        for log in self.logbook.logs:
            query = "SELECT MODE, count(MODE) FROM %s WHERE QSO_DATE >= %d0101 AND QSO_DATE < %d0101 GROUP by MODE" % (log.name, year, year+1)
            c = self.logbook.connection.cursor()
            c.execute(query)
            xy = c.fetchall()

            for i in range(len(xy)):
                mode = xy[i][0]
                if mode == "":
                    mode = "Unspecified"

                # Add to running total
                if mode in mode_count.keys():
                    mode_count[mode] += xy[i][1]
                else:
                    mode_count[mode] = xy[i][1]

        return mode_count

    def update(self):
        """ Update the information presented on the summary page. """

        self.summary["LOG_COUNT"].set_label(str(self.logbook.log_count))
        self.summary["QSO_COUNT"].set_label(str(self.logbook.record_count))
        try:
            t = datetime.fromtimestamp(getmtime(self.logbook.path)).strftime("%d %B %Y @ %H:%M")
            self.summary["DATE_MODIFIED"].set_label(str(t))
        except (IOError, OSError) as e:
            logging.exception(e)
        return
