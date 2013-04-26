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
from datetime import datetime

# All the possible field names and their associated data types 
# from the ADIF specification (version 3.0.2)
AVAILABLE_FIELD_NAMES_TYPES = {"CALL": "S", 
                              "DATE": "D",
                              "TIME": "T",
                              "FREQ": "N",
                              "BAND": "E",
                              "MODE": "E",
                              "RST_SENT": "S",
                              "RST_RCVD": "S"}

AVAILABLE_FIELD_NAMES_ORDERED = ["CALL", "DATE", "TIME", "FREQ", "BAND", "MODE", "RST_SENT", "RST_RCVD"]

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

ADIF_VERSION = "3.0.2"

class ADIF:
   
   def __init__(self):
      # Class for I/O of files using the Amateur Data Interchange Format (ADIF).
      logging.debug("New ADIF instance created!")
      
   def read(self, path):
      
      logging.debug("Reading in ADIF file with path: %s." % path)
      
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
      
      records = self.parse_adi(text)
         
      if(records == []):
         logging.warning("No records found in the file. Empty file or wrong file type?")
         
      return records
      
   def parse_adi(self, text):
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
               fields_and_data_dictionary[fd[0].upper()] = fd[2][:int(fd[1])]
            records.append(fields_and_data_dictionary)
      
      assert n_eor == n_record
      
      return records

      
   def write(self, records, path):
      f = open(path, 'w') # Open file for writing
      
      # First write a header containing program version, number of records, etc.
      dt = datetime.now()
      
      f.write('''Amateur radio log file. Generated on %s. Contains %d record(s). 
      
<adif_ver:5>%s
<programid:5>PyQSO
<programversion:8>0.1a.dev

<eoh>\n''' % (dt, len(records), ADIF_VERSION))
      
      # Then write each log to the file.
      for r in records:
         for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
            if( (r[field_name] != "NULL") and (r[field_name] != "") ):
               f.write("<%s:%d>%s\n" % (field_name.lower(), len(r[field_name]), r[field_name]))
         f.write("<eor>\n")

      f.close()
      
   
   def test_read(self):
      f = open("../ADIF.test_read.adi.test", 'w')
      f.write('''Some test ADI data.<eoh>

<call:4>TEST<band:3>40M<mode:2>CW
<qso_date:8:d>20130322<time_on:4>1955<eor>''')
      f.close()
    
      records = self.read("../ADIF.test_read.adi.test")
      
      assert records == [{'band': '40M', 'time_on': '1955', 'call': 'TEST', 'mode': 'CW', 'qso_date': '20130322'}]
              
if(__name__ == '__main__'):
   a = ADIF() 
   a.test_read()

