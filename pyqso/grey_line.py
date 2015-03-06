#!/usr/bin/env python
# File: grey_line.py

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
from datetime import datetime
try:
   import numpy
   import matplotlib
   logging.debug("Using version %s of matplotlib." % (matplotlib.__version__))
   matplotlib.use('Agg')
   matplotlib.rcParams['font.size'] = 10.0
   from mpl_toolkits.basemap import Basemap
   from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
   have_necessary_modules = True
except ImportError:
   logging.error("Could not import a non-standard Python module needed by the GreyLine class, or the version of the non-standard module is too old. Check that all the PyQSO dependencies are satisfied.")
   have_necessary_modules = False

class GreyLine(Gtk.VBox):
   """ A tool for visualising the grey line. """
   
   def __init__(self, parent):
      """ Set up the drawing canvas and the timer which will re-plot the grey line every 30 minutes. """
      logging.debug("Setting up the grey line...") 
      Gtk.VBox.__init__(self, spacing=2)
      self.parent = parent

      if(have_necessary_modules):
         self.fig = matplotlib.figure.Figure()
         self.canvas = FigureCanvas(self.fig) # For embedding in the Gtk application
         self.pack_start(self.canvas, True, True, 0)
         self.refresh_event = GObject.timeout_add(1800000, self.draw) # Re-draw the grey line automatically after 30 minutes (if the grey line tool is visible).

      self.show_all()

      logging.debug("Grey line ready!") 

      return

   def draw(self):
      """ Draw the world map and the grey line on top of it. This method always returns True to satisfy the GObject timer. """

      if(have_necessary_modules):
         if(self.parent.toolbox.tools.get_current_page() != 1 or not self.parent.toolbox.get_visible()):
            # Don't re-draw if the grey line is not visible.
            return True # We need to return True in case this is method was called by a timer event.
         else:
            logging.debug("Drawing the grey line...") 
            # Re-draw the grey line
            self.fig.clf()
            sub = self.fig.add_subplot(111)

            # Draw the map of the world. This is based on the example from:
            # http://matplotlib.org/basemap/users/examples.html
            m = Basemap(projection='mill', lon_0=0, ax=sub, resolution='c', fix_aspect=False)
            m.drawcountries(linewidth=0.5)
            m.drawcoastlines(linewidth=0.5)
            m.drawparallels(numpy.arange(-90, 90, 30), labels=[1, 0, 0, 0])
            m.drawmeridians(numpy.arange(m.lonmin, m.lonmax+30, 60), labels=[0, 0, 0, 1])
            m.drawmapboundary(fill_color='lightblue')
            m.fillcontinents(color='darkgreen', lake_color='lightblue')
            m.nightshade(datetime.utcnow()) # Add in the grey line using UTC time. Note that this requires NetCDF.
            logging.debug("Grey line drawn.") 
            return True
      else:
         return False # Don't try to re-draw the canvas if the necessary modules to do so could not be imported.

