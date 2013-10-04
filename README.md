    File: README.md
    Copyright (C) 2013 Christian Jacobs.

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

PyQSO is a general-purpose contact logging tool for amateur radio operators.

Assuming that the current working directory is PyQSO's base directory (the directory that the Makefile is in), PyQSO can be installed via the terminal with the following command:

   `make install`

Note: 'sudo' may be needed for this. Once installed, the following command will run PyQSO:
   
   pyqso

Alternatively, PyQSO can be run with:

   `python bin/pyqso`

from PyQSO's base directory.

The PyQSO user manual is stored as a LaTeX source file in the doc/ directory. It can be compiled with the following command:

   `make manual`

which will produce the manual.pdf file.

Dependencies
------------

PyQSO depends on:

* gir1.2-gtk-3.0
* python-mpltoolkits.basemap
* python-numpy
* python-matplotlib (version 1.3.0)

