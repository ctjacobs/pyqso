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

import sqlite3
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import logging

MODES_FILE = os.path.expanduser("~/.config/pyqso/modes.db")


class Modes:

    def __init__(self):

        try:
            connection = sqlite3.connect(MODES_FILE)
            c = connection.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS modes (
                            mode TEXT NOT NULL,
                            submode TEXT NOT NULL,
                            UNIQUE(mode, submode)
                            ); """)

            # Fill the new table with the basic list of modes and submodes.
            for mode in self.basic:
                for submode in self.basic[mode]:
                    c.execute("""REPLACE INTO modes(mode, submode) VALUES(?, ?)""", (mode, submode))
            connection.commit()
            connection.close()
        except sqlite3.Error as e:
            logging.exception(e)

        #self.update("http://www.adif.org/309/ADIF_309.htm")
        return

    @property
    def basic(self):
        """ A basic list of valid modes listed in the ADIF specification.
        This is a dictionary with the key-value pairs holding the MODE and SUBMODE(s) respectively. """

        modes = {"": ("",),
                 "AM": ("",),
                 "ATV": ("",),
                 "CHIP": ("", "CHIP64", "CHIP128"),
                 "CLO": ("",),
                 "CONTESTI": ("",),
                 "CW": ("", "PCW"),
                 "DIGITALVOICE": ("",),
                 "DOMINO": ("", "DOMINOEX", "DOMINOF"),
                 "DSTAR": ("",),
                 "FAX": ("",),
                 "FM": ("",),
                 "FSK441": ("",),
                 "FT8": ("",),
                 "HELL": ("", "FMHELL", "FSKHELL", "HELL80", "HFSK", "PSKHELL"),
                 "ISCAT": ("", "ISCAT-A", "ISCAT-B"),
                 "JT4": ("", "JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G"),
                 "JT6M": ("",),
                 "JT9": ("",),
                 "JT44": ("",),
                 "JT65": ("", "JT65A", "JT65B", "JT65B2", "JT65C", "JT65C2"),
                 "MFSK": ("", "MFSK4", "MFSK8", "MFSK11", "MFSK16", "MFSK22", "MFSK31", "MFSK32", "MFSK64", "MFSK128"),
                 "MT63": ("",),
                 "OLIVIA": ("", "OLIVIA 4/125", "OLIVIA 4/250", "OLIVIA 8/250", "OLIVIA 8/500", "OLIVIA 16/500", "OLIVIA 16/1000", "OLIVIA 32/1000"),
                 "OPERA": ("", "OPERA-BEACON", "OPERA-QSO"),
                 "PAC": ("", "PAC2", "PAC3", "PAC4"),
                 "PAX": ("", "PAX2"),
                 "PKT": ("",),
                 "PSK": ("", "FSK31", "PSK10", "PSK31", "PSK63", "PSK63F", "PSK125", "PSK250", "PSK500", "PSK1000", "PSKAM10", "PSKAM31", "PSKAM50", "PSKFEC31", "QPSK31", "QPSK63", "QPSK125", "QPSK250", "QPSK500"),
                 "PSK2K": ("",),
                 "Q15": ("",),
                 "ROS": ("", "ROS-EME", "ROS-HF", "ROS-MF"),
                 "RTTY": ("", "ASCI"),
                 "RTTYM": ("",),
                 "SSB": ("", "LSB", "USB"),
                 "SSTV": ("",),
                 "THOR": ("",),
                 "THRB": ("", "THRBX"),
                 "TOR": ("", "AMTORFEC", "GTOR"),
                 "V4": ("",),
                 "VOI": ("",),
                 "WINMOR": ("",),
                 "WSPR": ("",)
                 }

        # A dictionary of all the deprecated MODE values.
        deprecated = {"AMTORFEC": ("",),
                            "ASCI": ("",),
                            "CHIP64": ("",),
                            "CHIP128": ("",),
                            "DOMINOF": ("",),
                            "FMHELL": ("",),
                            "FSK31": ("",),
                            "GTOR": ("",),
                            "HELL80": ("",),
                            "HFSK": ("",),
                            "JT4A": ("",),
                            "JT4B": ("",),
                            "JT4C": ("",),
                            "JT4D": ("",),
                            "JT4E": ("",),
                            "JT4F": ("",),
                            "JT4G": ("",),
                            "JT65A": ("",),
                            "JT65B": ("",),
                            "JT65C": ("",),
                            "MFSK8": ("",),
                            "MFSK16": ("",),
                            "PAC2": ("",),
                            "PAC3": ("",),
                            "PAX2": ("",),
                            "PCW": ("",),
                            "PSK10": ("",),
                            "PSK31": ("",),
                            "PSK63": ("",),
                            "PSK63F": ("",),
                            "PSK125": ("",),
                            "PSKAM10": ("",),
                            "PSKAM31": ("",),
                            "PSKAM50": ("",),
                            "PSKFEC31": ("",),
                            "PSKHELL": ("",),
                            "QPSK31": ("",),
                            "QPSK63": ("",),
                            "QPSK125": ("",),
                            "THRBX": ("",)
                            }

        # Include all deprecated modes.
        modes.update(deprecated)
        return modes

    @property
    def all(self):
        try:
            connection = sqlite3.connect(MODES_FILE)
            c = connection.cursor()
            result = c.execute("""SELECT * FROM modes""")
            rows = result.fetchall()

            modes = {}
            for row in rows:
                mode = row[0]
                submode = row[1]
                if(mode in modes.keys()):
                    modes[mode].append(submode)
                else:
                    modes[mode] = [submode]
            connection.close()
        except sqlite3.Error as e:
            logging.exception(e)
        return modes

    def update(self, url):
        modes = self.parse(url)
        try:
            connection = sqlite3.connect(MODES_FILE)
            c = connection.cursor()
            for mode in modes:
                for submode in modes[mode]:
                    c.execute("REPLACE INTO modes(mode, submode) VALUES(?,?)", (mode, submode))
            connection.commit()
            connection.close()
        except sqlite3.Error as e:
            logging.exception(e)
        
        return

    def parse(self, url):
        page = urlopen(url).read()
        soup = BeautifulSoup(page, "html.parser")

        # Remove the <span> tags but keep the tags' contents.
        for match in soup.findAll("span"):
            match.unwrap()

        # Find the MODES table.
        rows = soup.find(id="Enumeration_Mode").find_all("tr")

        # Extract modes and submodes.
        modes = {}
        for row in rows[1:]:  # Ignores the header row.
            mode, submode = row.find_all("td")[0:2]
            mode = mode.text.split(" (import-only)")[0].strip()
            submode = tuple(submode.text.strip().split(", "))
            if(mode not in modes):
                modes[mode] = submode

        return modes

