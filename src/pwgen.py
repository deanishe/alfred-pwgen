#!/usr/bin/python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-07-27
#

"""pwgen.py command [options]

Usage:
    pwgen.py generate [-v|-q|-d] [<length>]
    pwgen.py conf [-v|-q|-d] [<query>]
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

from generators import get_generators

log = None

DEFAULT_PW_LENGTH = 30

DEFAULT_SETTINGS = {
    'pw_length': DEFAULT_PW_LENGTH,
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
        pw_length = self.args.get('<length>') or ''
        pw_length = pw_length.strip()

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
            pw, entropy = g.password(pw_length)
            subtitle = 'Strength : %0.2f  // %s' % (entropy, g.description)
            wf.add_item(pw,
                        subtitle,
                        arg=pw, uid=g.id_,
                        autocomplete='{0}'.format(pw_length),
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
