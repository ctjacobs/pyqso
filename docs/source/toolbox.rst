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

Click on the ``Connect to Telnet Server`` button and enter the DX server
details in the dialog that appears. If no port is specified, PyQSO will
use the default value of 23. A username and password may also need to be
supplied. Once connected, the server output will appear in the DX
cluster frame (see Figure [fig:dx:sub:`c`\ luster]). A command can also
be sent to the server by typing it into the entry box and clicking the
adjacent ``Send Command`` button.

|The DX cluster frame.| [fig:dx:sub:`c`\ luster]

Grey line
---------

The grey line tool (see Figure [fig:grey:sub:`l`\ ine]) can be used to
check which parts of the world are in darkness. The position of the grey
line is automatically updated every 30 minutes.

|The grey line tool.| [fig:grey:sub:`l`\ ine]

Awards
------

The awards progress tracker (see Figure [fig:awards]) updates its data
each time a record is added, deleted, or modified. Currently only the
DXCC award is supported (visit http://www.arrl.org/dxcc for more
information).

|The award progress tracker.| [fig:awards]

