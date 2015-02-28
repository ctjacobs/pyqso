# Change Log

## [0.2] - unreleased
### Added
- Travis CI configuration file for automated building and testing.
- Buttons to add the current date and time.
- Option to specify default values for the power and mode fields.
- Allow UTC time to be used when creating records.
- Allow prefixes/suffixes to be removed when looking up a callsign (e.g. "MYCALL" would be extracted from "EA3/MYCALL/M").

### Changed
- Migrated the documentation to a Sphinx-based setup.
- Separate the Create and Open functionality for logbooks.

### Fixed
- Logging debug messages to file.
- 'Z' characters in callsigns were being ignored when importing ADIF files. This has now been fixed.
- Specifed the Agg backend for matplotlib to workaround a bug in Ubuntu 14.10.
- Sorting the date and time fields in the correct chronological order.
- Removal of duplicate records.
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

[unreleased]: https://github.com/ctjacobs/pyqso/compare/v0.1...HEAD
[0.1]: https://github.com/ctjacobs/pyqso/compare/v0.1b...v0.1
