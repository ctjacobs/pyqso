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
from mpl_toolkits.basemap import Basemap
from datetime import datetime
from matplotlib.figure import Figure
from backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

class GreyLine(Gtk.VBox):
   
   def __init__(self, root_window):
         
      Gtk.VBox.__init__(self, spacing=2)

      fig = Figure()
      sub = fig.add_subplot(111)

      # Draw the map of the world. This is based on the example from:
      # http://matplotlib.org/basemap/users/examples.html
      m = Basemap(projection='mill', lon_0=0, ax=sub, resolution='c', fix_aspect=False)
      m.drawcoastlines()
      m.drawparallels(numpy.arange(-90,90,30), labels=[1,0,0,0])
      m.drawmeridians(numpy.arange(m.lonmin,m.lonmax+30,60), labels=[0,0,0,1])

      m.drawmapboundary(fill_color='lightblue')
      m.fillcontinents(color='darkgreen', lake_color='lightblue')
      m.nightshade(datetime.utcnow()) # Add in the grey line using UTC time. Note that this requires NetCDF.

      canvas = FigureCanvas(fig) # For embedding in the Gtk application
      self.pack_start(canvas, True, True, 0)

      self.show_all()

      return

