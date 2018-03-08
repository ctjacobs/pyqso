#!/usr/bin/env python3

#    Copyright (C) 2013-2018 Christian Thomas Jacobs.

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
import re
from os.path import expanduser
from datetime import datetime
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
    from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3
    have_necessary_modules = True
except ImportError as e:
    logging.warning(e)
    logging.warning("Could not import a non-standard Python module needed by the WorldMap class, or the version of the non-standard module is too old. Check that all the PyQSO dependencies are satisfied.")
    have_necessary_modules = False
try:
    import geocoder
    have_geocoder = True
except ImportError:
    logging.warning("Could not import the geocoder module!")
    have_geocoder = False


class NavigationToolbar(NavigationToolbar2GTK3):
    toolitems = [t for t in NavigationToolbar2GTK3.toolitems if t[0] in ("Home", "Zoom", "Save")]


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


class Maidenhead:

    """ The Maidenhead Locator System. """

    def __init__(self):
        self.upper = "ABCDEFGHIJKLMNOPQR"
        self.lower = "abcdefghijklmnopqrstuvwx"
        return

    def ll2gs(self, latitude, longitude):
        """ Convert latitude-longitude coordinates to a Maidenhead grid square locator.
        This is based on the code by Walter Underwood, K6WRU (https://ham.stackexchange.com/questions/221/how-can-one-convert-from-lat-long-to-grid-square).

        :arg float latitude: The latitude.
        :arg float longitude: The longitude.
        :rtype: str
        :returns: The Maidenhead grid square locator.
        """

        adjusted_latitude = latitude + 90
        adjusted_longitude = longitude + 180
        field_latitude = self.upper[int(adjusted_latitude/10)]
        field_longitude = self.upper[int(adjusted_longitude/20)]
        square_latitude = int(adjusted_latitude % 10)
        square_longitude = int((adjusted_longitude/2) % 10)

        return ("%s"*4) % (field_longitude, field_latitude, square_longitude, square_latitude)

    def gs2ll(self, grid_square):
        """ Convert a Maidenhead grid square locator to latitude-longitude coordinates.
        This is based on the gridSquareToLatLon function in HamGridSquare.js by Paul Brewer, KI6CQ (https://gist.github.com/DrPaulBrewer/4279e9d234a1bd6dd3c0), released under the MIT license.

        :arg str grid_square: The Maidenhead grid square locator.
        :rtype: tuple
        :returns: The latitude-longitude coordinates in a tuple.
        """

        m = re.match(r"^[A-X][A-X][0-9][0-9]$", grid_square)
        if(m):
            gs = m.group(0)
            latitude = self.latitude4(gs)+0.5
            longitude = self.longitude4(gs)+1.0
        else:
            m = re.match(r"^[A-X][A-X][0-9][0-9][a-x][a-x]$", grid_square)
            if(m):
                gs = m.group(0)
                latitude = self.latitude4(gs) + (1.0/60.0)*2.5*(ord(gs[5])-ord("a")+0.5)
                longitude = self.longitude4(gs) + (1.0/60.0)*5*(ord(gs[4])-ord("a")+0.5)
            else:
                raise ValueError("Unable to parse grid square string.")

        return (latitude, longitude)

    def latitude4(self, g):
        return 10*(ord(g[1]) - ord("A")) + int(g[3])-90

    def longitude4(self, g):
        return 20*(ord(g[0]) - ord("A")) + 2*int(g[2])-180


