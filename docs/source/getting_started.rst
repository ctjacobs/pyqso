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

