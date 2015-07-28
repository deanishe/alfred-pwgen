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
"""

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division
)

import abc
import math
import os

ENTROPY_PER_LEVEL = 32

# string.punctuation contains a few characters we don't want
# like backslash and tilde
punctuation = """!"#$%&'()*+,-./:;<=>?@[]^_{|}"""


class PassGenBase(object):
    """Base class for generators"""
    __metaclass__ = abc.ABCMeta

    def password(self, strength=None, length=None):
        """Method to generate and return password.

        Either ``strength`` or ``length`` must be specified.

        Returns tuple: (password, entropy)

        """

        if strength is not None:
            length = int(math.ceil(strength / self.entropy))

        chars = self.data
        pw = [chars[ord(c) % len(chars)] for c in os.urandom(length)]
        return ''.join(pw), self.entropy * length

    @property
    def entropy(self):
        return math.log(len(self.data), 2)

    @abc.abstractproperty
    def id_(self):
        """Short name of the generator.

        Used in settings to identify the generator.

        """

        return

    @abc.abstractproperty
    def name(self):
        """Human-readable name of the generator."""
        return

    @abc.abstractproperty
    def description(self):
        """Longer description of the generator."""
        return

    @abc.abstractproperty
    def data(self):
        """List of data to choose from."""
        return
