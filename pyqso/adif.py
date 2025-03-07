#!/usr/bin/env python3

#    Copyright (C) 2012-2017 Christian Thomas Jacobs.

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

import re
import logging
from datetime import datetime
import calendar
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from os.path import expanduser

# ADIF field names and their associated data types available in PyQSO.
AVAILABLE_FIELD_NAMES_TYPES = {"CALL": "S",
                               "QSO_DATE": "D",
                               "TIME_ON": "T",
                               "FREQ": "N",
                               "BAND": "E",
                               "MODE": "E",
                               "SUBMODE": "E",
                               "PROP_MODE": "E",
                               "TX_PWR": "N",
                               "RST_SENT": "S",
                               "RST_RCVD": "S",
                               "QSL_SENT": "S",
                               "QSL_RCVD": "S",
                               "NOTES": "M",
                               "NAME": "S",
                               "ADDRESS": "S",
                               "STATE": "S",
                               "COUNTRY": "S",
                               "DXCC": "N",
                               "CQZ": "N",
                               "ITUZ": "N",
                               "IOTA": "C",
                               "GRIDSQUARE": "S",
                               "SAT_NAME": "S",
                               "SAT_MODE": "S"}
# Note: The logbook uses the ADIF field names for the database column names.
# This list is used to display the columns in a logical order.
AVAILABLE_FIELD_NAMES_ORDERED = ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "SUBMODE", "PROP_MODE", "TX_PWR",
                                 "RST_SENT", "RST_RCVD", "QSL_SENT", "QSL_RCVD", "NOTES", "NAME",
                                 "ADDRESS", "STATE", "COUNTRY", "DXCC", "CQZ", "ITUZ", "IOTA", "GRIDSQUARE", "SAT_NAME", "SAT_MODE"]
# Define the more user-friendly versions of the field names.
AVAILABLE_FIELD_NAMES_FRIENDLY = {"CALL": "Callsign",
                                  "QSO_DATE": "Date",
                                  "TIME_ON": "Time",
                                  "FREQ": "Frequency (MHz)",
                                  "BAND": "Band",
                                  "MODE": "Mode",
                                  "SUBMODE": "Submode",
                                  "PROP_MODE": "Propagation Mode",
                                  "TX_PWR": "TX Power (W)",
                                  "RST_SENT": "RST Sent",
                                  "RST_RCVD": "RST Received",
                                  "QSL_SENT": "QSL Sent",
                                  "QSL_RCVD": "QSL Received",
                                  "NOTES": "Notes",
                                  "NAME": "Name",
                                  "ADDRESS": "Address",
                                  "STATE": "State",
                                  "COUNTRY": "Country",
                                  "DXCC": "DXCC",
                                  "CQZ": "CQ Zone",
                                  "ITUZ": "ITU Zone",
                                  "IOTA": "IOTA Designator",
                                  "GRIDSQUARE": "Grid Square",
                                  "SAT_NAME": "Satellite Name",
                                  "SAT_MODE": "Satellite Mode"}

# A: AwardList
# B: Boolean
# N: Number
# S: String
# I: International string
# D: Date
# T: Time
# M: Multi-line string
# G: Multi-line international string
# L: Location
# E: Enumerated
DATA_TYPES = ["A", "B", "N", "S", "I", "D", "T", "M", "G", "L", "E"]

