import string
from generators import PassGenBase

class HexGenerator(PassGenBase):
    """Generate passwords made of hexadecimal chars only."""

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