Preferences
===========

PyQSO user preferences are stored in a configuration file located at
``~/.config/pyqso/preferences.ini``, where ``~`` denotes the user's home directory.

General
-------

Under the ``General`` tab, the user can choose to:

-  Always show the toolbox (see the `Toolbox <toolbox.html>`_ section) when PyQSO is started.

-  Display yearly logbook statistics on the Summary page when a logbook is opened (see figure:summary_).

-  Open a default logbook file.

-  Keep the ``Add Record`` dialog window open after a new QSO is added, in preparation for the next QSO.

   .. _figure:summary:
   .. figure::  images/summary.png
      :align:   center
      
      The Summary page which appears after a logbook is opened. This presents some basic logbook statistics.

View
----

Not all the available fields have to be displayed in the logbook. The user can choose to hide a subset by unchecking them in the ``View`` tab. PyQSO must be restarted in order for any changes to take effect.

Records
-------

The records tab comprises options concerning the Add/Edit Record dialog window. It allows users to:

-  Use the UTC timezone when autocompleting the date and time fields.

-  Choose whether the band should be automatically determined from the frequency field.

-  Specify default values for the Power, Mode, and Submode fields.

-  Enter the QSO's frequency in a unit other than MHz (note that the frequency will always be presented in MHz in the main window, regardless of this preference).

-  Specify the callsign lookup settings.

Callsign lookup
~~~~~~~~~~~~~~~

The user can enter their login details to access the `qrz.com <http://qrz.com/>`_ or `hamqth.com <http://hamqth.com/>`_ database and perform callsign lookups. Note that these details are currently stored in plain text (unencrypted) format.

If the ``Ignore callsign prefixes and/or suffixes`` box is checked, then PyQSO will perform the callsign lookup whilst ignoring all prefixes (i.e. anything before a preceding "/" in the callsign) and the suffixes "P", "M", "A", "PM", "MM", "AM", and "QRP". For example, if the callsign to be looked up is F/MYCALL/QRP, only MYCALL will be looked up. If you get 'Callsign not found' errors, try enabling this option.

Import/Export
-------------

PyQSO currently supports the ``NOTES`` field in the ADIF specification, but not the ``COMMENTS`` field. When a user imports a log in ADIF format, they can choose to merge any existing text in the ``COMMENTS`` field with the ``NOTES`` field by checking the 'merge' checkbox. This way, no information in the ``COMMENTS`` field is discarded during the import process.

Hamlib support
--------------

PyQSO features rudimentary support for the `Hamlib <http://hamlib.sourceforge.net/>`_ library. The name and path of the radio device connected to the user's computer can be specified in the ``Hamlib`` tab of the preferences dialog. Upon adding a new record to the log, PyQSO will use Hamlib to retrieve the current frequency and mode that the radio device is set to and automatically fill in the Frequency and Mode fields.

World Map
---------

The user can pin-point their QTH on the world map by specifying the latitude-longitude coordinates (or looking them up based on the QTH's name, e.g. city name) in the ``World Map`` tab. Maidenhead grid squares can also be rendered, with worked grid squares shaded, which is particularly useful for satellite operating.
