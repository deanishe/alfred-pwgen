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

from collections import defaultdict
import itertools
import math
import os
import string
import random

from generators.base import PassGenBase, ENTROPY_PER_LEVEL


# Markov chain code from
# https://github.com/SimonSapin/snippets/blob/master/markov_passwords.py


def pairwise(iterable):
    """
    Yield pairs of consecutive elements in iterable.

    >>> list(pairwise('abcd'))
    [('a', 'b'), ('b', 'c'), ('c', 'd')]
    """
    iterator = iter(iterable)
    try:
        a = iterator.next()
    except StopIteration:
        return
    for b in iterator:
        yield a, b
        a = b


class MarkovChain(object):
    """Markov chain implementation. Initialise with text ``sample``.

    If a system transits from a state to another and the next state depends
    only on the current state and not the past, it is said to be a
    Markov chain.

    It is determined by the probability of each next state from any current
    state.

    See http://en.wikipedia.org/wiki/Markov_chain

    The probabilities are built from the frequencies in the `sample` chain.
    Elements of the sample that are not a valid state are ignored.

    """

    def __init__(self, sample):
        self._rand = random.SystemRandom()
        self.counts = counts = defaultdict(lambda: defaultdict(int))

        for word in sample.split(' '):
            for current, nxt in pairwise(word):
                counts[current][nxt] += 1

        self.totals = dict(
            (current, sum(next_counts.itervalues()))
            for current, next_counts in counts.iteritems()
        )

    def next(self, state):
        """Return random next state.

        Choose at random and return a next state from a current state,
        according to the probabilities for this chain

        """

        nexts = self.counts[state].iteritems()
        # Like random.choice() but with a different weight for each element
        rand = self._rand.randrange(0, self.totals[state])
        # Using bisection here could be faster, but simplicity prevailed.
        # (Also it’s not that slow with 26 states or so.)
        for next_state, weight in nexts:
            if rand < weight:
                return next_state
            rand -= weight

    def __iter__(self):
        """Return an infinite iterator of states."""

        state = self._rand.choice(self.counts.keys())
        while True:
            state = self.next(state)
            yield state


class WordGenerator(object):
    """Yield pronounceable words"""

    def __init__(self, sample, min_length=3, max_length=6):
        self.min_length = min_length
        self.max_length = max_length

        # Remove punctuation, numbers and some whitespace from sample
        bad_chars = string.punctuation + string.digits + '\n\t'
        self.sample = ''.join([c for c in sample.lower()
                               if c not in bad_chars])

        # import math
        # chain = MarkovChain(self.sample)
        # self.entropy = math.log(sum(chain.totals.values()), 2)

    def __iter__(self):
        rand = random.SystemRandom()
        while True:
            chain = MarkovChain(self.sample)
            length = rand.randrange(self.min_length, self.max_length)
            yield ''.join(itertools.islice(chain, length))


class PronounceableGenerator(PassGenBase):
    """Pronounceable passwords based on Markov chains."""

    _sample_file = 'english.txt'

    def __init__(self):
        self._sample = None
        self._generator = None

    @property
    def id_(self):
        return 'pronounceable'

    @property
    def name(self):
        return 'Pronounceable'

    @property
    def description(self):
        return 'Pronounceable, based on English'

    @property
    def data(self):
        return None

    @property
    def entropy(self):
        # Conservative estimate based on the number
        # of elements in a chain based on `english.txt`
        return 13.43
        # return self.generator.entropy

    @property
    def sample(self):
        if not self._sample:
            path = os.path.join(os.path.dirname(__file__),
                                self._sample_file)
            with open(path, 'rb') as fp:
                self._sample = fp.read().decode('utf-8')

        return self._sample

    @property
    def generator(self):
        if not self._generator:
            self._generator = WordGenerator(self.sample)

        return self._generator

    def _password_by_iterations(self, iterations):
        """Return password using ``iterations`` iterations."""
        words = []
        gen = WordGenerator(self.sample)
        words = itertools.islice(gen, iterations)
        return '-'.join(words), self.entropy * iterations

    def _password_by_length(self, length):
        """Return password of length ``length``."""

        words = []
        pw_length = 0
        for word in self.generator:
            words.append(word)
            pw_length += len(word) + 1
            if pw_length >= length:
                break

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


if __name__ == '__main__':
    # gen = PronounceableGenerator()
    # print(gen.password(30))
    words = set()
    words_in_words = 0
    i = 1
    path = os.path.join(os.path.dirname(__file__), 'english.txt')
    with open(path, 'rb') as fp:
        sample = fp.read().decode('utf-8')
    gen = WordGenerator(sample)
    for word in gen:
        if word in words:
            words_in_words += 1
        else:
            words.add(word)
            words_in_words = 0
        if words_in_words == 10:
            break
        if i % 1000 == 0:
            print('%d/%d unique words' % (len(words), i))
        i += 1
    print('%d words' % len(words))
