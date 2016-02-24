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
A password generator based on the contents of ``/usr/share/dict/words``
"""

from __future__ import print_function, unicode_literals, absolute_import


from generators import WordGenBase


class WordlistGenerator(WordGenBase):
    """Generate passwords based on the ``words`` file included with OS X.

    There's not a huge amount of entropy, so the passwords need to be
    rather long. But they are easier to remember than most of the others.

    The words in the passwords are joined with hyphens, but these are
    not included in the calculation of password strength.

    """

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
    def id(self):
        return 'dictionary'

    @property
    def name(self):
        return 'Dictionary'

    @property
    def description(self):
        return 'Dictionary words'
