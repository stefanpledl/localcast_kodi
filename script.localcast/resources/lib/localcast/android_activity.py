"""Building the Kodi built-in that hands a path to the LocalCast Android app."""

from localcast.quoting import quote_builtin_arg

#: Application id of LocalCast on Google Play.
PACKAGE = 'de.stefanpledl.localcast'

#: Android intent action used to open a media URL in LocalCast.
ACTION = 'android.intent.action.VIEW'

#: MIME type sent with the intent.  LocalCast sniffs the real type itself.
MIME_TYPE = 'video/*'

#: Kodi virtual paths that are not a media location LocalCast could open.
_VIRTUAL_PREFIXES = (
    'videodb://',
    'musicdb://',
    'library://',
    'pvr://',
    'special://',
    'addons://',
    'sources://',
)


def is_plugin_path(path):
    """Return True when *path* is served by a Kodi add-on (``plugin://``).

    Such paths are only resolved by Kodi while it plays them itself, so they
    cannot be handed to another app directly.
    """
    return bool(path) and str(path).startswith('plugin://')


def is_castable_path(path):
    """Return True when *path* is something LocalCast can open on its own.

    Empty values, ``plugin://`` paths and Kodi's virtual library protocols
    are rejected.  Anything else - bare file-system paths, ``smb://``,
    ``nfs://``, ``http(s)://`` and the like - is passed through verbatim.
    """
    if not path:
        return False
    text = str(path)
    if is_plugin_path(text):
        return False
    lowered = text.lower()
    for prefix in _VIRTUAL_PREFIXES:
        if lowered.startswith(prefix):
            return False
    return True


def start_android_activity_command(path):
    """Return the ``StartAndroidActivity`` built-in that opens *path* in LocalCast.

    The path is passed verbatim, including any ``|User-Agent=...`` header
    suffix Kodi appends to stream URLs - LocalCast parses that suffix itself.
    """
    return 'StartAndroidActivity("%s","%s","%s",%s)' % (
        PACKAGE,
        ACTION,
        MIME_TYPE,
        quote_builtin_arg(path),
    )
