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


def compare_date_and_time(model, row1, row2, user_data):
    """ Compare two rows (let's call them A and B) in a Gtk.ListStore, and sort by both date and time.

    :arg Gtk.TreeModel model: The model used to sort the log data.
    :arg Gtk.TreeIter row1: The pointer to row A.
    :arg Gtk.TreeIter row2: The pointer to row B.
    :arg user_data: The specific column from which to retrieve data for rows A and B.
    :returns: -1 if Row B's date/time is more recent than Row A's; 0 if both dates and times are the same; 1 if Row A's date/time is more recent than Row B's.
    :rtype: int
    """
    date1 = model.get_value(row1, user_data[0])
    date2 = model.get_value(row2, user_data[0])
    time1 = model.get_value(row1, user_data[1])
    time2 = model.get_value(row2, user_data[1])
    if date1 < date2:
        return -1
    elif date1 == date2:
        # If the dates are the same, then let's also sort by time.
        if time1 > time2:
            return 1
        elif time1 == time2:
            return 0
        else:
            return -1
    else:
        return 1


def compare_default(model, row1, row2, user_data):
    """ The default sorting function for all Gtk.ListStore objects.

    :arg Gtk.TreeModel model: The model used to sort the log data.
    :arg Gtk.TreeIter row1: The pointer to row A.
    :arg Gtk.TreeIter row2: The pointer to row B.
    :arg user_data: The specific column from which to retrieve data for rows A and B.
    :returns: -1 if the value of Row A's column value is less than Row B's column value; 0 if both values are the same; 1 if Row A's column value is greater than Row B's column value.
    :rtype: int
    """

    # Let's try to deal with numerical values, if possible.
    try:
        value1 = float(model.get_value(row1, user_data))
        value2 = float(model.get_value(row2, user_data))
    except ValueError:
        value1 = model.get_value(row1, user_data)
        value2 = model.get_value(row2, user_data)

    if value1 < value2:
        return -1
    elif value1 == value2:
        return 0
    else:
        return 1
