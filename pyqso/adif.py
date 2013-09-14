#!/usr/bin/env python 
# File: adif.py

#    Copyright (C) 2012 Christian Jacobs.

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
import unittest
from datetime import datetime
import calendar

# ADIF field names and their associated data types available in PyQSO.
AVAILABLE_FIELD_NAMES_TYPES = {"CALL": "S", 
                              "QSO_DATE": "D",
                              "TIME_ON": "T",
                              "FREQ": "N",
                              "BAND": "E",
                              "MODE": "E",
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
                              "IOTA": "C"}
# Note: The logbook uses the ADIF field names for the database column names.
# This list is used to display the columns in a logical order.
AVAILABLE_FIELD_NAMES_ORDERED = ["CALL", "QSO_DATE", "TIME_ON", "FREQ", "BAND", "MODE", "TX_PWR", 
                                 "RST_SENT", "RST_RCVD", "QSL_SENT", "QSL_RCVD", "NOTES", "NAME",
                                 "ADDRESS", "STATE", "COUNTRY", "DXCC", "CQZ", "ITUZ", "IOTA"]
# Define the more user-friendly versions of the field names.
AVAILABLE_FIELD_NAMES_FRIENDLY = {"CALL":"Callsign",
                                  "QSO_DATE":"Date",
                                  "TIME_ON":"Time",
                                  "FREQ":"Frequency (MHz)",
                                  "BAND":"Band",
                                  "MODE":"Mode",
                                  "TX_PWR":"TX Power (W)",
                                  "RST_SENT":"TX RST",
                                  "RST_RCVD":"RX RST",
                                  "QSL_SENT":"QSL Sent",
                                  "QSL_RCVD":"QSL Received",
                                  "NOTES":"Notes",
                                  "NAME":"Name",
                                  "ADDRESS":"Address",
                                  "STATE":"State",
                                  "COUNTRY":"Country",
                                  "DXCC":"DXCC",
                                  "CQZ":"CQ Zone",
                                  "ITUZ":"ITU Zone",
                                  "IOTA":"IOTA Designator"}

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
DATA_TYPES = ["A", "B", "N", "S", "I", "D", "T", "M", "G", "L", "E"]

ADIF_VERSION = "1.0"

