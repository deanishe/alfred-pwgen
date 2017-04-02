# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-01
#

"""
Pasteboard: private copy + paste
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mark data copied to pasteboard as "concealed", so clipboard
managers ignore it.
"""

from __future__ import print_function, absolute_import

import subprocess

from AppKit import NSPasteboard
from Foundation import NSData

# setting org.nspasteboard.ConcealedType to anything
# informs clipboard managers to ignore these data
# http://nspasteboard.org
UTI_PRIVATE = 'org.nspasteboard.ConcealedType'

JS_PASTE = """
ObjC.import('Carbon');

// Simulate CMD+V keypress via Carbon. Unaffected by other modifiers
// the user may be holding down.
function paste() {
  var src = $.CGEventSourceCreate($.kCGEventSourceStateCombinedSessionState);

  var pasteCommandDown = $.CGEventCreateKeyboardEvent(src, $.kVK_ANSI_V, true);
  $.CGEventSetFlags(pasteCommandDown, $.kCGEventFlagMaskCommand);
  var pasteCommandUp = $.CGEventCreateKeyboardEvent(src, $.kVK_ANSI_V, false);

  $.CGEventPost($.kCGAnnotatedSessionEventTap, pasteCommandDown);
  $.CGEventPost($.kCGAnnotatedSessionEventTap, pasteCommandUp);
}

function run(argv) {
    paste()
}
"""


def nsdata(obj):
    """Convert ``object`` to `NSData`."""
    if isinstance(obj, unicode):
        s = obj.encode('utf-8')
    else:
        s = str(obj)

    return NSData.dataWithBytes_length_(s, len(s))


def copy(data, uti='public.utf8-plain-text', private=True):
    """Put ``data`` on pasteboard with type ``uti``.

    If ``private`` is ``True`` (the default), the data are
    marked as "concealed", so clipboard managers will ignore
    them.

    Args:
        data (object): Data to put on pasteboard
        uti (str, optional): UTI for data
        private (bool, optional): Whether to hide the data from
            clipboard managers
    """
    pbdata = {uti: data}
    if private:
        pbdata[UTI_PRIVATE] = 'whateva'

    pboard = NSPasteboard.generalPasteboard()
    pboard.clearContents()

    for uti, data in pbdata.items():
        if isinstance(uti, unicode):
            uti = uti.encode('utf-8')

        pboard.setData_forType_(nsdata(data), uti)


def paste():
    """Simulate CMD+V.

    Simulate keypress via Carbon, which unlike AppleScript,
    ignores the keys the user has their fat fingers on.

    """
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', JS_PASTE]
    subprocess.check_call(cmd)
