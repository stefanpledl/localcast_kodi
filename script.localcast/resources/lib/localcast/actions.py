"""What the add-on does: the settings buttons, the menu and the context item."""

from localcast import android_activity
from localcast import kodi_api
from localcast import playercorefactory

# String ids from resources/language/*/strings.po
STR_CONTEXT_LABEL = 32001
STR_ENABLE = 32013
STR_DISABLE = 32015
STR_STATUS = 32017
STR_HELP = 32019
STR_REPLACE_FOREIGN = 32031
STR_RESTART_NOW = 32032
STR_RESTART_LATER = 32033
STR_ALREADY_OFF = 32034
STR_FOREIGN_NOT_DELETED = 32035
STR_RESTORE_BACKUP = 32036
STR_STATUS_ENABLED = 32037
STR_STATUS_DISABLED = 32038
STR_STATUS_FOREIGN = 32039
STR_FILE_LINE = 32040
STR_HELP_TEXT = 32041
STR_ANDROID_ONLY = 32042
STR_NOTHING_TO_CAST = 32043
STR_PLUGIN_ITEM = 32044
STR_SENT = 32045
STR_ERROR = 32046
STR_BACKUP_RESTORED = 32047

_STATUS_STRINGS = {
    playercorefactory.ENABLED: STR_STATUS_ENABLED,
    playercorefactory.DISABLED: STR_STATUS_DISABLED,
    playercorefactory.FOREIGN: STR_STATUS_FOREIGN,
}


def _xml_path():
    return playercorefactory.profile_xml_path(kodi_api.translate_path)


def _current_status(path):
    """Return (status, exists) for the playercorefactory.xml at *path*."""
    if not kodi_api.exists(path):
        return playercorefactory.DISABLED
    ours = playercorefactory.is_ours(kodi_api.read_text(path))
    return playercorefactory.status_of(True, ours)


def _prompt_restart():
    if kodi_api.yesno(kodi_api.localized(STR_RESTART_NOW)):
        kodi_api.log('user chose to quit Kodi after changing playercorefactory.xml')
        kodi_api.quit_kodi()
    else:
        kodi_api.notification(kodi_api.localized(STR_RESTART_LATER))


# -- settings actions --------------------------------------------------------

def enable_automatic_casting():
    """Write our playercorefactory.xml, backing up a foreign one first."""
    path = _xml_path()
    status = _current_status(path)
    if status == playercorefactory.FOREIGN:
        if not kodi_api.yesno(kodi_api.localized(STR_REPLACE_FOREIGN)):
            kodi_api.log('enable cancelled: foreign playercorefactory.xml kept')
            return
        backup = playercorefactory.backup_path(path)
        if not kodi_api.copy(path, backup):
            raise IOError('could not back up ' + path + ' to ' + backup)
        kodi_api.log('backed up foreign playercorefactory.xml to ' + backup)
    kodi_api.write_text(path, playercorefactory.PLAYERCOREFACTORY_XML)
    kodi_api.log('wrote ' + path)
    _prompt_restart()


def disable_automatic_casting():
    """Delete our playercorefactory.xml and offer to restore a backup."""
    path = _xml_path()
    status = _current_status(path)
    if status == playercorefactory.DISABLED:
        kodi_api.notification(kodi_api.localized(STR_ALREADY_OFF))
        return
    if status == playercorefactory.FOREIGN:
        kodi_api.ok(kodi_api.localized(STR_FOREIGN_NOT_DELETED))
        return
    if not kodi_api.delete(path):
        raise IOError('could not delete ' + path)
    kodi_api.log('deleted ' + path)
    backup = playercorefactory.backup_path(path)
    if kodi_api.exists(backup):
        if kodi_api.yesno(kodi_api.localized(STR_RESTORE_BACKUP)):
            if not kodi_api.copy(backup, path):
                raise IOError('could not restore ' + backup + ' to ' + path)
            kodi_api.delete(backup)
            kodi_api.log('restored ' + backup)
            kodi_api.notification(kodi_api.localized(STR_BACKUP_RESTORED))
    _prompt_restart()


def show_status():
    """Tell the user whether automatic casting is on, off or blocked."""
    path = _xml_path()
    status = _current_status(path)
    message = kodi_api.localized(_STATUS_STRINGS[status])
    file_line = kodi_api.localized(STR_FILE_LINE) % path
    kodi_api.ok(message + '[CR][CR]' + file_line)


def show_help():
    """Explain the two ways of casting and the prerequisites."""
    kodi_api.ok(kodi_api.localized(STR_HELP_TEXT))


def show_main_menu():
    """Offer the four actions in a list and run the chosen one."""
    entries = (
        (STR_ENABLE, enable_automatic_casting),
        (STR_DISABLE, disable_automatic_casting),
        (STR_STATUS, show_status),
        (STR_HELP, show_help),
    )
    labels = [kodi_api.localized(string_id) for string_id, _ in entries]
    choice = kodi_api.select(labels)
    if 0 <= choice < len(entries):
        entries[choice][1]()


# -- context menu ------------------------------------------------------------

def cast_listitem():
    """Hand the focused list item to LocalCast (context menu entry)."""
    if not kodi_api.is_android():
        kodi_api.notification(kodi_api.localized(STR_ANDROID_ONLY))
        return
    path = kodi_api.listitem_path()
    if not path:
        kodi_api.notification(kodi_api.localized(STR_NOTHING_TO_CAST))
        return
    if android_activity.is_plugin_path(path) or not android_activity.is_castable_path(path):
        kodi_api.log('context cast refused for non-castable path ' + path)
        kodi_api.ok(kodi_api.localized(STR_PLUGIN_ITEM))
        return
    command = android_activity.start_android_activity_command(path)
    kodi_api.log('context cast: ' + command)
    kodi_api.run_builtin(command)
    kodi_api.notification(kodi_api.localized(STR_SENT))


# -- entry point helpers -----------------------------------------------------

ACTIONS = {
    'enable': enable_automatic_casting,
    'disable': disable_automatic_casting,
    'status': show_status,
    'help': show_help,
}


def run(argv):
    """Dispatch ``default.py``'s command line: one action name or the menu."""
    name = argv[1].strip().lower() if len(argv) > 1 else ''
    action = ACTIONS.get(name)
    if action is None:
        if name:
            kodi_api.log('unknown action "%s", showing menu' % name)
        action = show_main_menu
    action()


def report_error(exc, traceback_text):
    """Log a traceback and tell the user something went wrong."""
    kodi_api.log('unhandled error: ' + traceback_text)
    try:
        kodi_api.ok(kodi_api.localized(STR_ERROR) % type(exc).__name__)
    except Exception:  # pylint: disable=broad-except
        kodi_api.ok('LocalCast add-on error: ' + type(exc).__name__)
