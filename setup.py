#!/usr/bin/env python

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

