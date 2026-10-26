import unittest

from tests import _path  # noqa: F401  (adds resources/lib to sys.path)

from localcast import android_activity
from localcast.android_activity import (
    PACKAGE,
    is_castable_path,
    is_plugin_path,
    start_android_activity_command,
)


class PackageTest(unittest.TestCase):

    def test_package_is_the_play_store_id(self):
        self.assertEqual('de.stefanpledl.localcast', PACKAGE)


class IsPluginPathTest(unittest.TestCase):

    def test_plugin_paths(self):
        self.assertTrue(is_plugin_path('plugin://plugin.video.youtube/play/?video_id=x'))

    def test_other_paths_are_not_plugin_paths(self):
        self.assertFalse(is_plugin_path('smb://nas/share/a.mkv'))
        self.assertFalse(is_plugin_path('/storage/emulated/0/Movies/a.mkv'))
        self.assertFalse(is_plugin_path(''))
        self.assertFalse(is_plugin_path(None))


class IsCastablePathTest(unittest.TestCase):

    def test_not_castable(self):
        for path in (
                '',
                None,
                'plugin://plugin.video.youtube/play/?video_id=x',
                'videodb://movies/titles/12',
                'musicdb://songs/1',
                'library://video/movies/titles.xml',
                'pvr://channels/tv/All/1.pvr',
                'special://profile/playlists/video/a.m3u',
                'addons://sources/video/',
                'sources://video/',
                'VIDEODB://movies/titles/12',
        ):
            self.assertFalse(is_castable_path(path), path)

    def test_castable(self):
        for path in (
                '/storage/emulated/0/Movies/a.mkv',
                'smb://nas/share/a.mkv',
                'nfs://nas/export/a.mkv',
                'http://h/x.m3u8|User-Agent=Foo',
                'https://h/x.mp4',
                'file:///sdcard/Movies/a.mp4',
        ):
            self.assertTrue(is_castable_path(path), path)


class StartAndroidActivityCommandTest(unittest.TestCase):

    def test_exact_command_for_simple_smb_path(self):
        self.assertEqual(
            'StartAndroidActivity("de.stefanpledl.localcast",'
            '"android.intent.action.VIEW","video/*","smb://nas/share/a.mkv")',
            start_android_activity_command('smb://nas/share/a.mkv'))

    def test_user_agent_suffix_is_passed_verbatim(self):
        path = 'http://h/x.m3u8|User-Agent=Mozilla/5.0 (X11; Linux)&Referer=http://h/'
        command = start_android_activity_command(path)
        self.assertTrue(command.endswith(',"' + path + '")'), command)

    def test_quotes_in_path_are_escaped(self):
        command = start_android_activity_command('/a/b "c".mkv')
        self.assertTrue(command.endswith(',"/a/b \\"c\\".mkv")'), command)

    def test_constants(self):
        self.assertEqual('android.intent.action.VIEW', android_activity.ACTION)
        self.assertEqual('video/*', android_activity.MIME_TYPE)


if __name__ == '__main__':
    unittest.main()
