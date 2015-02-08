| 

Introduction
============

Overview
--------

PyQSO is a logging tool for amateur radio operators. It provides a
simple graphical interface through which users can manage information
about the contacts/QSOs they make with other operators on the air. All
information is stored in a light-weight SQL database. Other key features
include:

-  Customisable interface (e.g. only show callsign and frequency
   information).

-  Import and export logs in ADIF format.

-  Perform callsign lookups and auto-fill data fields using the qrz.com
   database.

-  Sort the logs by individual fields.

-  Print a hard-copy of logs, or print to PDF.

-  Connect to Telnet-based DX clusters.

-  Progress tracker for the DXCC award.

-  Grey line plotter.

-  Filter out QSOs based on the callsign field (e.g. only display
   contacts with callsigns beginning with “M6”).

-  Remove duplicate QSOs.

-  Basic support for the Hamlib library.

The source code for PyQSO is available for download at:

``https://github.com/ctjacobs/pyqso``

Data storage model
------------------

Many amateur radio operators choose to store all the contacts they ever
make in a single *logbook*, whereas others keep a separate logbook for
each year, for example. Each logbook may be divided up to form multiple
distinct *logs*, perhaps one for casual repeater contacts and another
for DX’ing. Finally, each log can contain multiple *records*. PyQSO is
based around this three-tier model for data storage, going from logbooks
at the top to individual records at the bottom.

Rather than storing each log in a separate file, a single database can
hold several logs together; in PyQSO, a database is therefore analogous
to a logbook. Within a database the user can create multiple tables
which are analogous to the logs. Within each table the user can
create/modify/delete records which are analogous to the records in each
log.

Licensing
---------

PyQSO is free software, released under the GNU General Public License.
Please see the file called COPYING for more information.

Structure of this manual
------------------------

The structure of this manual is as follows. Chapter
[chap:getting:sub:`s`\ tarted] is all about getting started with PyQSO –
from the installation process through to creating a new logbook (or
opening an existing one). Chapter [chap:log:sub:`m`\ anagement] explains
how to create a log in the logbook, as well as the basic operations that
users can perform with existing logs, such as printing, importing
from/exporting to ADIF format, and sorting. Chapter
[chap:record:sub:`m`\ anagement] deals with the bottom layer of the
three-tier model – the creation, deletion, and modification of QSO
records in a log. Chapter [chap:toolbox] introduces the PyQSO toolbox
which contains three tools that are useful to amateur radio operators: a
DX cluster, a grey line plotter, and an awards progress tracker.
Finally, Chapter [chap:preferences] explains how users can set up Hamlib
support and show/hide various fields in a log, along with several other
user preferences that can be set via the Preferences dialog window.

Getting started
===============

System requirements
-------------------

It is recommended that users run PyQSO on the Linux operating system,
since all development and testing of PyQSO takes place there.

As the name suggests, PyQSO is written primarily in the Python
programming language. The graphical user interface has been built using
the GTK+ library through the PyGObject bindings. PyQSO also uses an
SQLite embedded database to manage all the contacts an amateur radio
operator makes. Users must therefore make sure that the Python
interpreter and any additional software dependencies are satisfied
before PyQSO can be run successfully. The list of software packages that
PyQSO depends on is provided in the README file.

Installation and running
------------------------

Assuming that the current working directory is PyQSO’s base directory
(the directory that the Makefile is in), PyQSO can be installed via the
terminal with the following command:

``make install``

Note: ‘sudo’ may be needed for this. Once installed, the following
command will run PyQSO:

``pyqso``

Alternatively, PyQSO can be run (without installing) with:

``python bin/pyqso``

from PyQSO’s base directory.

Command-line options
~~~~~~~~~~~~~~~~~~~~

There are several options available when executing PyQSO from the
command-line.

Open a specified logbook file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to being able to open a new or existing logbook through the
graphical interface, users can also specify a logbook file to open at
the command line with the ``-l`` or ``–logbook`` option. For example, to
open a logbook file called ``mylogbook.db``, use the following command:

``pyqso –logbook /path/to/mylogbook.db``

If the file does not already exist, PyQSO will create it.

Debugging mode
^^^^^^^^^^^^^^

Running PyQSO with the ``-d`` or ``–debug`` flag enables the debugging
mode:

``pyqso –debug``

All debugging-related messages are written to a file called pyqso.debug,
located in the current working directory.

Opening a new or existing logbook
---------------------------------

Logbooks are SQL databases, and as such they are accessed with a
database connection. To create a connection and open the logbook, click
``Open a New or Existing Logbook...`` in the ``Logbook`` menu, and
either:

-  Find and select an existing logbook database file (which usually has
   a ``.db`` file extension), and click ``Open`` to create the database
   connection; or

-  Create a new database by entering a (non-existing) file name and
   clicking ``Open``. The logbook database file (and a connection to it)
   will then be created automatically.

Once the database connection has been established, the database file
name will appear in the status bar. All logs in the logbook will be
opened automatically, and the interface will look something like the one
shown in Figure [fig:log:sub:`v`\ iew\ :sub:`w`\ ith\ :sub:`a`\ wards].

|The PyQSO main window, showing the records in a log called
``repeater_contacts``, and the awards tool in the toolbox below it.|
[fig:log:sub:`v`\ iew\ :sub:`w`\ ith\ :sub:`a`\ wards]

Closing a logbook
-----------------

A logbook can be closed (along with its corresponding database
connection) by clicking the ``Close Logbook`` button in the toolbar, or
by clicking ``Close Logbook`` in the ``Logbook`` menu.

Log management
==============

