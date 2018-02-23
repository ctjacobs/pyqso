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
    import cartopy
    logging.info("Using version %s of cartopy." % (cartopy.__version__))
    from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
    have_necessary_modules = True
except ImportError as e:
    logging.warning(e)
    logging.warning("Could not import a non-standard Python module needed by the GreyLine class, or the version of the non-standard module is too old. Check that all the PyQSO dependencies are satisfied.")
    have_necessary_modules = False
try:
    import geocoder
    have_geocoder = True
except ImportError:
    logging.warning("Could not import the geocoder module!")
    have_geocoder = False


class Point:
    """ A point on the grey line map. """
    def __init__(self, name, latitude, longitude, style="yo"):
        """ Set up the point's attributes.

        :arg str name: The name that identifies the point.
        :arg float latitude: The latitude of the point on the map.
        :arg float longitude: The longitude of the point on the map.
        :arg str style: The style of the point when plotted. By default it is a filled yellow circle.
        """

        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.style = style
        return


class GreyLine:

    """ A tool for visualising the grey line. """

    def __init__(self, application):
        """ Set up the drawing canvas and the timer which will re-plot the grey line every 30 minutes.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """
        logging.debug("Setting up the grey line...")

        self.application = application
        self.builder = self.application.builder
        self.points = []

        if(have_necessary_modules):
            self.fig = matplotlib.figure.Figure()
            self.canvas = FigureCanvas(self.fig)  # For embedding in the Gtk application
            self.builder.get_object("greyline").pack_start(self.canvas, True, True, 0)
            self.refresh_event = GObject.timeout_add(1800000, self.draw)  # Re-draw the grey line automatically after 30 minutes (if the grey line tool is visible).

        # Plot the QTH coordinates, if available.
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser('~/.config/pyqso/preferences.ini')) != [])
        (section, option) = ("general", "show_qth")
        if(have_config and config.has_option(section, option)):
            if(config.getboolean(section, option)):
                try:
                    qth_name = config.get("general", "qth_name")
                    qth_latitude = float(config.get("general", "qth_latitude"))
                    qth_longitude = float(config.get("general", "qth_longitude"))
                    self.add_point(qth_name, qth_latitude, qth_longitude, "ro")
                except ValueError:
                    logging.warning("Unable to get the QTH name, latitude and/or longitude. The QTH will not be pinpointed on the grey line map. Check preferences?")

        self.builder.get_object("greyline").show_all()

        logging.debug("Grey line ready!")

        return

    def add_point(self, name, latitude, longitude, style="yo"):
        """ Add a point and re-draw the map.

        :arg str name: The name that identifies the point.
        :arg float latitude: The latitude of the point on the map.
        :arg float longitude: The longitude of the point on the map.
        :arg str style: The style of the point when plotted. By default it is a filled yellow circle.
        """
        p = Point(name, latitude, longitude, style)
        self.points.append(p)
        self.draw()
        return

    def pinpoint(self, r):
        """ Pinpoint the location of a QSO on the grey line map based on the COUNTRY field.

        :arg r: The QSO record containing the location to pinpoint.
        """

        if(have_geocoder):
            country = r["COUNTRY"]
            callsign = r["CALL"]

            # Get the latitude-longitude coordinates of the country.
            if(country):
                try:
                    g = geocoder.google(country)
                    latitude, longitude = g.latlng
                    logging.debug("QTH coordinates found: (%s, %s)", str(latitude), str(longitude))
                    self.add_point(callsign, latitude, longitude)
                except ValueError:
                    logging.exception("Unable to lookup QTH coordinates.")
                except Exception:
                    logging.exception("Unable to lookup QTH coordinates. Check connection to the internets? Lookup limit reached?")

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
                # Set up the world map.
                self.fig.clf()
                ax = self.fig.add_subplot(111, projection=cartopy.crs.PlateCarree())
                ax.set_extent([-180, 180, -90, 90])
                ax.gridlines()
                ax.add_feature(cartopy.feature.LAND)
                ax.add_feature(cartopy.feature.OCEAN)
                ax.add_feature(cartopy.feature.COASTLINE)
                ax.add_feature(cartopy.feature.BORDERS, alpha=0.25)

                # TODO: Re-draw the grey line.

                # Plot points on the map.
                if(self.points):
                    logging.debug("Plotting QTHs on the map...")
                    for p in self.points:
                        ax.plot(p.longitude, p.latitude, p.style, transform=cartopy.crs.PlateCarree())
                        ax.text(p.longitude+0.01*p.longitude, p.latitude+0.01*p.latitude, p.name, color="black", size="small", weight="bold")

                return True
        else:
            return False  # Don't try to re-draw the canvas if the necessary modules to do so could not be imported.
