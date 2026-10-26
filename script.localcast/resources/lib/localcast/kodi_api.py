"""Thin wrappers around the Kodi Python API.

This is the only module in the add-on that imports ``xbmc``, ``xbmcgui``,
``xbmcvfs`` and ``xbmcaddon``.  Everything else stays testable without Kodi.
"""

import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

ADDON_ID = 'script.localcast'
LOG_PREFIX = '[' + ADDON_ID + '] '


# -- environment -------------------------------------------------------------

def is_android():
    """Return True when Kodi runs on Android."""
    return bool(xbmc.getCondVisibility('System.Platform.Android'))


def listitem_path():
    """Return the path of the focused list item, or '' when there is none.

    Context-menu scripts receive the item as ``sys.listitem``; the info label
    is the fallback for every other entry point.
    """
    try:
        item = getattr(sys, 'listitem', None)
        if item is not None:
            path = item.getPath()
            if path:
                return path
    except Exception:  # pylint: disable=broad-except
        pass
    try:
        return xbmc.getInfoLabel('ListItem.FileNameAndPath') or ''
    except Exception:  # pylint: disable=broad-except
        return ''


# -- file system -------------------------------------------------------------

def translate_path(special_path):
    """Map a ``special://`` URL to a real path."""
    return xbmcvfs.translatePath(special_path)


def exists(path):
    """Return True when *path* exists in Kodi's virtual file system."""
    return bool(xbmcvfs.exists(path))


def read_text(path):
    """Return the UTF-8 text content of *path* ('' when it cannot be read)."""
    handle = xbmcvfs.File(path)
    try:
        data = handle.readBytes()
    finally:
        handle.close()
    if isinstance(data, bytes):
        return data.decode('utf-8', 'replace')
    return str(data or '')


def write_text(path, text):
    """Write *text* to *path*, replacing any existing file."""
    handle = xbmcvfs.File(path, 'w')
    try:
        if not handle.write(text):
            raise IOError('xbmcvfs could not write ' + path)
    finally:
        handle.close()


def delete(path):
    """Delete *path*; return True on success."""
    return bool(xbmcvfs.delete(path))


def copy(source, destination):
    """Copy *source* to *destination*; return True on success."""
    return bool(xbmcvfs.copy(source, destination))


# -- strings and dialogs -----------------------------------------------------

def addon_name():
    """Return the add-on's display name."""
    return xbmcaddon.Addon().getAddonInfo('name') or 'LocalCast'


def localized(string_id):
    """Return the add-on string with *string_id* in the user's language."""
    return xbmcaddon.Addon().getLocalizedString(string_id)


def yesno(message, heading=None):
    """Show a yes/no dialog; return True when the user picked yes."""
    return bool(xbmcgui.Dialog().yesno(heading or addon_name(), message))


def ok(message, heading=None):
    """Show an OK dialog and wait for it to be dismissed."""
    xbmcgui.Dialog().ok(heading or addon_name(), message)


def notification(message, heading=None, time_ms=4000):
    """Show a toast notification with the add-on icon."""
    icon = xbmcaddon.Addon().getAddonInfo('icon') or xbmcgui.NOTIFICATION_INFO
    xbmcgui.Dialog().notification(heading or addon_name(), message, icon, time_ms)


def select(options, heading=None):
    """Show a selection list; return the chosen index or -1 when cancelled."""
    return xbmcgui.Dialog().select(heading or addon_name(), list(options))


# -- actions -----------------------------------------------------------------

def quit_kodi():
    """Ask Kodi to quit."""
    xbmc.executebuiltin('Quit')


def run_builtin(command):
    """Execute a Kodi built-in function."""
    xbmc.executebuiltin(command)


def log(message):
    """Write *message* to the Kodi log at INFO level."""
    xbmc.log(LOG_PREFIX + str(message), xbmc.LOGINFO)
