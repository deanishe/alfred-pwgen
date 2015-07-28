#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-07-27
#

"""
Basic generators.
"""

from __future__ import print_function, unicode_literals, absolute_import

import string

from .base import PassGenBase, punctuation


class AsciiGenerator(PassGenBase):
    """Simple ASCII password generator."""

    @property
    def id_(self):
        return 'ascii'

    @property
    def name(self):
        return 'ASCII'

    @property
    def description(self):
        return 'ASCII characters with punctuation'

    @property
    def data(self):
        return string.ascii_letters + string.digits + punctuation


class AlphanumGenerator(PassGenBase):
    """Simple alphanumeric password generator."""

    @property
    def id_(self):
        return 'alphanumeric'

    @property
    def name(self):
        return 'Alphanumeric'

    @property
    def description(self):
        return 'ASCII characters without punctuation'

    @property
    def data(self):
        return string.ascii_letters + string.digits


class AlphanumClearGenerator(PassGenBase):
    """Simple alphanumeric password generator w/out confusable characters."""

    @property
    def id_(self):
        return 'alphanumeric-clear'

    @property
    def name(self):
        return 'Clear Alphanumeric'

    @property
    def description(self):
        return 'ASCII characters without confusing characters or punctuation'

    @property
    def data(self):
        data = (set(string.ascii_letters) | set(string.digits))
        data = data - set('l10O')
        return ''.join(data)


class NumericGenerator(PassGenBase):
    """Simple numeric password generator."""

    @property
    def id_(self):
        return 'numeric'

    @property
    def name(self):
        return 'Numeric'

    @property
    def description(self):
        return 'Digits only'

    @property
    def data(self):
        return string.digits
