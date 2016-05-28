Introduction
============

Overview
--------

`PyQSO <http://christianjacobs.uk/pyqso>`_ is a logging tool for amateur radio operators. It provides a
simple graphical interface through which users can manage information
about the contacts/QSOs they make with other operators on the air. All
information is stored in a light-weight SQL database. Other key features
include:

-  Customisable interface (e.g. only show callsign and frequency
   information).

-  Import and export logs in ADIF format.

-  Perform callsign lookups and auto-fill data fields using the qrz.com and hamqth.com online databases.

-  Sort the logs by individual fields.

-  Print a hard-copy of logs, or print to PDF.

-  Connect to Telnet-based DX clusters.

-  Progress tracker for the DXCC award.

-  Grey line plotter.

-  Filter out QSOs based on the callsign field (e.g. only display
   contacts with callsigns beginning with "M6").

-  Remove duplicate QSOs.

-  Basic support for the Hamlib library.

The source code for PyQSO, written in Python (version 3.x), is available for download from the `GitHub repository <https://github.com/ctjacobs/pyqso>`_.

Data storage model
------------------

Many amateur radio operators choose to store all the contacts they ever
make in a single *logbook*, whereas others keep a separate logbook for
each year, for example. Each logbook may be divided up to form multiple
distinct *logs*, perhaps one for casual repeater contacts and another
for DX'ing. Finally, each log can contain multiple *records*. PyQSO is
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

PyQSO is free software, released under the `GNU General Public License <http://www.gnu.org/licenses/gpl-3.0.en.html>`_. Please see the file called ``COPYING`` for more information. A copyright year range of the form YYYY-ZZZZ specifies every single year from YYYY to ZZZZ inclusive (for example, 2012-2016 means 2012, 2013, 2014, 2015, 2016).

Contact
-------

If you have any comments or questions about PyQSO, please send them via email to Christian Jacobs (2E0ICL) at christian@christianjacobs.uk. Bug reports and feature requests can be made via the `issue tracker <https://github.com/ctjacobs/pyqso/issues>`_.

Structure of this documentation
-------------------------------

The structure of this documentation is as follows. The section on `Getting Started <getting_started.html>`_ provides information on the PyQSO installation process through to creating a new logbook (or opening an existing one). The `Log Management <log_management.html>`_ section explains how to create a log in the logbook, as well as the basic operations that users can perform with existing logs, such as printing, importing from/exporting to ADIF format, and sorting. The `Record Management <record_management.html>`_ section deals with the bottom layer of the three-tier model - the creation, deletion, and modification of QSO records in a log. The `Toolbox <toolbox.html>`_ section introduces the PyQSO toolbox which contains three tools that are useful to amateur radio operators: a DX cluster, a grey line plotter, and an awards progress tracker. Finally, the `Preferences <preferences.html>`_ section explains how users can set up Hamlib support and show/hide various fields in a log, along with several other user preferences that can be set via the Preferences dialog window. A `keyboard shortcuts list <shortcuts.html>`_ is also available for reference.

