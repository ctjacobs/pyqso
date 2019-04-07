#!/usr/bin/env python3

#    Copyright (C) 2019 Christian Thomas Jacobs.

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

from urllib.request import urlopen
from bs4 import BeautifulSoup

page = urlopen('http://www.adif.org/307/ADIF_307.htm').read()
soup = BeautifulSoup(page, "html.parser")

# Remove the <span> tags but keep the tags' contents.
for match in soup.findAll('span'):
    match.unwrap()

# Find the MODES table.
rows = soup.find(id="Enumeration_Mode").find_all('tr')

# Extract modes and submodes.
modes = {}
for row in rows[1:]:
    mode, submode, description = row.find_all('td')
    mode = mode.text.split(" (import-only)")[0].strip()
    submode = tuple(submode.text.strip().split(", "))
    modes[mode] = submode
print(modes)
