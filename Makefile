#!/usr/bin/env python
# File: Makefile

#    Copyright (C) 2013 Christian Jacobs.

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

.PHONY: input clean install docs unittest

input: 	clean install documentation

install:
	@echo "*** Installing PyQSO"
	python setup.py install

docs:
	@echo "*** Building the documentation"
	cd docs; make html; cd ..

unittest:
	@echo "*** Running the unit tests"
	cd pyqso; for file in *.py; do (python $$file); done; cd ..

clean:
	@echo "*** Cleaning build directory"
	rm -rf build
	@echo "*** Cleaning pyqso directory"
	cd pyqso; rm -f *.pyc ADIF.test_read.adi ADIF.test_write*.adi; cd ..
	@echo "*** Cleaning doc directory"
	cd docs; make clean; cd ..
