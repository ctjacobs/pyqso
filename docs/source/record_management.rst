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
figure:edit_record_). Note that the current date and time
are filled in automatically. When ready, click ``OK`` to save the
changes.

   .. _figure:edit_record:
   .. figure::  images/edit_record.png
      :align:   center
      
      Record dialog used to add new records and edit existing ones.
      
Callsign lookup
~~~~~~~~~~~~~~~

PyQSO can also resolve station-related information (e.g. the operator's
name, address, and ITU Zone) by clicking the ``Callsign lookup``
button adjacent to the Callsign data entry box. Note that the user must
first supply their `qrz.com <http://qrz.com/>`_ or `hamqth.com <http://hamqth.com/>`_ account information in the preferences dialog
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
