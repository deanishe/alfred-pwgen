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
import random
import string

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

# each syllable is consonant-vowel-consonant "pronounceable"
syllables = map(''.join, itertools.product(initial_consonants,
                                           vowels,
                                           final_consonants))


def password(length, wordlist=syllables):
    words = []
    pw_length = 0
    rand = random.SystemRandom()
    while pw_length < length:
        word = rand.choice(wordlist)
        words.append(word)
        pw_length += len(word) + 1
    pw = '-'.join(words)
    if len(pw) > length:
        pw = pw[:length]
        pw.rstrip('-')

    return pw

if __name__ == '__main__':
    print('%d syllables' % len(syllables))
    print(password(30))
