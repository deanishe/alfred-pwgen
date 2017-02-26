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
Package containing password generators.

This module contains the machinery for loading generators and
the base class for generators.

The default generators are contained in (and loaded from) the
other modules in this package matching the pattern ``gen_*.py``.

All generators must subclass ``PassGenBase`` or ``WordGenBase``
in order to be recognised by the workflow.

"""

from __future__ import (
    print_function,
    unicode_literals,
    absolute_import,
    division
)

import abc
import logging
import math
import os
import random
import sys

__all__ = [
    'ENTROPY_PER_LEVEL',
    'get_generators',
    'get_subclasses',
    'import_generators',
    'PassGenBase',
    'punctuation',
    'WordGenBase',
]

imported_dirs = set()

log = logging.getLogger('workflow.generators')

ENTROPY_PER_LEVEL = 32

# string.punctuation contains a few characters we don't want
# like backslash and tilde
punctuation = """!"#$%&'()*+,-./:;<=>?@[]^_{|}"""


class PassGenBase(object):
    """Base class for generators.

    Generators *must* subclass this abstract base class (or
    ``WordGenBase``, which is a subclass of this class).

    If you just use ``PassGenBase.register()``, the workflow
    will not find the generator.

    Subclasses must override the ``id``, ``name``, ``description``
    and ``data`` properties to be valid generators.

    A very simple generator can just return a sequence of
    characters from ``data``. The ``password`` method of this
    base class will then generate a random password of the
    required length/strength from the interable's contents.

    """

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
        """Entropy per element (character word) in bits."""
        return math.log(len(self.data), 2)

    @abc.abstractproperty
    def id(self):
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


def _get_generator_modules(dirpath):
    """Return list of files in dirpath matching ``gen_*.py``"""
    modnames = []

    for filename in os.listdir(dirpath):
        if not filename.endswith('.py') or not filename.startswith('gen_'):
            continue

        modnames.append(os.path.splitext(filename)[0])

    return modnames


class WordGenBase(PassGenBase):
    """Base class for word-based generators.

    Usage is the same as ``PassGenBase`` except ``data`` should
    be a sequence of words, not characters.

    """

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


def import_generators(dirpath):
    """Import all ``gen_*.py`` modules within directory ``dirpath``.

    Modules will be imported under ``generators.user_<modname>``.

    As a result, user modules may override built-ins.

    """
    dirpath = os.path.abspath(dirpath)

    if dirpath in imported_dirs:
        log.debug('Directory already imported : `%s`', dirpath)
        return

    imported_dirs.add(dirpath)

    # Is ``dirpath`` this package?
    builtin = dirpath == os.path.abspath(os.path.dirname(__file__))

    if not builtin and dirpath not in sys.path:
        sys.path.append(dirpath)

    kind = ('user', 'built-in')[builtin]

    for modname in _get_generator_modules(dirpath):

        if builtin:
            modname = 'generators.%s' % modname

        try:
            __import__(modname)
            log.debug('Imported %s generators from `%s`', kind, modname)
        except Exception as err:
            log.error('Error importing `%s` : %s', modname, err)


def get_subclasses(klass):
    """Return list of all subclasses of `klass`.

    Also recurses into subclasses.

    """
    subclasses = []

    for cls in klass.__subclasses__():
        subclasses.append(cls)
        subclasses += get_subclasses(cls)

    return subclasses


def get_generators():
    """Return a list containing an instance of each available generator.

    It would be preferable to return the class (not all generators are
    needed), but abstract base classes use properties, not attributes,
    to enforce interface compliance :(

    """
    generators = []
    builtin_dir = os.path.abspath(os.path.dirname(__file__))

    # Import the built-ins only once
    if builtin_dir not in imported_dirs:
        import_generators(builtin_dir)

    for klass in get_subclasses(PassGenBase):
        # Ignore base classes
        if klass.__name__ == 'WordGenBase':
            continue

        try:
            inst = klass()
            log.debug('Loaded generator : `%s`', inst.name)
        except Exception as err:
            log.error(err)
        else:
            generators.append(inst)

    # Sort generators by strength
    generators.sort(key=lambda c: c.entropy, reverse=True)
    return generators
