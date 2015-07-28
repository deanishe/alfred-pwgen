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
Package containing password generators.
"""

from __future__ import print_function, unicode_literals, absolute_import

import logging
import os

from .base import PassGenBase

__all__ = ['get_subclasses', 'get_generators']

_import_done = False

log = logging.getLogger('workflow.generators')


def _import_generators():
    """Import all generator modules within this package."""
    global _import_done
    # Import all modules in this directory that match `gen_*.py`
    dirpath = os.path.dirname(__file__)
    for filename in os.listdir(dirpath):
        if not filename.endswith('.py') or not filename.startswith('gen_'):
            continue
        modname = filename[:-3]  # Remove extension
        log.debug('Importing generators from : %s ...', modname)
        try:
            __import__('generators.{0}'.format(modname))
        except Exception as err:
            log.error("Couldn't import `%s` : %s", modname, err)
    _import_done = True


def get_subclasses(klass):
    """Return list of all subclasses of `klass`.

    Also recurses into subclasses.

    """

    subclasses = []
    for klass in klass.__subclasses__():
        subclasses.append(klass)
        subclasses += get_subclasses(klass)
    return subclasses


def get_generators():
    """Return a list containing an instance of each available generator."""
    generators = []

    if not _import_done:
        _import_generators()

    for klass in get_subclasses(PassGenBase):
        try:
            inst = klass()
        except Exception as err:
            log.error(err)
        else:
            generators.append(inst)

    # Sort generators by strength
    generators.sort(key=lambda c: c.entropy, reverse=True)
    return generators
