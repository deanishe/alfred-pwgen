#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-07-28
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import math
import random

from generators.base import PassGenBase


class WordlistGenerator(PassGenBase):

    _filepath = '/usr/share/dict/words'
    _maxlen = 6  # Ignore words longer than this

    def __init__(self):
        self._words = None

    @property
    def data(self):
        if not self._words:
            words = set()
            with open(self._filepath, 'rb') as fp:
                for line in fp:
                    line = line.strip()
                    if not line or len(line) > self._maxlen:
                        continue
                    words.add(line.lower())
            self._words = sorted(words)

        return self._words

    @property
    def id_(self):
        return 'dictionary'

    @property
    def name(self):
        return 'Dictionary'

    @property
    def description(self):
        return 'Dictionary words'

    def _password_by_iterations(self, iterations):
        """Return password using ``iterations`` iterations."""
        words = []
        rand = random.SystemRandom()
        words = [rand.choice(self.data) for i in range(iterations)]
        return '-'.join(words), self.entropy * iterations

    def _password_by_length(self, length):
        """Return password of length ``length``."""
        words = []
        pw_length = 0
        rand = random.SystemRandom()
        while pw_length < length:
            word = rand.choice(self.data)
            words.append(word)
            pw_length += len(word) + 1

        pw = '-'.join(words)

        return pw, self.entropy * len(words)

    def password(self, strength=None, length=None):
        """Method to generate and return password.

        Either ``strength`` or ``length`` must be specified.

        Returns tuple: (password, entropy)

        """

        if strength is not None:
            iterations = int(math.ceil(strength / self.entropy))
            return self._password_by_iterations(iterations)

        else:
            return self._password_by_length(length)
