#!/bin/sh

#    Copyright (C) 2013 Christian T. Jacobs.

#    This file is part of PyQSO.

#    PyQSO is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyQSO is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyQSO.  If not, see <http://www.gnu.org/licenses/>.

.PHONY: input clean install docs test

input: 	clean install docs

install:
	echo "*** Installing PyQSO"
	python3 setup.py install

docs:
	echo "*** Building the documentation"
	cd docs; make html; cd ..

test:
	echo "*** Running the unit tests"
	python3 -m unittest discover --start-directory=pyqso --pattern=*.py --verbose

clean:
	echo "*** Cleaning docs directory"
	cd docs; make clean; cd ..
	echo "*** Cleaning pyqso directory"
	rm -f ADIF.test_*.adi; cd pyqso; rm -f *.pyc ADIF.test_*.adi; cd ..
	echo "*** Removing build directory"
	rm -rf build
