    Copyright (C) 2013 Christian T. Jacobs.

    This file is part of PyQSO.

    PyQSO is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyQSO is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyQSO.  If not, see <http://www.gnu.org/licenses/>.

PyQSO
=====

PyQSO is a contact logging tool for amateur radio operators.

[![Build Status](https://travis-ci.org/njohnsn/pyqso.svg)](https://travis-ci.org/njohnsn/pyqso)
[![Documentation Status](https://readthedocs.org/projects/pyqso/badge/?version=latest)](https://readthedocs.org/projects/pyqso/?badge=latest)

Installation and running
------------------------

Assuming that the current working directory is PyQSO's base directory (the directory that the Makefile is in), PyQSO can be installed via the terminal with the following command:

   `make install`

Note: 'sudo' may be needed for this. Once installed, the following command will run PyQSO:
   
   `pyqso`

Alternatively, PyQSO can be run (without installing) with:

   `python bin/pyqso`

from PyQSO's base directory.

Documentation
-------------

The PyQSO documentation is stored in the `docs` directory. It can be built with the following command:

   `make docs`

which will produce an HTML version of the documentation in `docs/build/html` that can be opened in a web browser.

Alternatively, a ready-built version of the PyQSO documentation can be found on [Read the Docs](http://pyqso.readthedocs.org/en/latest/).

Dependencies
------------

PyQSO depends on the following Debian packages:

* gir1.2-gtk-3.0
* python2.7
* python-gi-cairo (for log printing purposes)

The following extra packages are necessary to enable the grey line tool:

* python-mpltoolkits.basemap
* python-numpy
* python-matplotlib (version 1.3.0 or later)

The following extra package is necessary to enable Hamlib support:

* python-libhamlib2

The following extra package is necessary to build the documentation:

* python-sphinx

Contact
-------

If you have any comments or questions about PyQSO, please send them via email to <c.jacobs10@imperial.ac.uk>.