class WorldMap:

    """ A tool for visualising the world map. """

    def __init__(self, application):
        """ Set up the drawing canvas and the timer which will re-plot the world map every 30 minutes.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """
        logging.debug("Setting up the world map...")

        self.application = application
        self.builder = self.application.builder
        self.points = []

        if(have_necessary_modules):
            self.fig = matplotlib.figure.Figure()
            self.canvas = FigureCanvas(self.fig)  # For embedding in the Gtk application
            self.builder.get_object("worldmap").pack_start(self.canvas, True, True, 0)
            toolbar = NavigationToolbar(self.canvas, self.application.window)
            self.builder.get_object("worldmap").pack_start(toolbar, False, False, 0)
            self.refresh_event = GObject.timeout_add(1800000, self.draw)  # Re-draw the world map automatically after 30 minutes (if the world map tool is visible).

        # Add the QTH coordinates for plotting, if available.
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
                    logging.warning("Unable to get the QTH name, latitude and/or longitude. The QTH will not be pinpointed on the world map. Check preferences?")

        self.maidenhead = Maidenhead()
        self.grid_square_count = numpy.zeros((len(self.maidenhead.upper), len(self.maidenhead.upper)), dtype=bool)

        self.builder.get_object("worldmap").show_all()

        logging.debug("World map ready!")

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
        """ Pinpoint the location of a QSO on the world map based on the COUNTRY field.

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

        :returns: Always returns True to satisfy the GObject timer, unless the necessary WorldMap dependencies are not satisfied (in which case, the method returns False so as to not re-draw the canvas).
        :rtype: bool
        """

        if(have_necessary_modules):
            toolbox = self.builder.get_object("toolbox")
            tools = self.builder.get_object("tools")
            if(tools.get_current_page() != 1 or not toolbox.get_visible()):
                # Don't re-draw if the world map is not visible.
                return True  # We need to return True in case this is method was called by a timer event.
            else:
                # Set up the world map.
                logging.debug("Drawing the world map...")
                self.fig.clf()
                ax = self.fig.add_subplot(111, projection=cartopy.crs.PlateCarree())
                ax.set_extent([-180, 180, -90, 90])
                ax.set_aspect("auto")

                gl = ax.gridlines(draw_labels=True)
                gl.xlabels_top = False
                gl.ylabels_right = False
                gl.xformatter = cartopy.mpl.gridliner.LONGITUDE_FORMATTER
                gl.yformatter = cartopy.mpl.gridliner.LATITUDE_FORMATTER
                ax.add_feature(cartopy.feature.LAND, facecolor="green")
                ax.add_feature(cartopy.feature.OCEAN, color="skyblue")
                ax.add_feature(cartopy.feature.COASTLINE)
                ax.add_feature(cartopy.feature.BORDERS, alpha=0.4)

                # Draw the grey line. This is based on the code from the Cartopy Aurora Forecast example (http://scitools.org.uk/cartopy/docs/latest/gallery/aurora_forecast.html) and used under the Open Government Licence (http://scitools.org.uk/cartopy/docs/v0.15/copyright.html).
                logging.debug("Drawing the grey line...")
                dt = datetime.utcnow()
                axial_tilt = 23.5
                reference_solstice = datetime(2016, 6, 21, 22, 22)
                days_per_year = 365.2425
                seconds_per_day = 86400.0

                days_since_reference = (dt - reference_solstice).total_seconds()/seconds_per_day
                latitude = axial_tilt*numpy.cos(2*numpy.pi*days_since_reference/days_per_year)
                seconds_since_midnight = (dt - datetime(dt.year, dt.month, dt.day)).seconds
                longitude = -(seconds_since_midnight/seconds_per_day - 0.5)*360

                pole_longitude = longitude
                if latitude > 0:
                    pole_latitude = -90 + latitude
                    central_rotated_longitude = 180
                else:
                    pole_latitude = 90 + latitude
                    central_rotated_longitude = 0

                rotated_pole = cartopy.crs.RotatedPole(pole_latitude=pole_latitude, pole_longitude=pole_longitude, central_rotated_longitude=central_rotated_longitude)

                x = numpy.empty(360)
                y = numpy.empty(360)
                x[:180] = -90
                y[:180] = numpy.arange(-90, 90.)
                x[180:] = 90
                y[180:] = numpy.arange(90, -90., -1)

                ax.fill(x, y, transform=rotated_pole, color="black", alpha=0.5)

                # Plot points on the map.
                if(self.points):
                    logging.debug("Plotting QTHs on the map...")
                    for p in self.points:
                        ax.plot(p.longitude, p.latitude, p.style, transform=cartopy.crs.PlateCarree())
                        ax.text(p.longitude+0.02*p.longitude, p.latitude+0.02*p.latitude, p.name, color="white", size="small", weight="bold")

                # Draw Maidenhead grid squares.
                xx = numpy.linspace(-180, 180, len(list(self.maidenhead.upper))+1)
                yy = numpy.linspace(-90, 90, len(list(self.maidenhead.upper))+1)
                A = self.grid_square_count.copy()
                A[10, 10] = True
                A[12, 12] = True
                A[10, 5] = True
                A[9, 5] = True
                z = numpy.ma.masked_array(A, A == 0)
                ax.pcolormesh(xx, yy, z, transform=cartopy.crs.PlateCarree(), cmap='Purples', vmin=0, vmax=1, edgecolors="k", linewidth=2, alpha=0.6)
                for i in range(len(self.maidenhead.upper)):
                    for j in range(len(self.maidenhead.upper)):
                        text = self.maidenhead.upper[i]+self.maidenhead.upper[j]
                        ax.text((xx[i]+xx[i+1])/2.0, (yy[j]+yy[j+1])/2.0, text, ha="center", va="center", size=8, color="w")

                return True
        else:
            return False  # Don't try to re-draw the canvas if the necessary modules to do so could not be imported.
