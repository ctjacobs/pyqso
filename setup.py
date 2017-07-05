#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian Thomas Jacobs.

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

from setuptools import setup

setup(name="PyQSO",
      version="1.0.0",
      description="A contact logging tool for amateur radio operators.",
      author="Christian Thomas Jacobs",
      author_email="christian@christianjacobs.uk",
      url="https://github.com/ctjacobs/pyqso",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Natural Language :: English",
          "Programming Language :: Python :: 3",
          "Topic :: Communications :: Ham Radio",
      ]
      packages=["pyqso"],
      package_dir={"pyqso": "pyqso"},
      package_data={"pyqso": ["res/pyqso.glade", "res/log_64x64.png"]},
      scripts=["bin/pyqso"],
      zip_safe=False
      )
