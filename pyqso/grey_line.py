#!/usr/bin/env python
# File: grey_line.py

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
import numpy
import matplotlib
matplotlib.rcParams['font.size'] = 10.0
from mpl_toolkits.basemap import Basemap
from datetime import datetime
from backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

class GreyLine(Gtk.VBox):
   
   def __init__(self, root_window):
         
      Gtk.VBox.__init__(self, spacing=2)

      self.fig = matplotlib.figure.Figure()
      self.canvas = FigureCanvas(self.fig) # For embedding in the Gtk application
      self.pack_start(self.canvas, True, True, 0)

      self.root_window = root_window
      self.refresh_event = GObject.timeout_add(1800000, self.draw) # Re-draw the grey line automatically after 30 minutes (if the grey line tool is visible).

      self.show_all()

      return

   def draw(self):
      if(self.root_window.toolbox.tools.get_current_page() != 1 or not self.root_window.toolbox.get_visible()):
         # Don't re-draw if the grey line is not visible.
         return True # We need to return True in case this is method was called by a timer event.
      else:
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

         return True

