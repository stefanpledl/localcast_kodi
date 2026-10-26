"""In-memory stand-ins for the xbmc* modules so actions.py can be exercised.

``install()`` puts fake ``xbmc``, ``xbmcgui``, ``xbmcvfs`` and ``xbmcaddon``
modules into ``sys.modules`` and returns the shared ``FakeKodi`` state.  The
localized strings come from the real en_GB strings.po, so a string id that
actions.py uses but the PO file lacks fails loudly.
"""

import os
import re
import sys
import types

ADDON_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'script.localcast')
LANGUAGE_DIR = os.path.join(ADDON_DIR, 'resources', 'language')

_MSG_RE = re.compile(r'msgctxt "#(\d+)"\s*\nmsgid "((?:[^"\\]|\\.)*)"\s*\nmsgstr "((?:[^"\\]|\\.)*)"')


def _unescape(text):
    return text.replace('\\"', '"').replace('\\n', '\n')


def load_po(locale):
    """Return {id: (msgid, msgstr)} for resource.language.<locale>/strings.po."""
    path = os.path.join(LANGUAGE_DIR, 'resource.language.' + locale, 'strings.po')
    with open(path, 'r', encoding='utf-8') as handle:
        data = handle.read()
    return {int(num): (_unescape(msgid), _unescape(msgstr))
            for num, msgid, msgstr in _MSG_RE.findall(data)}


class FakeKodi(object):
    """Shared state behind the fake modules."""

    PROFILE = '/data/user/0/org.xbmc.kodi/files/.kodi/userdata/'

    def __init__(self):
        self.files = {}
        self.log_lines = []
        self.builtins = []
        self.notifications = []
        self.ok_dialogs = []
        self.yesno_questions = []
        self.yesno_answers = []
        self.select_choices = []
        self.select_options = []
        self.android = True
        self.listitem_path = ''
        self.infolabels = {}
        self.strings = {num: msgid for num, (msgid, _) in load_po('en_gb').items()}
        self.copy_fails = False
        self.delete_fails = False

    # -- helpers used by the tests ------------------------------------------

    def answer_yesno(self, *answers):
        self.yesno_answers.extend(answers)

    def choose(self, *indexes):
        self.select_choices.extend(indexes)

    def xml_path(self):
        return self.PROFILE + 'playercorefactory.xml'

    def backup_path(self):
        return self.xml_path() + '.localcast.bak'


def install():
    """Install fake xbmc* modules and return the FakeKodi behind them."""
    state = FakeKodi()

    # -- xbmc --
    xbmc = types.ModuleType('xbmc')
    xbmc.LOGINFO = 1
    xbmc.LOGERROR = 4

    def getCondVisibility(condition):
        if condition == 'System.Platform.Android':
            return state.android
        return False

    def getInfoLabel(label):
        return state.infolabels.get(label, '')

    def executebuiltin(command, wait=False):
        state.builtins.append(command)

    def log(message, level=1):
        state.log_lines.append(message)

    xbmc.getCondVisibility = getCondVisibility
    xbmc.getInfoLabel = getInfoLabel
    xbmc.executebuiltin = executebuiltin
    xbmc.log = log

    # -- xbmcgui --
    xbmcgui = types.ModuleType('xbmcgui')
    xbmcgui.NOTIFICATION_INFO = 'info'

    class Dialog(object):

        def yesno(self, heading, message, *args, **kwargs):
            state.yesno_questions.append(message)
            if not state.yesno_answers:
                raise AssertionError('unexpected yesno: ' + message)
            return state.yesno_answers.pop(0)

        def ok(self, heading, message, *args, **kwargs):
            state.ok_dialogs.append(message)
            return True

        def notification(self, heading, message, icon=None, time=5000, sound=True):
            state.notifications.append(message)

        def select(self, heading, options, *args, **kwargs):
            state.select_options.append(list(options))
            if not state.select_choices:
                return -1
            return state.select_choices.pop(0)

    xbmcgui.Dialog = Dialog

    # -- xbmcvfs --
    xbmcvfs = types.ModuleType('xbmcvfs')

    def translatePath(path):
        if path == 'special://profile/':
            return state.PROFILE
        return path

    def exists(path):
        return path in state.files

    class File(object):

        def __init__(self, path, mode='r'):
            self.path = path
            self.mode = mode
            self.closed = False
            if mode == 'w':
                state.files[path] = b''

        def readBytes(self, numbytes=0):
            return state.files.get(self.path, b'')

        def read(self, numbytes=0):
            return self.readBytes().decode('utf-8')

        def write(self, data):
            if isinstance(data, str):
                data = data.encode('utf-8')
            state.files[self.path] = state.files.get(self.path, b'') + data
            return True

        def close(self):
            self.closed = True

    def delete(path):
        if state.delete_fails:
            return False
        return state.files.pop(path, None) is not None

    def copy(source, destination):
        if state.copy_fails or source not in state.files:
            return False
        state.files[destination] = state.files[source]
        return True

    xbmcvfs.translatePath = translatePath
    xbmcvfs.exists = exists
    xbmcvfs.File = File
    xbmcvfs.delete = delete
    xbmcvfs.copy = copy

    # -- xbmcaddon --
    xbmcaddon = types.ModuleType('xbmcaddon')

    class Addon(object):

        def __init__(self, addon_id=None):
            self.addon_id = addon_id or 'script.localcast'

        def getLocalizedString(self, string_id):
            if string_id not in state.strings:
                raise KeyError('string id %d missing from strings.po' % string_id)
            return state.strings[string_id]

        def getAddonInfo(self, key):
            return {'name': 'LocalCast', 'id': 'script.localcast',
                    'icon': '/addons/script.localcast/icon.png'}.get(key, '')

    xbmcaddon.Addon = Addon

    forget()
    for name, module in (('xbmc', xbmc), ('xbmcgui', xbmcgui),
                         ('xbmcvfs', xbmcvfs), ('xbmcaddon', xbmcaddon)):
        sys.modules[name] = module

    return state


def forget():
    """Drop the fake modules and the add-on modules bound to them.

    ``from localcast import actions`` reuses the attribute on the already
    imported ``localcast`` package without re-importing, so the attributes
    have to go as well - otherwise a later test talks to the previous test's
    fakes.
    """
    for name in ('xbmc', 'xbmcgui', 'xbmcvfs', 'xbmcaddon',
                 'localcast.actions', 'localcast.kodi_api'):
        sys.modules.pop(name, None)
    package = sys.modules.get('localcast')
    if package is not None:
        for name in ('actions', 'kodi_api'):
            package.__dict__.pop(name, None)
