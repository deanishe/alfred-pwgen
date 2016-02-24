#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-07-27
#

"""
Generate password from (mostly) gibberish words.

http://stackoverflow.com/a/5502875/356942
"""

from __future__ import print_function, unicode_literals, absolute_import

import itertools
import string

from generators import WordGenBase


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


class PronounceableGenerator(WordGenBase):
    """Generate passwords based on (mostly) gibberish words.

    Better entropy (so stronger passwords for the same bits) than
    the dictionary-based generator (``WordlistGenerator``), but
    a bit harder to remember.

    The words in the passwords are joined with hyphens, but these are
    not included in the calculation of password strength.

    """

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
    def id(self):
        return 'pronounceable'

    @property
    def name(self):
        return 'Pronounceable Nonsense'

    @property
    def description(self):
        return 'Pronounceable, (mostly) nonsense words'


if __name__ == '__main__':
    gen = PronounceableGenerator()
    print(gen.password(length=30))
