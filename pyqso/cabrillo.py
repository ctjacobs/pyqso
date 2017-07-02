#!/usr/bin/env python3

#    Copyright (C) 2017 Christian Thomas Jacobs.

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

import logging

CABRILLO_VERSION = "3.0"

CONTESTS = ["", "AP-SPRINT", "ARRL-10", "ARRL-160", "ARRL-222", "ARRL-DX-CW", "ARRL-DX-SSB", "ARRL-RR-PH", "ARRL-RR-DIG", "ARRL-RR-CW", "ARRL-SCR", "ARRL-SS-CW", "ARRL-SS-SSB", "ARRL-UHF-AUG", "ARRL-VHF-JAN", "ARRL-VHF-JUN", "ARRL-VHF-SEP", "ARRL-RTTY", "BARTG-RTTY", "CQ-160-CW", "CQ-160-SSB", "CQ-WPX-CW", "CQ-WPX-RTTY", "CQ-WPX-SSB", "CQ-VHF", "CQ-WW-CW", "CQ-WW-RTTY", "CQ-WW-SSB", "DARC-WAEDC-CW", "DARC-WAEDC-RTTY", "DARC-WAEDC-SSB", "DL-DX-RTTY", "DRCG-WW-RTTY", "FCG-FQP", "IARU-HF", "JIDX-CW", "JIDX-SSB", "NAQP-CW", "NAQP-SSB", "NA-SPRINT-CW", "NA-SPRINT-SSB", "NCCC-CQP", "NEQP", "OCEANIA-DX-CW", "OCEANIA-DX-SSB", "RDXC", "RSGB-IOTA", "SAC-CW", "SAC-SSB", "STEW-PERRY", "TARA-RTTY"]


class Cabrillo:

    """ The Cabrillo class supplies methods for writing log files in the Cabrillo format (v3.0).
    For more information, visit http://wwrof.org/cabrillo/ """

    def __init__(self):
        """ Initialise class for I/O of files using the Cabrillo format. """
        return

    def write(self, records, path, contest="", mycall=""):
        """ Write a list of QSO records to a file in the Cabrillo format.

        :arg list records: The list of QSO records to write.
        :arg str path: The desired path of the Cabrillo file to write to.
        :arg str contest: The name of the contest.
        :arg str mycall: The callsign used during the contest.
        :returns: True if the write process was successful, otherwise False.
        :rtype: bool
        :raises IOError: if the Cabrillo file cannot be written (e.g. due to lack of write permissions)."""

        logging.debug("Writing records to a Cabrillo file...")

        success = False
        try:
            f = open(path, mode='w', errors="replace")  # Open file for writing

            # Header
            f.write("""START-OF-LOG: %s\n""" % (CABRILLO_VERSION))
            f.write("""CREATED-BY: PyQSO v1.0.0\n""")
            f.write("""CALLSIGN: %s\n""" % (mycall))
            f.write("""CONTEST: %s\n""" % (contest))

            # Write each record to the file.
            for r in records:

                # Frequency. Note that this must be in kHz. The frequency is stored in MHz in the database, so it's converted to kHz here.
                try:
                    freq = str(float(r["FREQ"])*1e3)
                except ValueError as e:
                    freq = ""

                # Mode
                if(r["MODE"] == "SSB"):
                    mo = "PH"
                elif(r["MODE"] == "CW"):
                    mo = "CW"
                elif(r["MODE"] == "FM"):
                    mo = "FM"
                else:
                    # FIXME: This assumes that the mode is any other non-CW digital mode, which isn't always going to be the case (e.g. for AM).
                    mo = "RY"

                # Date in yyyy-mm-dd format.
                date = r["QSO_DATE"][0:4] + "-" + r["QSO_DATE"][4:6] + "-" + r["QSO_DATE"][6:8]

                # Time
                time = r["TIME_ON"]

                # The callsign that was used when operating the contest station.
                call_sent = mycall

                # Exchange (the part sent to the distant station)
                exch_sent = r["RST_SENT"]

                # Callsign
                call_rcvd = r["CALL"]

                # Exchange (the part received from the distant station)
                exch_rcvd = r["RST_RCVD"]

                # Transmitter ID (must be 0 or 1, if applicable).
                # FIXME: For now this has been hard-coded to 0.
                t = "0"

                f.write("""QSO: %s %s %s %s %s %s %s %s %s\n""" % (freq, mo, date, time, call_sent, exch_sent, call_rcvd, exch_rcvd, t))

            # Footer
            f.write("END-OF-LOG:")

            f.close()

            logging.info("Wrote %d QSOs to %s in Cabrillo format." % (len(records), path))
            success = True

        except IOError as e:
            logging.error("I/O error %d: %s" % (e.errno, e.strerror))
        except Exception as e:  # All other exceptions.
            logging.error("An error occurred when writing the Cabrillo file.")
            logging.exception(e)

        return success
