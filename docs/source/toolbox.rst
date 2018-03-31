Toolbox
=======

The toolbox is hidden by default. To show it, click ``Toolbox`` in the
``View`` menu.

DX cluster
----------

A DX cluster is essentially a server through which amateur radio
operators can report and receive updates about QSOs that are in progress
across the bands. PyQSO is able to connect to a DX cluster that operates
using the Telnet protocol to provide a text-based alert service. As a
result of the many different Telnet-based software products that DX
clusters run, PyQSO currently outputs the raw data received from the DX
cluster rather than trying to parse it in some way.

Click on ``Connect to Telnet Server`` then ``New...`` in the ``Connection`` menu, and enter the DX server
details in the dialog that appears. If no port is specified, PyQSO will
use the default value of 23. A username and password may also need to be
supplied. Frequently used servers can be bookmarked for next time; bookmarked server details are stored in ``~/.config/pyqso/bookmarks.ini``, where ``~`` denotes the user's home directory.

Once connected, the server output will appear in the DX
cluster frame (see figure:dx_cluster_). A command can also
be sent to the server by typing it into the entry box beneath the server output and clicking the
adjacent ``Send Command`` button (or pressing the Enter key).

   .. _figure:dx_cluster:
   .. figure::  images/dx_cluster.png
      :align:   center
      
      The DX cluster frame.

World map
---------

The world map tool (see figure:world_map_) can be used to plot the QTH of your station and stations that you have contacted. It also features a grey line to check which parts of the world are in darkness. The position of the grey line is automatically updated every 30 minutes.

The user's QTH can be pin-pointed on the map by specifying the QTH's location (e.g. city name) and latitude-longitude coordinates in the preferences. If the `geocoder <https://pypi.python.org/pypi/geocoder>`_ library is installed then these coordinates can be filled in for you by clicking the lookup button after entering the QTH's name, otherwise the coordinates will need to be entered manually.

The location of a worked station may also be plotted by right-clicking on the relevant QSO in the main window and selecting ``Pinpoint`` from the popup menu.

   .. _figure:world_map:
   .. figure::  images/world_map.png
      :align:   center
      
      The world map tool with the user's QTH (e.g. Southampton) pin-pointed in red, and several other worked stations pin-pointed in yellow. Worked grid squares are shaded purple.

Awards
------

The awards progress tracker (see figure:awards_) updates its data
each time a record is added, deleted, or modified. Currently only the
DXCC award is supported (visit the `ARRL DXCC website <http://www.arrl.org/dxcc>`_ for more
information).

   .. _figure:awards:
   .. figure::  images/awards.png
      :align:   center
      
      The award progress tracker.

