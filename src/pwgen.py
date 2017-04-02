#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2015 Dean Jackson <deanishe@deanishe.net>
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
    pwgen.py conf [-v|-q|-d] [<query>]
    pwgen.py copy [-v|-q|-d] [-p] <password>
    pwgen.py notify [-v|-q|-d] <message>
    pwgen.py set [-v|-q|-d] <key> [<value>]
    pwgen.py toggle [-v|-q|-d] <genid>
    pwgen.py (-h|--version)

Options:
    -p, --paste    Also paste password to frontmost application
    -h, --help     Show this message and quit
    --version      Show version and exit
    -v, --verbose  Show INFO-level messages and above
    -q, --quiet    Show WARNING-level messages and above
    -d, --debug    Show all messages

"""

from __future__ import print_function, unicode_literals, absolute_import

import logging
import os
import subprocess
import sys

from docopt import docopt
from workflow import Workflow3

from generators import get_generators, ENTROPY_PER_LEVEL, import_generators

log = None

DEFAULT_PW_LENGTH = 20
DEFAULT_PW_STRENGTH = 3

# Less entropy means a weak password
STRENGTH_WEAK = 64
# More entropy means a strong password
STRENGTH_STRONG = 96

ICON_WORKFLOW = 'icon.png'

ICON_STRONG = 'icons/strong.icns'
ICON_OKAY = 'icons/okay.icns'
ICON_WEAK = 'icons/weak.icns'

ICON_TOGGLE_ON = 'icons/toggle-on.icns'
ICON_TOGGLE_OFF = 'icons/toggle-off.icns'

ICON_UPDATE_AVAILABLE = 'icons/update-available.icns'
ICON_UPDATE_NONE = 'icons/update-none.icns'

ICON_HELP = 'icons/help.icns'
ICON_SETTINGS = 'icons/option.icns'
ICON_WARNING = 'icons/warning.icns'

# Alfred keywords
KEYWORD_GEN = 'pwgen'
KEYWORD_LEN = 'pwlen'
KEYWORD_CONF = 'pwconf'

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

HELP_URL = 'https://github.com/deanishe/alfred-pwgen#alfred-password-generator'

# AppleScript to call Alfred
ALFRED_AS = """\
tell application "Alfred 3"
    {0}