class ADIF:
   """ The ADIF class supplies methods for reading, parsing, and writing log files in the Amateur Data Interchange Format (ADIF). """
   
   def __init__(self):
      # Class for I/O of files using the Amateur Data Interchange Format (ADIF).
      logging.debug("New ADIF instance created!")
      
   def read(self, path):
      """ Read an ADIF file with a specified path (given in the 'path' argument), and then parse it.
      The output is a list of dictionaries (one dictionary per QSO), with each dictionary containing field-value pairs,
      e.g. {FREQ:145.500, BAND:2M, MODE:FM}. """
      logging.debug("Reading in ADIF file with path: %s..." % path)

      text = ""      
      try:
         f = open(path, 'r')
         text = f.read()
         f.close() # Close the file, otherwise "bad things" might happen!
      except IOError as e:
         logging.error("I/O error %d: %s" % (e.errno, e.strerror))
         raise
      except:
         logging.error("Unknown error occurred when reading the ADIF file.")
         raise

      records = self._parse_adi(text)
         
      if(records == []):
         logging.warning("No records found in the file. Empty file or wrong file type?")
         
      return records
      
   def _parse_adi(self, text):
      """ Parse some raw text (defined in the 'text' argument) for ADIF field data.
      Outputs a list of dictionaries (one dictionary per QSO). Each dictionary contains the field-value pairs,
      e.g. {FREQ:145.500, BAND:2M, MODE:FM}. """
      records = []

      # Separate the text at the <eor> or <eoh> markers.
      tokens = re.split('(<eor>|<eoh>)', text, flags=re.IGNORECASE)
      tokens.pop() # Anything after the final <eor> marker should be ignored.
      
      # The header might tell us the number of records, but let's not assume
      # this and simply ignore it instead (if it exists).
      if(re.search('<eoh>', text, flags=re.IGNORECASE) is not None):
         # There is a header present, so let's ignore everything
         # up to and including the <eoh> marker. Note that
         # re.search has been used here to handle any case sensitivity.
         # Previously we were checking for <eoh>. <EOH> is also valid
         # but wasn't been detected before.
         while len(tokens) > 0:
            t = tokens.pop(0)
            if(re.match('<eoh>', t, flags=re.IGNORECASE) is not None):
               break
            
      n_eor = 0 
      n_record = 0
      records = []
      for t in tokens:
         if(re.match('<eor>', t, flags=re.IGNORECASE) is not None):
            n_eor = n_eor + 1
            continue
         else:
            n_record = n_record + 1
            # Each record will have field names and corresponding
            # data entries. Store this in a dictionary.
            # Note: This is based on the code written by OK4BX.
            # (http://web.bxhome.org/blog/ok4bx/2012/05/adif-parser-python)
            fields_and_data_dictionary = {}
            fields_and_data = re.findall('<(.*?):(\d*).*?>([^<\t\n\r\f\v\Z]+)', t)  
            for fd in fields_and_data:
               # Let's force all field names to be in upper case.
               # This will help us later when comparing the field names
               # against the available field names in the ADIF specification.
               field_name = fd[0].upper()
               field_data = fd[2][:int(fd[1])]

               # Combo boxes are used later on and these are case sensitive,
               # so adjust the field data accordingly.
               if(field_name == "BAND"):
                  field_data = field_data.lower()
               elif(field_name == "MODE"):
                  field_data = field_data.upper()

               if(field_name in AVAILABLE_FIELD_NAMES_ORDERED):
                  field_data_type = AVAILABLE_FIELD_NAMES_TYPES[field_name]
                  if(self.is_valid(field_name, field_data, field_data_type)):
                     # Only add the field if it is a standard ADIF field and it holds valid data.
                     fields_and_data_dictionary[field_name] = field_data

            records.append(fields_and_data_dictionary)
      
      assert n_eor == n_record
      
      return records

      
   def write(self, records, path):
      """ Write an ADIF file containing all the QSOs in the 'records' list. The desired path is specified in the 'path' argument. 
      This method returns None. """
      try:
         f = open(path, 'w') # Open file for writing
         
         # First write a header containing program version, number of records, etc.
         dt = datetime.now()
         
         f.write("""Amateur radio log file. Generated on %s. Contains %d record(s). 
         
<adif_ver:5>%s
<programid:5>PyQSO
<programversion:8>0.1a.dev
<eoh>\n""" % (dt, len(records), ADIF_VERSION))
         
         # Then write each log to the file.
         for r in records:
            for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
               if( (r[field_name] != "NULL") and (r[field_name] != "") ):
                  f.write("<%s:%d>%s\n" % (field_name.lower(), len(r[field_name]), r[field_name]))
            f.write("<eor>\n")

         f.close()

      except IOError as e:
         logging.error("I/O error %d: %s" % (e.errno, e.strerror))
         raise
      except:
         logging.error("Unknown error occurred when writing the ADIF file.")
         raise
         
      return


   def is_valid(self, field_name, data, data_type):
      """ Validate the data in a field (with name 'field_name') with respect to the ADIF specification. 
      This method returns either True or False to indicate whether the data is valid or not. """
      
      # Allow an empty string, in case the user doesn't want
      # to fill in this field.
      if(data == ""):
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
                  return (len(data) == 6) # HHMMSS format

      #FIXME: Need to make sure that the "S" and "M" data types accept ASCII-only characters
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
         m = re.match(ur"(.+)", data, re.UNICODE)
         if(m is None):
            return False
         else:
            return (m.group(0) == data)

      elif(data_type == "G"):
         # IntlMultilineString
         m = re.match(ur"(.+(\r\n)*.*)", data, re.UNICODE)
         if(m is None):
            return False
         else:
            return (m.group(0) == data)

      elif(data_type == "M"):
         # MultilineString
         #m = re.match(r"(.+(\r\n)*.*)", data)
         #if(m is None):
         #   return False
         #else:
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
            modes = ["", "AM", "AMTORFEC", "ASCI", "ATV", "CHIP64", "CHIP128", "CLO", "CONTESTI", "CW", "DSTAR", "DOMINO", "DOMINOF", "FAX", "FM", "FMHELL", "FSK31", "FSK441", "GTOR", "HELL", "HELL80", "HFSK", "ISCAT", "JT44", "JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G", "JT65", "JT65A", "JT65B", "JT65C", "JT6M", "MFSK8", "MFSK16", "MT63", "OLIVIA", "PAC", "PAC2", "PAC3", "PAX", "PAX2", "PCW", "PKT", "PSK10", "PSK31", "PSK63", "PSK63F", "PSK125", "PSKAM10", "PSKAM31", "PSKAM50", "PSKFEC31", "PSKHELL", "Q15", "QPSK31", "QPSK63", "QPSK125", "ROS", "RTTY", "RTTYM", "SSB", "SSTV", "THRB", "THOR", "THRBX", "TOR", "V4", "VOI", "WINMOR", "WSPR"]
            return (data in modes)
         elif(field_name == "BAND"):
            bands = ["", "2190m", "560m", "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "4m", "2m", "1.25m", "70cm", "33cm", "23cm", "13cm", "9cm", "6cm", "3cm", "1.25cm", "6mm", "4mm", "2.5mm", "2mm", "1mm"]
            return (data in bands)
         else:
            return True

      else:
         return True
      
   
class TestADIF(unittest.TestCase):
   def test_adif_read(self):
      adif = ADIF()
      f = open("ADIF.test_read.adi", 'w')
      f.write("""Some test ADI data.<eoh>

<call:4>TEST<band:3>40M<mode:2>CW
<qso_date:8:d>20130322<time_on:4>1955<eor>""")
      f.close()
    
      records = adif.read("ADIF.test_read.adi")
      
      assert records == [{'BAND': '40M', 'TIME_ON': '1955', 'CALL': 'TEST', 'MODE': 'CW', 'QSO_DATE': '20130322'}]
              
if(__name__ == '__main__'):
   unittest.main()

