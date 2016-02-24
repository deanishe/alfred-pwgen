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
Password genrators based on the German alphabet.

These are variations on the default generators using an alphabet
extended with German letters.

"""

from __future__ import print_function, unicode_literals, absolute_import

from .gen_basic import AsciiGenerator, AlphanumGenerator
from .gen_pronounceable_markov import PronounceableMarkovGenerator


# Umlauts, lovely umlauts
german_chars = 'ÄäÖöÜüß'


class GermanGenerator(AsciiGenerator):
    """ASCII + German characters."""

    @property
    def id(self):
        return 'german'

    @property
    def name(self):
        return 'German'

    @property
    def description(self):
        return 'German alphabet and digits with punctuation'

    @property
    def data(self):
        return super(GermanGenerator, self).data + german_chars


class GermanAlphanumericGenerator(AlphanumGenerator):
    """German alphabet and digits."""

    @property
    def id(self):
        return 'german-alphanumeric'

    @property
    def name(self):
        return 'German Alphanumeric'

    @property
    def description(self):
        return 'German alphabet and digits without punctuation'

    @property
    def data(self):
        return super(GermanAlphanumericGenerator, self).data + german_chars


class GermanPronounceableGenerator(PronounceableMarkovGenerator):
    """Pronounceable German passwords based on Markov chains."""

    _sample_file = 'german.txt'

    @property
    def id(self):
        return 'pronounceable-german'

    @property
    def name(self):
        return 'German Pronounceable Markov'

    @property
    def description(self):
        return 'Pronounceable passwords based on German'
