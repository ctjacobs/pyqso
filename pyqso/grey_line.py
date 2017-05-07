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

from gi.repository import GObject
import logging
from datetime import datetime
from os.path import expanduser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
try:
    import numpy
    logging.info("Using version %s of numpy." % (numpy.__version__))
    import matplotlib
    logging.info("Using version %s of matplotlib." % (matplotlib.__version__))
    import mpl_toolkits.basemap
    logging.info("Using version %s of mpl_toolkits.basemap." % (mpl_toolkits.basemap.__version__))
    from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
    have_necessary_modules = True
except ImportError as e:
    logging.warning(e)
    logging.warning("Could not import a non-standard Python module needed by the GreyLine class, or the version of the non-standard module is too old. Check that all the PyQSO dependencies are satisfied.")
    have_necessary_modules = False


class GreyLine:

    """ A tool for visualising the grey line. """

    def __init__(self, application):
        """ Set up the drawing canvas and the timer which will re-plot the grey line every 30 minutes.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """
        logging.debug("Setting up the grey line...")

        self.application = application
        self.builder = self.application.builder

        # Get the QTH coordinates, if available.
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])
        (section, option) = ("general", "show_qth")
        self.show_qth = False
        if(have_config and config.has_option(section, option)):
            if(config.get("general", "show_qth") == "True"):
                self.show_qth = True
                try:
                    self.qth_name = config.get("general", "qth_name")
                    self.qth_latitude = float(config.get("general", "qth_latitude"))
                    self.qth_longitude = float(config.get("general", "qth_longitude"))
                except ValueError:
                    logging.warning("Unable to get the QTH name, latitude and/or longitude. The QTH will not be pinpointed on the grey line map. Check preferences?")
                    self.show_qth = False

        if(have_necessary_modules):
            self.fig = matplotlib.figure.Figure()
            self.canvas = FigureCanvas(self.fig)  # For embedding in the Gtk application
            self.builder.get_object("greyline").pack_start(self.canvas, True, True, 0)
            self.refresh_event = GObject.timeout_add(1800000, self.draw)  # Re-draw the grey line automatically after 30 minutes (if the grey line tool is visible).

        self.builder.get_object("greyline").show_all()

        logging.debug("Grey line ready!")

        return

    def draw(self):
        """ Draw the world map and the grey line on top of it.

        :returns: Always returns True to satisfy the GObject timer, unless the necessary GreyLine dependencies are not satisfied (in which case, the method returns False so as to not re-draw the canvas).
        :rtype: bool
        """

        if(have_necessary_modules):
            toolbox = self.builder.get_object("toolbox")
            tools = self.builder.get_object("tools")
            if(tools.get_current_page() != 1 or not toolbox.get_visible()):
                # Don't re-draw if the grey line is not visible.
                return True  # We need to return True in case this is method was called by a timer event.
            else:
                logging.debug("Drawing the grey line...")
                # Re-draw the grey line
                self.fig.clf()
                sub = self.fig.add_subplot(111)

                # Draw the map of the world. This is based on the example from:
                # http://matplotlib.org/basemap/users/examples.html
                m = mpl_toolkits.basemap.Basemap(projection='mill', lon_0=0, ax=sub, resolution='c', fix_aspect=False)
                m.drawcountries(linewidth=0.5)
                m.drawcoastlines(linewidth=0.5)
                m.drawparallels(numpy.arange(-90, 90, 30), labels=[1, 0, 0, 0])
                m.drawmeridians(numpy.arange(m.lonmin, m.lonmax+30, 60), labels=[0, 0, 0, 1])
                m.drawmapboundary(fill_color='lightblue')
                m.fillcontinents(color='darkgreen', lake_color='lightblue')
                m.nightshade(datetime.utcnow())  # Add in the grey line using UTC time. Note that this requires NetCDF.
                logging.debug("Grey line drawn.")

                # Pin-point QTH on the map.
                if(self.show_qth):
                    qth_x, qth_y = m(self.qth_longitude, self.qth_latitude)
                    m.plot(qth_x, qth_y, "yo")
                    sub.text(qth_x, qth_y, self.qth_name, color='yellow')

                return True
        else:
            return False  # Don't try to re-draw the canvas if the necessary modules to do so could not be imported.
