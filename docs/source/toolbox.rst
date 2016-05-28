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
be sent to the server by typing it into the entry box beneath the server output, and clicking the
adjacent ``Send Command`` button.

   .. _figure:dx_cluster:
   .. figure::  images/dx_cluster.png
      :align:   center
      
      The DX cluster frame.

Grey line
---------

The grey line tool (see figure:grey_line_) can be used to
check which parts of the world are in darkness. The position of the grey
line is automatically updated every 30 minutes.

   .. _figure:grey_line:
   .. figure::  images/grey_line.png
      :align:   center
      
      The grey line tool.

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

