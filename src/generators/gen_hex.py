#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Matthieu Baudoux <https://github.com/gabalis>,
#   Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-02-24
#

from generators import PassGenBase


class HexGenerator(PassGenBase):
    """Generate passwords made of hexadecimal characters only."""

    @property
    def id(self):
        return 'hex'

    @property
    def name(self):
        return 'Hexadecimal'

    @property
    def description(self):
        return 'Hexadecimal characters'

    @property
    def data(self):
        return '0123456789abcdef'