# All the valid modes listed in the ADIF specification. This is a dictionary with the key-value pairs holding the MODE and SUBMODE(s) respectively.
MODES = {"": ("",),
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
MODES_DEPRECATED = {"AMTORFEC": ("",),
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
MODES.update(MODES_DEPRECATED)

# All the bands listed in the ADIF specification.
BANDS = ["", "2190m", "630m", "560m", "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "4m", "2m", "1.25m", "70cm", "33cm", "23cm", "13cm", "9cm", "6cm", "3cm", "1.25cm", "6mm", "4mm", "2.5mm", "2mm", "1mm"]
# The lower and upper frequency bounds (in MHz) for each band in BANDS.
BANDS_RANGES = [(None, None), (0.136, 0.137), (0.472, 0.479), (0.501, 0.504), (1.8, 2.0), (3.5, 4.0), (5.102, 5.4065), (7.0, 7.3), (10.0, 10.15), (14.0, 14.35), (18.068, 18.168), (21.0, 21.45), (24.890, 24.99), (28.0, 29.7), (50.0, 54.0), (70.0, 71.0), (144.0, 148.0), (222.0, 225.0), (420.0, 450.0), (902.0, 928.0), (1240.0, 1300.0), (2300.0, 2450.0), (3300.0, 3500.0), (5650.0, 5925.0), (10000.0, 10500.0), (24000.0, 24250.0), (47000.0, 47200.0), (75500.0, 81000.0), (119980.0, 120020.0), (142000.0, 149000.0), (241000.0, 250000.0)]

PROPAGATION_MODES = ["", "AS", "AUE", "AUR", "BS", "ECH", "EME", "ES", "F2", "FAI", "INTERNET", "ION", "IRL", "MS", "RPT", "RS", "SAT", "TEP", "TR"]

ADIF_VERSION = "3.0.4"


class ADIF:

    """ The ADIF class supplies methods for reading, parsing, and writing log files in the Amateur Data Interchange Format (ADIF).
    For more information, visit http://adif.org/ """

    def __init__(self):
        """ Initialise class for I/O of files using the Amateur Data Interchange Format (ADIF). """
        return

    def read(self, path):
        """ Read an ADIF file and parse it.

        :arg str path: The path to the ADIF file to read.
        :returns: A list of dictionaries (one dictionary per QSO), with each dictionary containing field-value pairs, e.g. {FREQ:145.500, BAND:2M, MODE:FM}. If the file cannot be read, the method returns None.
        :rtype: list
        :raises IOError: If the ADIF file does not exist or cannot be read (e.g. due to lack of read permissions).
        """
        logging.debug("Reading in ADIF file with path: %s..." % path)

        text = ""
        with open(path, mode="r", errors="replace") as f:
            text = f.read()

        records = self.parse_adi(text)

        if(records == []):
            logging.warning("No records found in the file. Empty file or wrong file type?")

        logging.info("Read %d QSOs from %s in ADIF format." % (len(records), path))
        return records

    def parse_adi(self, text):
        """ Parse some raw text (defined in the 'text' argument) for ADIF field data.

        :arg str text: The raw text from the ADIF file to parse.
        :returns: A list of dictionaries (one dictionary per QSO). Each dictionary contains the field-value pairs, e.g. {"FREQ": "145.500", "BAND": "2M", "MODE": "FM"}.
        :rtype: list
        """

        logging.debug("Parsing text from the ADIF file...")

        records = []

        # ADIF-related configuration options
        config = configparser.ConfigParser()
        have_config = (config.read(expanduser("~/.config/pyqso/preferences.ini")) != [])
        (section, option) = ("import_export", "merge_comment")
        if(have_config and config.has_option(section, option) and config.getboolean(section, option)):
            merge_comment = True
        else:
            merge_comment = False

        # Separate the text at the <eor> or <eoh> markers.
        tokens = re.split("(<eor>|<eoh>)", text, flags=re.IGNORECASE)
        tokens.pop()  # Anything after the final <eor> marker should be ignored.

        # The header might tell us the number of records, but let's not assume
        # this and simply ignore it instead (if it exists).
        if(re.search("<eoh>", text, flags=re.IGNORECASE) is not None):
            # There is a header present, so let's ignore everything
            # up to and including the <eoh> marker.
            while len(tokens) > 0:
                t = tokens.pop(0)
                if(re.match("<eoh>", t, flags=re.IGNORECASE) is not None):
                    break

        n_eor = 0
        n_record = 0
        records = []
        pattern = re.compile(r"<(.*?):(\d*).*?>([^<]+)")

        for t in tokens:
            if(re.match("<eor>", t, flags=re.IGNORECASE) is not None):
                n_eor += 1
                continue
            else:
                n_record += 1
                # Each record will have field names and corresponding
                # data entries. Store this in a dictionary.
                # Note: This is based on the code written by OK4BX.
                # (http://web.bxhome.org/blog/ok4bx/2012/05/adif-parser-python)
                fields_and_data_dictionary = {}
                fields_and_data = pattern.findall(t)
                comment = None
                for fd in fields_and_data:
                    # Let's force all field names to be in upper case.
                    # This will help us later when comparing the field names
                    # against the available field names in the ADIF specification.
                    field_name = fd[0].upper()
                    # Only read in the number of characters specified by the data length.
                    field_data = fd[2][:int(fd[1])]

                    # Combo boxes are used later on and these are case sensitive,
                    # so adjust the field data accordingly.
                    if(field_name == "BAND"):
                        field_data = field_data.lower()
                    elif(field_name == "CALL" or field_name == "MODE" or field_name == "SUBMODE"):
                        field_data = field_data.upper()
                    elif(field_name == "COMMENT"):
                        # Keep a copy of the COMMENT field data, in case we want to merge
                        # it with the NOTES field.
                        comment = field_data
                    if(field_name in AVAILABLE_FIELD_NAMES_ORDERED):
                        field_data_type = AVAILABLE_FIELD_NAMES_TYPES[field_name]
                        if(self.is_valid(field_name, field_data, field_data_type)):
                            # Only add the field if it is a standard ADIF field and it holds valid data.
                            fields_and_data_dictionary[field_name] = field_data

                # Merge the COMMENT field with the NOTES field, if desired and applicable.
                if(merge_comment):
                    if("NOTES" in list(fields_and_data_dictionary.keys()) and comment):
                        logging.debug("Merging COMMENT field with NOTES field...")
                        fields_and_data_dictionary["NOTES"] += "\n" + comment
                        logging.debug("Merged fields.")
                    elif(comment):
                        # Create the NOTES entry, but only store the contents of the COMMENT field.
                        logging.debug("The COMMENT field is present, but not the NOTES field. The NOTES field will be created and will only hold the COMMENT.")
                        fields_and_data_dictionary["NOTES"] = comment
                    else:
                        pass
                records.append(fields_and_data_dictionary)

        assert n_eor == n_record

        logging.debug("Finished parsing text.")

        return records

    def write(self, records, path):
        """ Write an ADIF file containing all the QSOs in the 'records' list.

        :arg list records: The list of QSO records to write.
        :arg str path: The desired path of the ADIF file to write to.
        :returns: None
        :raises IOError: If the ADIF file cannot be written (e.g. due to lack of write permissions).
        """

        logging.debug("Writing records to an ADIF file...")

        with open(path, mode="w", errors="replace") as f:  # Open file for writing

            # First write a header containing program version, number of records, etc.
            dt = datetime.now()

            f.write("""Amateur radio log file. Generated on %s. Contains %d record(s).

<adif_ver:%d>%s
<programid:5>PyQSO
<programversion:5>1.1.0
<eoh>\n""" % (dt, len(records), len(str(ADIF_VERSION)), ADIF_VERSION))

            # Then write each record to the file.
            for r in records:
                for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
                    if(not(field_name.lower() in list(r.keys()) or field_name.upper() in list(r.keys()))):
                        # If the field_name does not exist in the record, then skip past it.
                        # Only write out the fields that exist and that have some data in them.
                        continue
                    else:
                        if((r[field_name] != "NULL") and (r[field_name] != "")):
                            f.write("<%s:%d>%s\n" % (field_name.lower(), len(r[field_name]), r[field_name]))
                f.write("<eor>\n")

            logging.debug("Finished writing records to the ADIF file.")
            f.close()

            logging.info("Wrote %d QSOs to %s in ADIF format." % (len(records), path))

        return

    def is_valid(self, field_name, data, data_type):
        """ Validate the data in a field with respect to the ADIF specification.

        :arg str field_name: The name of the ADIF field.
        :arg str data: The data of the ADIF field to validate.
        :arg str data_type: The type of data to be validated. See http://www.adif.org/304/ADIF_304.htm#Data_Types for the full list with descriptions.
        :returns: True or False to indicate whether the data is valid or not.
        :rtype: bool
        """

        logging.debug("Validating the following data in field '%s': %s" % (field_name, data))

        # Allow an empty string or None, in case the user doesn't want
        # to fill in this field.
        if(not data):
            return True

        if(data_type == "N"):
            # Allow a decimal point before and/or after any numbers,
            # but don't allow a decimal point on its own.
            m = re.match(r"-?(([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+))", data)
            if(m is None):
                # Did not match anything.
                return False
            else:
                # Make sure we match the whole string,
                # otherwise there may be an invalid character after the match.
                return (m.group(0) == data)

        elif(data_type == "B"):
            # Boolean
            m = re.match(r"(Y|N)", data)
            if(m is None):
                return False
            else:
                return (m.group(0) == data)

        elif(data_type == "D"):
            # Date
            pattern = re.compile(r"([0-9]{4})")
            m_year = pattern.match(data, 0)
            if((m_year is None) or (int(m_year.group(0)) < 1930)):
                # Did not match anything.
                return False
            else:
                pattern = re.compile(r"([0-9]{2})")
                m_month = pattern.match(data, 4)
                if((m_month is None) or int(m_month.group(0)) > 12 or int(m_month.group(0)) < 1):
                    # Did not match anything.
                    return False
                else:
                    pattern = re.compile(r"([0-9]{2})")
                    m_day = pattern.match(data, 6)
                    days_in_month = calendar.monthrange(int(m_year.group(0)), int(m_month.group(0)))
                    if((m_day is None) or int(m_day.group(0)) > days_in_month[1] or int(m_day.group(0)) < 1):
                        # Did not match anything.
                        return False
                    else:
                        # Make sure we match the whole string,
                        # otherwise there may be an invalid character after the match.
                        return (len(data) == 8)

        elif(data_type == "T"):
            # Time
            pattern = re.compile(r"([0-9]{2})")
            m_hour = pattern.match(data, 0)
            if((m_hour is None) or (int(m_hour.group(0)) < 0) or (int(m_hour.group(0)) > 23)):
                # Did not match anything.
                return False
            else:
                pattern = re.compile(r"([0-9]{2})")
                m_minutes = pattern.match(data, 2)
                if((m_minutes is None) or int(m_minutes.group(0)) < 0 or int(m_minutes.group(0)) > 59):
                    # Did not match anything.
                    return False
                else:
                    if(len(data) == 4):
                        # HHMM format
                        return True
                    pattern = re.compile(r"([0-9]{2})")
                    m_seconds = pattern.match(data, 4)
                    if((m_seconds is None) or int(m_seconds.group(0)) < 0 or int(m_seconds.group(0)) > 59):
                        # Did not match anything.
                        return False
                    else:
                        # Make sure we match the whole string,
                        # otherwise there may be an invalid character after the match.
                        return (len(data) == 6)  # HHMMSS format

        # FIXME: Need to make sure that the "S" and "M" data types accept ASCII-only characters
        # in the range 32-126 inclusive.
        elif(data_type == "S"):
            # String
            m = re.match(r"(.+)", data)
            if(m is None):
                return False
            else:
                return (m.group(0) == data)

        elif(data_type == "I"):
            # IntlString
            m = re.match(r"(.+)", data, re.UNICODE)
            if(m is None):
                return False
            else:
                return (m.group(0) == data)

        elif(data_type == "G"):
            # IntlMultilineString
            m = re.match(r"(.+(\r\n)*.*)", data, re.UNICODE)
            if(m is None):
                return False
            else:
                return (m.group(0) == data)

        elif(data_type == "M"):
            # MultilineString
            # m = re.match(r"(.+(\r\n)*.*)", data)
            # if(m is None):
            #   return False
            # else:
            #   return (m.group(0) == data)
            return True

        elif(data_type == "L"):
            # Location
            pattern = re.compile(r"([EWNS]{1})", re.IGNORECASE)
            m_directional = pattern.match(data, 0)
            if(m_directional is None):
                # Did not match anything.
                return False
            else:
                pattern = re.compile(r"([0-9]{3})")
                m_degrees = pattern.match(data, 1)
                if((m_degrees is None) or int(m_degrees.group(0)) < 0 or int(m_degrees.group(0)) > 180):
                    # Did not match anything.
                    return False
                else:
                    pattern = re.compile(r"([0-9]{2}\.[0-9]{3})")
                    m_minutes = pattern.match(data, 4)
                    if((m_minutes is None) or float(m_minutes.group(0)) < 0 or float(m_minutes.group(0)) > 59.999):
                        # Did not match anything.
                        return False
                    else:
                        # Make sure we match the whole string,
                        # otherwise there may be an invalid character after the match.
                        return (len(data) == 10)

        elif(data_type == "E" or data_type == "A"):
            # Enumeration, AwardList.
            if(field_name == "MODE"):
                return (data in list(MODES.keys()))
            elif(field_name == "SUBMODE"):
                submodes = [submode for mode in list(MODES.keys()) for submode in MODES[mode]]
                return (data in submodes)
            elif(field_name == "BAND"):
                return (data in BANDS)
            else:
                return True

        else:
            return True
