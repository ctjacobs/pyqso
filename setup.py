#!/usr/bin/env python
# File: setup.py

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

from distutils.core import setup

setup(name='PyQSO',
      version='0.1a.dev',
      description='A Python-based QSO logging tool',
      author='Christian Jacobs',
      url='https://launchpad.net/pyqso',
      packages=['pyqso'],
      package_dir = {'pyqso': 'pyqso'},
      scripts=["bin/pyqso"]
     )

