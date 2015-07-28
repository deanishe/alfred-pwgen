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

import random

from .base import PassGenBase


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

    def password(self, length=30):
        words = []
        pw_length = 0
        rand = random.SystemRandom()
        while pw_length < length:
            word = rand.choice(self.data)
            words.append(word)
            pw_length += len(word) + 1

        pw = '-'.join(words)

        return pw, self.entropy * len(words)
