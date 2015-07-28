#!/usr/bin/python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-07-27
#

"""pwgen.py <command> [options]

Generate secure passwords.

Usage:
    pwgen.py generate [-v|-q|-d] [<strength>]
    pwgen.py generate [-v|-q|-d] --length [<length>]
    pwgen.py conf [-v|-q|-d]
    pwgen.py set [-v|-q|-d] <key> <value>
    pwget.py reset [-v|-q|-d] <key>
    pwgen.py (-h|--version)

Options:
    -h, --help     Show this message and quit
    --version      Show version and exit
    -v, --verbose  Show INFO-level messages and above
    -q, --quiet    Show WARNING-level messages and above
    -d, --debug    Show all messages

"""

from __future__ import print_function, unicode_literals, absolute_import

import logging
import sys

from docopt import docopt
from workflow import Workflow, ICON_WARNING

from generators import get_generators, ENTROPY_PER_LEVEL

log = None

DEFAULT_PW_LENGTH = 20
DEFAULT_PW_STRENGTH = 3

# Characters for strength bar
BLOCK_FULL = '\u2589'
BLOCK_75 = '\u258a'
BLOCK_50 = '\u258c'
BLOCK_25 = '\u258e'
BLOCK_EMPTY = ''

DEFAULT_SETTINGS = {
    'pw_length': DEFAULT_PW_LENGTH,
    'pw_strength': DEFAULT_PW_STRENGTH,
    'strength_bar': True,
    'generators': [
        'ascii',
        'alphanumeric',
        'alphanumeric-clear',
        'pronounceable',
        'numeric',
        'dictionary',
    ],
}

UPDATE_SETTINGS = {
    'github_slug': 'deanishe/alfred-pwgen'
}

HELP_URL = ''


def pw_strength_meter(entropy):
    """Return 'graphical' bar of password strength."""
    bar = ''
    bars, rem = divmod(entropy / ENTROPY_PER_LEVEL, 1)
    bar = BLOCK_FULL * int(bars)

    if rem >= 0.75:
        bar += BLOCK_75
    elif rem >= 0.5:
        bar += BLOCK_50
    elif rem >= 0.25:
        bar += BLOCK_25

    return bar


def entropy_from_strength(strength):
    """Return bits of entropy for ``strength``.

    If ``strength`` ends in 'b', treat as bits, else
    treat as level and multiply by ``ENTROPY_PER_LEVEL``.

    """

    if not isinstance(strength, basestring):
        strength = str(strength)
    strength = strength.strip()
    if not strength:
        return None

    if strength.endswith('b'):
        return int(strength[:-1])

    return int(strength) * ENTROPY_PER_LEVEL


class PasswordApp(object):
    """Workflow application"""

    def __init__(self, wf):
        self.wf = wf
        self.query = None
        self.args = None

    def run(self):
        """Main application entry point.

        Parse command-line arguments and call appropriate `do_XXX` method.

        """

        args = self.args = docopt(__doc__,
                                  argv=self.wf.args,
                                  version=self.wf.version)

        if args.get('--verbose'):
            log.setLevel(logging.INFO)
        elif args.get('--quiet'):
            log.setLevel(logging.ERROR)
        elif args.get('--debug'):
            log.setLevel(logging.DEBUG)
        log.debug("Set log level to %s" %
                  logging.getLevelName(log.level))

        log.debug('args : %r', args)

        if args.get('generate'):
            return self.do_generate()
        elif args.get('conf'):
            return self.do_conf()

    def do_generate(self):
        """Generate and display passwords from active generators."""
        wf = self.wf
        args = self.args
        query = ''
        mode = 'strength'
        pw_length = None
        pw_strength = None

        # Determine mode
        if args.get('--length'):
            mode = 'length'
            pw_length = args.get('<length>') or ''
            pw_length = pw_length.strip()
            query = pw_length

            if pw_length:
                if not pw_length.isdigit():
                    wf.add_item('`{0}` is not a number'.format(pw_length),
                                'Usage: pwgen [length]',
                                icon=ICON_WARNING)
                    wf.send_feedback()
                    return 0

                pw_length = int(pw_length)

            pw_length = pw_length or wf.settings.get('pw_length',
                                                     DEFAULT_PW_LENGTH)

            log.info('Password length: %d', pw_length)

        else:  # Default strength mode
            pw_strength = args.get('<strength>') or ''
            query = pw_strength
            try:
                pw_strength = entropy_from_strength(pw_strength)
            except ValueError:
                wf.add_item('`{0}` is not a number'.format(pw_strength),
                            'Usage: pwgen [length]',
                            icon=ICON_WARNING)
                wf.send_feedback()
                return 0

            pw_strength = (
                pw_strength or
                entropy_from_strength(wf.settings.get('pw_strength',
                                                      DEFAULT_PW_STRENGTH)))

            log.info('Password strength: %d bits', pw_strength)

        generators = get_generators()

        # Filter out inactive generators
        active_generators = wf.settings.get('generators', [])
        if len(active_generators):
            generators = [g for g in generators if g.id_ in active_generators]

        log.debug('%d active generators', len(generators))

        if not len(generators):
            wf.add_item('No active generators',
                        'Use `pwconf` to activate some generators',
                        icon=ICON_WARNING)

        for g in generators:
            log.debug('[%0.2f/%s] %s : %s',
                      g.entropy, g.id_, g.name, g.description)
            # log.debug('[%s] %s', g.id_, g.password())
            if mode == 'length':
                pw, entropy = g.password(length=pw_length)
                # subtitle = 'Strength : %0.2f  // %s' % (entropy, g.description)
            else:
                pw, entropy = g.password(strength=pw_strength)

            if wf.settings.get('strength_bar'):
                strength = pw_strength_meter(entropy)
            else:
                strength = 'Strength : %0.1f bits' % entropy

            subtitle = ('%s // Length : %d  // %s' %
                        (strength, len(pw), g.description))
            # subtitle = ('Strength : %0.2f // Length : %d  // %s' %
            #             (entropy, len(pw), g.description))

            wf.add_item(pw,
                        subtitle,
                        arg=pw, uid=g.id_,
                        autocomplete=query,
                        valid=True,
                        copytext=pw,
                        largetext=pw)

        wf.send_feedback()
        return 0

    def do_conf(self):
        """Show configuration options"""


def main(wf):
    app = PasswordApp(wf)
    return app.run()


if __name__ == '__main__':
    wf = Workflow(
        default_settings=DEFAULT_SETTINGS)
    log = wf.logger
    sys.exit(wf.run(main))
