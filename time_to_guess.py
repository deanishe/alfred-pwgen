#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-07-28
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import sys

# Guesses/second
gps = 45000000000

bits = 32


def human_time(seconds):
    if seconds < 60:
        return '%0.3f seconds' % seconds
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    years, weeks = divmod(weeks, 52)
    centuries, years = divmod(years, 100)
    millenia, centuries = divmod(centuries, 10)
    universe_ages, millenia = divmod(millenia, 14000000)
    if universe_ages:
        return '%d ages of the universe' % universe_ages
    if millenia:
        return '%d millenia, %d centuries' % (millenia, centuries)
    if centuries:
        return '%d centuries, %d years' % (centuries, years)
    if years:
        return '%d years, %d weeks' % (years, weeks)
    elif weeks:
        return '%d weeks, %d days' % (weeks, days)

while bits <= 256:
    # guesses = int('0b' + '1' * (bits - 1), 2)
    guesses = 2 ** (bits - 1)
    time = float(guesses) / gps
    print('%3d bits : %s' % (bits, human_time(time)))
    bits += 32
