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
from os import pardir
from os.path import basename, getmtime, expanduser, dirname, join, realpath
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

    def __init__(self, application):
        """ Create a summary page containing various statistics such as the number of logs in the logbook, the logbook's modification date, etc.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.application = application
        self.logbook = self.application.logbook
        self.builder = self.application.builder
        glade_file_path = join(realpath(dirname(__file__)), pardir, "res/pyqso.glade")
        self.builder.add_objects_from_file(glade_file_path, ("summary_page",))
        self.summary_page = self.builder.get_object("summary_page")

        self.items = {}

        # Database name in large font at the top of the summary page
        self.builder.get_object("database_name").set_markup("<span size=\"x-large\">%s</span>" % basename(self.logbook.path))
        self.items["LOG_COUNT"] = self.builder.get_object("log_count")
        self.items["QSO_COUNT"] = self.builder.get_object("qso_count")
        self.items["DATE_MODIFIED"] = self.builder.get_object("date_modified")

        # Yearly statistics
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])
        (section, option) = ("general", "show_yearly_statistics")
        if(have_config and config.has_option(section, option)):
            if(config.get("general", "show_yearly_statistics") == "True" and have_matplotlib):
                hbox = Gtk.HBox()
                label = Gtk.Label("Display statistics for year: ", halign=Gtk.Align.START)
                hbox.pack_start(label, False, False, 6)
                year_select = Gtk.ComboBoxText()
                min_year, max_year = self.get_year_bounds()
                if min_year and max_year:
                    for year in range(max_year, min_year-1, -1):
                        year_select.append_text(str(year))
                year_select.append_text("")
                year_select.connect("changed", self.on_year_changed)
                hbox.pack_start(year_select, False, False, 6)
                self.summary_page.pack_start(hbox, False, False, 4)

                self.items["YEARLY_STATISTICS"] = Figure()
                canvas = FigureCanvas(self.items["YEARLY_STATISTICS"])
                canvas.set_size_request(800, 250)
                canvas.show()
                self.summary_page.pack_start(canvas, True, True, 4)

        # Summary tab label and icon.
        tab = Gtk.HBox(homogeneous=False, spacing=0)
        label = Gtk.Label(label="Summary  ")
        icon = Gtk.Image.new_from_icon_name(Gtk.STOCK_INDEX, Gtk.IconSize.MENU)
        tab.pack_start(label, False, False, 0)
        tab.pack_start(icon, False, False, 0)
        tab.show_all()

        self.logbook.notebook.insert_page(self.summary_page, tab, 0)  # Append as a new tab
        self.logbook.notebook.show_all()

        return

    def on_year_changed(self, combo):
        """ Re-plot the statistics for the year selected by the user. """

        # Clear figure
        self.items["YEARLY_STATISTICS"].clf()
        self.items["YEARLY_STATISTICS"].canvas.draw()

        # Get year to show statistics for.
        year = combo.get_active_text()
        try:
            year = int(year)
        except ValueError:
            # Empty year string.
            return

        # Number of contacts made each month
        contact_count_plot = self.items["YEARLY_STATISTICS"].add_subplot(121)
        contact_count = self.get_annual_contact_count(year)

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
        mode_count_plot = self.items["YEARLY_STATISTICS"].add_subplot(122)
        mode_count = self.get_annual_mode_count(year)
        (patches, texts, autotexts) = mode_count_plot.pie(list(mode_count.values()), labels=mode_count.keys(), autopct='%1.1f%%', shadow=False)
        for p in patches:
            # Make the patches partially transparent.
            p.set_alpha(0.75)
        mode_count_plot.set_title("Modes used")

        self.items["YEARLY_STATISTICS"].canvas.draw()

        return

    def get_year_bounds(self):
        """ Find the years of the oldest and newest QSOs across all logs in the logbook.

        :returns: The years of the oldest and newest QSOs. The tuple (None, None) is returned if no QSOs have been made or no QSO dates have been specified.
        :rtype: tuple
        """

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

        if len(min_years) == 0 or len(max_years) == 0:
            return None, None
        else:
            # Return the min and max across all logs.
            return min(min_years), max(max_years)

    def get_annual_contact_count(self, year):
        """ Find the total number of contacts made in each month in the specified year.

        :arg int year: The year of interest.
        :returns: The total number of contacts made in each month of a given year.
        :rtype: dict
        """

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
        """ Find the total number of contacts made with each mode in a specified year.

        :arg int year: The year of interest.
        :returns: The total number of contacts made with each mode in a given year.
        :rtype: dict
        """

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

        self.items["LOG_COUNT"].set_label(str(self.logbook.log_count))
        self.items["QSO_COUNT"].set_label(str(self.logbook.record_count))
        try:
            t = datetime.fromtimestamp(getmtime(self.logbook.path)).strftime("%d %B %Y @ %H:%M")
            self.items["DATE_MODIFIED"].set_label(str(t))
        except (IOError, OSError) as e:
            logging.exception(e)
        return
