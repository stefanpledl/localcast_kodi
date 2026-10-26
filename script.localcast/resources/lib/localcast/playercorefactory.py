"""The playercorefactory.xml that routes every video Kodi plays to LocalCast.

Kodi reads ``special://profile/playercorefactory.xml`` at start-up.  With an
``ExternalPlayer`` entry whose filename is an Android package id, Kodi on
Android launches that package with the media URL instead of playing it
itself.  The rules below send every video, SMB path, disc image and internet
stream that way.  There are deliberately no ``rtmp``/``rtsp`` rules: LocalCast
cannot play those protocols.
"""

#: Comment Kodi keeps verbatim; its presence tells us the file is ours.
MARKER = ('<!-- Written by the LocalCast Kodi add-on (script.localcast). '
          'Delete this file to restore Kodi\'s own player. -->')

PLAYERCOREFACTORY_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Written by the LocalCast Kodi add-on (script.localcast). Delete this file to restore Kodi's own player. -->
<playercorefactory>
  <players>
    <player name="LocalCast" type="ExternalPlayer" audio="false" video="true">
      <filename>de.stefanpledl.localcast</filename>
      <hidexbmc>true</hidexbmc>
      <playcountminimumtime>120</playcountminimumtime>
    </player>
  </players>
  <rules action="prepend">
    <rule protocols="smb" player="LocalCast"/>
    <rule dvdimage="true" player="LocalCast"/>
    <rule internetstream="true" player="LocalCast"/>
    <rule video="true" player="LocalCast"/>
  </rules>
</playercorefactory>
'''

#: File name of the player configuration inside the Kodi profile folder.
FILE_NAME = 'playercorefactory.xml'

#: Suffix of the backup written before a foreign file is replaced.
BACKUP_SUFFIX = '.localcast.bak'

#: Automatic casting is on: our file is in place.
ENABLED = 'enabled'
#: A playercorefactory.xml exists that we did not write.
FOREIGN = 'foreign'
#: No playercorefactory.xml exists.
DISABLED = 'disabled'

STATUSES = (ENABLED, FOREIGN, DISABLED)


def is_ours(xml_text):
    """Return True when *xml_text* carries the LocalCast marker comment."""
    if not xml_text:
        return False
    return MARKER in str(xml_text)


def profile_xml_path(translate_path):
    """Return the real path of ``special://profile/playercorefactory.xml``.

    *translate_path* is ``xbmcvfs.translatePath`` (or any callable that maps
    a ``special://`` URL to a real path).  A missing trailing separator on
    the translated folder is tolerated.
    """
    folder = translate_path('special://profile/') or ''
    if folder and not folder.endswith(('/', '\\')):
        folder += '/'
    return folder + FILE_NAME


def backup_path(xml_path):
    """Return the path of the backup kept next to *xml_path*."""
    return xml_path + BACKUP_SUFFIX


def status_of(exists, ours):
    """Map the two facts about the file to ENABLED, FOREIGN or DISABLED."""
    if not exists:
        return DISABLED
    if ours:
        return ENABLED
    return FOREIGN
