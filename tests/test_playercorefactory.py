import unittest
import xml.etree.ElementTree as ET

from tests import _path  # noqa: F401  (adds resources/lib to sys.path)

from localcast import playercorefactory
from localcast.playercorefactory import (
    DISABLED,
    ENABLED,
    FOREIGN,
    MARKER,
    PLAYERCOREFACTORY_XML,
    backup_path,
    is_ours,
    profile_xml_path,
    status_of,
)

HAND_WRITTEN = '''<?xml version="1.0" encoding="UTF-8"?>
<playercorefactory>
  <players>
    <player name="VLC" type="ExternalPlayer" audio="false" video="true">
      <filename>org.videolan.vlc</filename>
    </player>
  </players>
  <rules action="prepend">
    <rule video="true" player="VLC"/>
  </rules>
</playercorefactory>
'''


class IsOursTest(unittest.TestCase):

    def test_our_xml_is_ours(self):
        self.assertTrue(is_ours(PLAYERCOREFACTORY_XML))

    def test_empty_is_not_ours(self):
        self.assertFalse(is_ours(''))
        self.assertFalse(is_ours(None))

    def test_hand_written_is_not_ours(self):
        self.assertFalse(is_ours(HAND_WRITTEN))

    def test_marker_appears_verbatim_in_xml(self):
        self.assertIn(MARKER, PLAYERCOREFACTORY_XML)
        self.assertEqual(
            '<!-- Written by the LocalCast Kodi add-on (script.localcast). '
            'Delete this file to restore Kodi\'s own player. -->',
            MARKER)


class StatusOfTest(unittest.TestCase):

    def test_table(self):
        self.assertEqual(DISABLED, status_of(False, False))
        self.assertEqual(DISABLED, status_of(False, True))
        self.assertEqual(FOREIGN, status_of(True, False))
        self.assertEqual(ENABLED, status_of(True, True))

    def test_status_values(self):
        self.assertEqual('enabled', ENABLED)
        self.assertEqual('foreign', FOREIGN)
        self.assertEqual('disabled', DISABLED)


class ProfileXmlPathTest(unittest.TestCase):

    def test_with_trailing_slash(self):
        path = profile_xml_path(lambda special: '/data/user/0/org.xbmc.kodi/files/.kodi/userdata/')
        self.assertEqual('/data/user/0/org.xbmc.kodi/files/.kodi/userdata/playercorefactory.xml', path)

    def test_without_trailing_slash(self):
        path = profile_xml_path(lambda special: '/data/user/0/org.xbmc.kodi/files/.kodi/userdata')
        self.assertEqual('/data/user/0/org.xbmc.kodi/files/.kodi/userdata/playercorefactory.xml', path)

    def test_asks_for_the_profile_folder(self):
        seen = []

        def translate(special):
            seen.append(special)
            return '/p/'

        profile_xml_path(translate)
        self.assertEqual(['special://profile/'], seen)

    def test_backup_path(self):
        self.assertEqual('/p/playercorefactory.xml.localcast.bak',
                         backup_path('/p/playercorefactory.xml'))


class XmlContentTest(unittest.TestCase):

    def test_parses(self):
        root = ET.fromstring(PLAYERCOREFACTORY_XML.encode('utf-8'))
        self.assertEqual('playercorefactory', root.tag)

    def test_player_entry(self):
        root = ET.fromstring(PLAYERCOREFACTORY_XML.encode('utf-8'))
        players = root.findall('./players/player')
        self.assertEqual(1, len(players))
        player = players[0]
        self.assertEqual('LocalCast', player.get('name'))
        self.assertEqual('ExternalPlayer', player.get('type'))
        self.assertEqual('false', player.get('audio'))
        self.assertEqual('true', player.get('video'))
        self.assertEqual('de.stefanpledl.localcast', player.findtext('filename'))
        self.assertEqual('true', player.findtext('hidexbmc'))
        self.assertEqual('120', player.findtext('playcountminimumtime'))

    def test_rules(self):
        root = ET.fromstring(PLAYERCOREFACTORY_XML.encode('utf-8'))
        rules_el = root.find('./rules')
        self.assertEqual('prepend', rules_el.get('action'))
        rules = [dict(rule.attrib) for rule in rules_el.findall('rule')]
        self.assertEqual([
            {'protocols': 'smb', 'player': 'LocalCast'},
            {'dvdimage': 'true', 'player': 'LocalCast'},
            {'internetstream': 'true', 'player': 'LocalCast'},
            {'video': 'true', 'player': 'LocalCast'},
        ], rules)

    def test_no_rtmp_or_rtsp(self):
        lowered = PLAYERCOREFACTORY_XML.lower()
        self.assertNotIn('rtmp', lowered)
        self.assertNotIn('rtsp', lowered)

    def test_starts_with_xml_declaration_and_marker(self):
        lines = PLAYERCOREFACTORY_XML.splitlines()
        self.assertEqual('<?xml version="1.0" encoding="UTF-8"?>', lines[0])
        self.assertEqual(MARKER, lines[1])

    def test_file_name_constant(self):
        self.assertEqual('playercorefactory.xml', playercorefactory.FILE_NAME)


if __name__ == '__main__':
    unittest.main()
