# Change Log

## [0.3] - 2016-05-28
### Added
- Support for callsign lookups using the HamQTH.com database.
- Added a table of keyboard shortcuts to the documentation.
- More helpful messages regarding missing dependencies.
- Added the option of merging the COMMENT field with the NOTES field when importing records from an ADIF file.
- Bookmarking of Telnet-based DX cluster servers.

### Changed
- Ported the codebase over to Python 3 using 2to3 (thanks to Neil Johnson).
- The Summary page now also contains the total number of QSOs in the logbook.
- Improvements to docstrings.
- Various code cleanups (thanks to András Veres-Szentkirályi).
- Brought the list of valid modes up-to-date.
- Updated the list of bands and their frequency ranges.
- Configuration files are now written to ~/.config to keep the user's home directory uncluttered.
- The codebase is now compliant with the PEP 8 Python coding conventions (except for E501,F403,E226,E402,W503).
- Updated the documentation.

## [0.2] - 2015-03-07
### Added
- Travis CI configuration file for automated building and testing.
- Button to add the current date and time.
- Option to specify default values for the power and mode fields.
- Allow UTC time to be used when creating records.
- Allow prefixes/suffixes to be removed when looking up a callsign (e.g. "MYCALL" would be extracted from "EA3/MYCALL/M").

### Changed
- Migrated the documentation to a Sphinx-based setup.
- Separate the Create and Open functionality for logbooks.
- In the record dialog, the labels "TX RST" and "RX RST" have been changed to "RST Sent" and "RST Received". The underlying ADIF field names remain the same (RST_SENT and RST_RCVD).

### Fixed
- Logging debug messages to file.
- 'Z' characters in callsigns were being ignored when importing ADIF files. This has now been fixed.
- Specifed the Agg backend for matplotlib to workaround a bug in Ubuntu 14.10.
- Sorting the date and time fields in the correct chronological order.
- Removal of duplicate records.
- Error handling when looking up a callsign that does not have an entry on qrz.com.
- Handling of ConfigParser.NoOptionError exceptions when trying to load preferences.
- Handling of UnicodeDecodeError exceptions when parsing the output from DX cluster servers.

## [0.1] - 2014-03-22

### Changed
- The 'Notes' column is no longer automatically resized.
- The BEL character is now handled properly in the DX cluster tool.
- QSOs can now be sorted in the correct chronological order.

### Fixed
- Fixed the ADIF export functionality. Previously, only markers were being written and the actual record data was being skipped.

## [0.1b] - 2013-10-04

### Added
- Basic logging functionality.
- Import and export in ADIF format.
- Log printing.
- Basic support for Hamlib.
- Telnet-based DX cluster support.
- Progress tracker for the DXCC award.
- Greyline plotter.
- QSO filtering and sorting.
- Duplicate record removal.

[Unreleased]: https://github.com/ctjacobs/pyqso/compare/v0.2...master
[0.2]: https://github.com/ctjacobs/pyqso/compare/v0.1...v0.2
[0.1]: https://github.com/ctjacobs/pyqso/compare/v0.1b...v0.1