end tell
"""


def call_alfred_search(query):
    """Call Alfred with ``query``."""
    command = 'search "{0}"'.format(query)
    cmd = [b'/usr/bin/osascript', b'-e',
           ALFRED_AS.format(command).encode('utf-8')]
    subprocess.call(cmd)


def call_external_trigger(name, arg=None):
    """Call External Trigger ``name`` with optional ``arg``."""
    command = 'run trigger "{0}" in workflow "{1}"'.format(name, wf.bundleid)
    if arg is not None:
        command += ' with argument "{0}"'.format(arg)

    cmd = [b'/usr/bin/osascript', b'-e',
           ALFRED_AS.format(command).encode('utf-8')]
    subprocess.call(cmd)


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


def pw_strength_icon(entropy):
    """Return path to appropriate icon for entropy."""
    if entropy <= STRENGTH_WEAK:
        return ICON_WEAK
    if entropy >= STRENGTH_STRONG:
        return ICON_STRONG
    return ICON_OKAY


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
    """Workflow application."""

    def __init__(self, wf):
        """Create new `PasswordApp` with the active `Workflow` object."""
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

        log.debug('args=\n%r', args)

        for action in ('conf',
                       'copy',
                       'generate',
                       'notify',
                       'set',
                       'toggle'):

            if args.get(action):
                meth = 'do_' + action
                log.debug('calling %r ...', meth)
                return getattr(self, meth)()

        raise SystemExit('unknown action')

    def load_user_generators(self):
        """Ensure any user generators are loaded."""
        user_generator_dir = wf.datafile('generators')

        # Create user generator directory
        if not os.path.exists(user_generator_dir):
            os.makedirs(user_generator_dir, 0700)
        else:  # Import user generators
            import_generators(user_generator_dir)

    def do_notify(self):
        """Show a notification."""
        wf = self.wf
        args = self.args
        msg = args.get('<message>')
        if wf.settings.get('suppress_notifications'):
            log.debug('Notifications turned off')
            return

        if msg.strip() == '':
            log.debug('Empty notification')
            return

        from workflow.notify import notify
        notify('Password Generator', msg)

    def do_generate(self):
        """Generate and display passwords from active generators."""
        wf = self.wf
        args = self.args
        query = ''
        mode = 'strength'
        pw_length = None
        pw_strength = None

        if wf.update_available:
            wf.add_item('An Update is Available',
                        '↩ or ⇥ to install update',
                        autocomplete='workflow:update',
                        icon=ICON_UPDATE_AVAILABLE)

        # Determine mode
        if args.get('--length'):
            mode = 'length'
            pw_length = args.get('<length>') or ''
            pw_length = pw_length.strip()
            query = pw_length

            if pw_length:
                if not pw_length.isdigit():
                    wf.add_item('`{0}` is not a number'.format(pw_length),
                                'Usage: pwlen [length]',
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
                            'Usage: pwgen [strength]',
                            icon=ICON_WARNING)
                wf.send_feedback()
                return 0

            pw_strength = (
                pw_strength or
                entropy_from_strength(wf.settings.get('pw_strength',
                                                      DEFAULT_PW_STRENGTH)))

            log.info('Password strength: %d bits', pw_strength)

        self.load_user_generators()
        generators = get_generators()

        # Filter out inactive generators
        active_generators = wf.settings.get('generators', [])
        if len(active_generators):
            generators = [g for g in generators if g.id in active_generators]

        log.debug('%d active generators', len(generators))

        if not len(generators):
            wf.add_item('No active generators',
                        'Use `pwconf` to activate some generators',
                        icon=ICON_WARNING)

        for g in generators:
            log.debug('[%0.2f/%s] %s : %s',
                      g.entropy, g.id, g.name, g.description)
            # log.debug('[%s] %s', g.id, g.password())
            if mode == 'length':
                pw, entropy = g.password(length=pw_length)
            else:
                pw, entropy = g.password(strength=pw_strength)

            if wf.settings.get('strength_bar'):
                strength = pw_strength_meter(entropy)
            else:
                strength = 'Strength : %0.1f bits //' % entropy

            subtitle = ('%s Length : %d  // %s' %
                        (strength, len(pw), g.description))

            icon = pw_strength_icon(entropy)

            it = wf.add_item(pw,
                             subtitle,
                             arg=pw, uid=g.id,
                             autocomplete=query,
                             valid=True,
                             copytext=pw,
                             largetext=pw,
                             icon=icon)

            it.setvar('notification', 'Password copied to clipboard')
            it.setvar('action', 'copy')

            m = it.add_modifier('cmd', subtitle='Copy to clipboard and '
                                'paste to frontmost application', arg=pw)
            m.setvar('action', 'paste')

            m = it.add_modifier('alt',
                                subtitle='Copy to clipboard as public data',
                                arg=pw)
            m.setvar('action', 'public-copy')

            m = it.add_modifier('ctrl',
                                subtitle='Copy to clipboard as public data '
                                'and paste to frontmost application', arg=pw)
            m.setvar('action', 'public-paste')

        wf.send_feedback()
        return 0

    def do_conf(self):
        """Show configuration options."""
        args = self.args
        wf = self.wf
        query = args.get('<query>')
        options = []

        # Update status
        if wf.update_available:
            options.append(
                {
                    'title': 'An Update is Available',
                    'subtitle': '↩ or ⇥ to install update',
                    'autocomplete': 'workflow:update',
                    'icon': ICON_UPDATE_AVAILABLE,
                }
            )
        else:
            options.append(
                {
                    'title': 'No Update Available',
                    'subtitle': '↩ or ⇥ to check for an update',
                    'autocomplete': 'workflow:update',
                    'icon': ICON_UPDATE_NONE,
                }
            )

        # Help file
        options.append(
            {
                'title': 'Open Help',
                'subtitle': 'View online help in your browser',
                'autocomplete': 'workflow:help',
                'icon': ICON_HELP,
            }
        )

        # Settings
        options.append(
            {
                'title': 'Default Password Strength : {0}'.format(
                    wf.settings.get('pw_strength')),
                'subtitle': '↩ or ⇥ to change',
                'arg': 'set pw_strength',
                'valid': True,
                'icon': ICON_SETTINGS,
            }
        )

        options.append(
            {
                'title': 'Default Password Length : {0}'.format(
                    wf.settings.get('pw_length')),
                'subtitle': '↩ or ⇥ to change',
                'arg': 'set pw_length',
                'valid': True,
                'icon': ICON_SETTINGS,
            }
        )

        # Show notifications
        if wf.settings.get('suppress_notifications'):
            icon = ICON_TOGGLE_OFF
        else:
            icon = ICON_TOGGLE_ON
        options.append(
            {
                'title': 'Show notifications',
                'subtitle': 'Show a notification when a password is copied',
                'arg': 'toggle notifications',
                'valid': True,
                'icon': icon,
            }
        )

        # Strength bar
        if wf.settings.get('strength_bar'):
            icon = ICON_TOGGLE_ON
        else:
            icon = ICON_TOGGLE_OFF
        options.append(
            {
                'title': 'Strength Bar',
                'subtitle': 'Show password strength as a bar, not bits',
                'arg': 'toggle strength_bar',
                'valid': True,
                'icon': icon,
            }
        )

        # Generators
        self.load_user_generators()
        generators = get_generators()
        active_generators = wf.settings.get('generators', [])

        for gen in generators:
            if gen.id in active_generators:
                icon = ICON_TOGGLE_ON
            else:
                icon = ICON_TOGGLE_OFF
            options.append(
                {
                    'title': 'Generator : {0}'.format(gen.name),
                    'subtitle': gen.description,
                    'arg': 'toggle {0}'.format(gen.id),
                    'valid': True,
                    'icon': icon,
                }
            )

        if query:
            options = wf.filter(query, options, key=lambda d: d.get('title'),
                                min_score=30)

        if not options:
            wf.add_item('No matching items',
                        'Try a different query',
                        icon=ICON_WARNING)

        for opt in options:
            wf.add_item(**opt)

        wf.send_feedback()
        return 0

    def do_copy(self):
        """Securely copy (and optionally paste) password to pasteboard.

        Mark pasteboard data as concealed so clipboard history managers
        ignore them.

        """
        import pasteboard as pb

        password = self.args['<password>']
        if not password:
            raise ValueError('Password is empty')

        pb.copy(password, private=True)
        log.info('password copied to clipboard')

        if self.args['--paste']:
            # time.sleep(0.1)  # give copy time to complete
            log.debug('pasting ...')
            pb.paste()

    def do_set(self):
        """Set password strength/length."""
        wf = self.wf
        args = self.args
        key = args.get('<key>')
        value = args.get('<value>')
        if not value:
            return call_external_trigger(key, '')

        if not value.isdigit():
            msg = '`{0}` is not a number'.format(value)
            log.critical(msg)
            print('ERROR : {0}'.format(msg))
            call_alfred_search(KEYWORD_CONF + ' ')
            return 1

        value = int(value)

        if key == 'pw_strength':
            wf.settings['pw_strength'] = value
            print('Set default password strength to {0}'.format(value))
        if key == 'pw_length':
            wf.settings['pw_length'] = value
            print('Set default password length to {0}'.format(value))

        # call_alfred_search(KEYWORD_CONF + ' ')
        return 0

    def do_toggle(self):
        """Toggle generators on/off."""
        wf = self.wf
        args = self.args
        gen_id = args.get('<genid>')

        log.debug('toggling=%r', gen_id)

        # Strength bar toggle
        if gen_id == 'strength_bar':
            if wf.settings.get('strength_bar'):
                log.debug('Turning strength bar off...')
                wf.settings['strength_bar'] = False
                mode = 'off'
            else:
                log.debug('Turning strength bar on...')
                wf.settings['strength_bar'] = True
                mode = 'on'
            print('Turned strength bar {0}'.format(mode))

        # Notifications toggle
        elif gen_id == 'notifications':
            if wf.settings.get('suppress_notifications'):
                log.debug('Turning notifications on...')
                del wf.settings['suppress_notifications']
                mode = 'on'
            else:
                log.debug('Turning notifications off...')
                wf.settings['suppress_notifications'] = True
                mode = 'off'

        else:  # Generator toggles

            self.load_user_generators()

            gen = None
            for g in get_generators():
                if g.id == gen_id:
                    gen = g
                    break
            if not gen:
                log.critical('Unknown generator : %s', gen_id)
                return 1

            active_generators = wf.settings.get('generators', [])[:]
            if gen_id in active_generators:
                active_generators.remove(gen_id)
                log.info('Turned generator `%s` off', gen.name)
                mode = 'off'
            else:
                active_generators.append(gen_id)
                log.info('Turned generator `%s` on', gen.name)
                mode = 'on'
            log.debug('Active generators : %s', active_generators)
            wf.settings['generators'] = active_generators

            print("Turned generator '{0}' {1}".format(gen.name, mode))
        # call_alfred_search(KEYWORD_CONF + ' ')
        call_external_trigger('conf')
        return 0


def main(wf):
    """Run workflow."""
    app = PasswordApp(wf)
    return app.run()


if __name__ == '__main__':
    wf = Workflow3(
        default_settings=DEFAULT_SETTINGS,
        update_settings=UPDATE_SETTINGS,
        help_url=HELP_URL)
    log = wf.logger
    sys.exit(wf.run(main))
