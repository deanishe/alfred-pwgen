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
Generate gibberish words.

http://stackoverflow.com/a/5502875/356942
"""

from __future__ import print_function, unicode_literals, absolute_import

import itertools
import math
import random
import string

from generators.base import PassGenBase


initial_consonants = (
    set(string.ascii_lowercase) - set('aeiou')
    # remove those easily confused with others
    - set('qxc')
    # add some crunchy clusters
    | set(['bl', 'br', 'cl', 'cr', 'dr', 'fl',
           'fr', 'gl', 'gr', 'pl', 'pr', 'sk',
           'sl', 'sm', 'sn', 'sp', 'st', 'str',
           'sw', 'tr'])
)

final_consonants = (
    set(string.ascii_lowercase) - set('aeiou')
    # confusable
    - set('qxcsj')
    # crunchy clusters
    | set(['ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt',
           'pt', 'sk', 'sp', 'ss', 'st'])
)

vowels = 'aeiou'


class PronounceableGenerator(PassGenBase):

    def __init__(self):
        self._syllables = None

    @property
    def data(self):
        if not self._syllables:
            # each syllable is consonant-vowel-consonant "pronounceable"
            self._syllables = map(''.join,
                                  itertools.product(initial_consonants,
                                                    vowels,
                                                    final_consonants))
        return self._syllables

    @property
    def id_(self):
        return 'pronounceable'

    @property
    def name(self):
        return 'Pronounceable Nonsense'

    @property
    def description(self):
        return 'Pronounceable, (mostly) nonsense words'

    def _password_by_iterations(self, iterations):
        """Return password using ``iterations`` iterations."""

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
        if len(pw) > length:
            pw = pw[:length]
            pw.rstrip('-')

        return pw, self.entropy * len(words)

    def password(self, strength=None, length=None):
        """Generate and return password."""

        if strength is not None:
            iterations = int(math.ceil(strength / self.entropy))
            return self._password_by_iterations(iterations)

        else:
            return self._password_by_length(length)


if __name__ == '__main__':
    gen = PronounceableAltGenerator()
    print(gen.password(length=30))