**Note 1:** All the operations described below assume that a logbook is
already open.

**Note 2:** Any modifications made to the logs are permanent. Users
should make sure they keep up-to-date backups.

Creating a new log
------------------

To create a new log, click ``New Log`` in the ``Logbook`` menu and enter
the desired name of the log (e.g. repeater\_contacts, dx, mobile\_log).
Alternatively, use the shortcut key combination ``Ctrl + N``.

The log name must be unique (i.e. it cannot already exist in the
logbook). Furthermore, it can only be composed of alphanumeric
characters and the underscore character, and the first character in the
name must not be a number.

Note: When logs are stored in the database file, field/column names from
the ADIF standard are used. However, please note that only the following
subset of all the ADIF fields is considered: CALL, QSO\_DATE, TIME\_ON,
FREQ, BAND, MODE, TX\_PWR, RST\_SENT, RST\_RCVD, QSL\_SENT, QSL\_RCVD,
NOTES, NAME, ADDRESS, STATE, COUNTRY, DXCC, CQZ, ITUZ, IOTA. Visit
http://adif.org/ for more information about these fields.

Renaming a log
--------------

To rename the currently selected log, click ``Rename Selected Log`` in
the ``Logbook`` menu. Remember that the log’s new name cannot be the
same as another log in the logbook.

Deleting a log
--------------

To delete the currently selected log, click ``Delete Selected Log`` in
the ``Logbook`` menu. As with all database operations in PyQSO, this is
permanent and cannot be undone.

Importing and exporting a log
-----------------------------

While PyQSO stores logbooks in SQL format, it is possible to export
individual logs in the well-known ADIF format. Select the log to export,
and click ``Export Log`` in the ``Logbook`` menu.

Similarly, records can be imported from an ADIF file. Upon importing,
users can choose to store the records in a new log, or append them to an
existing log in the logbook. To import, click ``Import Log`` in the
``Logbook`` menu.

Note that all data must conform to the ADIF standard, otherwise it will
be ignored.

Printing a log
--------------

Due to restrictions on the page width, only a selection of field names
will be printed: callsign, date, time, frequency, and mode.

Filtering by callsign
---------------------

Entering an expression such as ``xyz`` into the ``Filter by callsign``
box will instantly filter out all records whose callsign field does not
contain ``xyz``.

Sorting by field
----------------

To sort a log by a particular field name, left-click the column header
that contains that field name. By default, it is the ``Index`` field
that is sorted in ascending order.

Record management
=================

**Note:** Any modifications made to the records are permanent. Users
should make sure they keep up-to-date backups.

Creating a new record (QSO)
---------------------------

A new QSO can be added by either:

-  Clicking the ``Add Record`` button in the toolbar.

-  Pressing ``Ctrl + R``.

-  Clicking ``Add Record...`` in the ``Records`` menu.

A dialog window will appear where details of the QSO can be entered (see
Figure [fig:edit:sub:`r`\ ecord]). Note that the current date and time
are filled in automatically. When ready, click ``OK`` to save the
changes.

|Record dialog used to add new records and edit existing ones.|
[fig:edit:sub:`r`\ ecord]

Callsign lookup
~~~~~~~~~~~~~~~

PyQSO can also resolve station-related information (e.g. the operator’s
name, address, and ITU Zone) by clicking the ``Lookup on qrz.com``
button adjacent to the Callsign data entry box. Note that the user must
first supply their qrz.com account information in the preferences dialog
window.

Editing a record
----------------

An existing record can be edited by:

-  Double-clicking on it.

-  Selecting it and clicking the ``Edit Record`` button in the toolbar.

-  Selecting it and clicking ``Edit Selected Record...`` in the
   ``Records`` menu.

This will bring up the same dialog window as before.

Deleting a record
-----------------

An existing record can be deleted by:

-  Selecting it and clicking the ``Delete Record`` button in the
   toolbar.

-  Selecting it and pressing the ``Delete`` key.

-  Selecting it and clicking ``Delete Selected Record...`` in the
   ``Records`` menu.

Removing duplicate records
--------------------------

PyQSO can find and delete duplicate records in a log. A record is a
duplicate of another if its data in the Callsign, Date, Time, Frequency,
and Mode fields are the same. Click ``Remove Duplicate Records`` in the
``Records`` menu.

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

Preferences
===========

PyQSO user preferences are stored in a configuration file located at
``~/.pyqso.ini``, where ``~`` denotes the user’s home directory.

General
-------

Under the ``General`` tab, the user can choose to show the toolbox (see
Chapter [chap:toolbox]) when PyQSO is started.

The user can also enter their login details to access the qrz.com
database. Note that these details are currently stored in plain text
(unencrypted) format.

View
----

Not all the available fields have to be displayed in the logbook. The
user can choose to hide a subset of them by unchecking them in the
``View`` tab. PyQSO must be restarted in order for any changes to take
effect.

Hamlib support
--------------

PyQSO features rudimentary support for the Hamlib library. The name and
path of the radio device connected to the user’s computer can be
specified in the ``Hamlib`` tab of the preferences dialog. Upon adding a
new record to the log, PyQSO will use Hamlib to retrieve the current
frequency that the radio device is set to and automatically fill in the
Frequency field.

.. |The PyQSO main window, showing the records in a log called ``repeater_contacts``, and the awards tool in the toolbox below it.| image:: images/log_with_awards.png
.. |Record dialog used to add new records and edit existing ones.| image:: images/edit_record.png
.. |The DX cluster frame.| image:: images/dx_cluster.png
.. |The grey line tool.| image:: images/grey_line.png
.. |The award progress tracker.| image:: images/awards.png
