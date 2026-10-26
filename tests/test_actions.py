"""Drive actions.py through fake xbmc* modules (see fake_kodi.py)."""

import sys
import types
import unittest

from tests import _path  # noqa: F401  (adds resources/lib to sys.path)
from tests import fake_kodi

LOCALES = ('en_gb', 'de_de', 'fr_fr', 'es_es', 'it_it', 'pt_br')


class ActionsTestCase(unittest.TestCase):

    def setUp(self):
        self.kodi = fake_kodi.install()
        from localcast import actions, kodi_api, playercorefactory  # noqa: E402
        self.actions = actions
        self.kodi_api = kodi_api
        self.pcf = playercorefactory
        self.xml_path = self.kodi.xml_path()
        self.backup = self.kodi.backup_path()

    def tearDown(self):
        fake_kodi.forget()
        if hasattr(sys, 'listitem'):
            del sys.listitem

    # -- helpers ------------------------------------------------------------

    def put_file(self, path, text):
        self.kodi.files[path] = text.encode('utf-8')

    def file_text(self, path):
        return self.kodi.files[path].decode('utf-8')

    def string(self, string_id):
        return self.kodi.strings[string_id]


class EnableTest(ActionsTestCase):

    def test_fresh_profile_writes_file_and_offers_quit(self):
        self.kodi.answer_yesno(True)
        self.actions.enable_automatic_casting()
        self.assertEqual(self.pcf.PLAYERCOREFACTORY_XML, self.file_text(self.xml_path))
        self.assertNotIn(self.backup, self.kodi.files)
        self.assertEqual([self.string(32032)], self.kodi.yesno_questions)
        self.assertEqual(['Quit'], self.kodi.builtins)

    def test_declining_quit_shows_restart_notification(self):
        self.kodi.answer_yesno(False)
        self.actions.enable_automatic_casting()
        self.assertEqual([], self.kodi.builtins)
        self.assertEqual([self.string(32033)], self.kodi.notifications)

    def test_our_own_file_is_rewritten_without_backup_prompt(self):
        self.put_file(self.xml_path, self.pcf.PLAYERCOREFACTORY_XML)
        self.kodi.answer_yesno(False)
        self.actions.enable_automatic_casting()
        self.assertEqual([self.string(32032)], self.kodi.yesno_questions)
        self.assertNotIn(self.backup, self.kodi.files)

    def test_foreign_file_declined_is_left_alone(self):
        self.put_file(self.xml_path, '<playercorefactory/>')
        self.kodi.answer_yesno(False)
        self.actions.enable_automatic_casting()
        self.assertEqual([self.string(32031)], self.kodi.yesno_questions)
        self.assertEqual('<playercorefactory/>', self.file_text(self.xml_path))
        self.assertNotIn(self.backup, self.kodi.files)
        self.assertEqual([], self.kodi.builtins)

    def test_foreign_file_accepted_is_backed_up_and_replaced(self):
        self.put_file(self.xml_path, '<playercorefactory/>')
        self.kodi.answer_yesno(True, False)
        self.actions.enable_automatic_casting()
        self.assertEqual('<playercorefactory/>', self.file_text(self.backup))
        self.assertEqual(self.pcf.PLAYERCOREFACTORY_XML, self.file_text(self.xml_path))
        self.assertEqual([self.string(32031), self.string(32032)], self.kodi.yesno_questions)

    def test_failed_backup_raises_and_does_not_overwrite(self):
        self.put_file(self.xml_path, '<playercorefactory/>')
        self.kodi.copy_fails = True
        self.kodi.answer_yesno(True)
        with self.assertRaises(IOError):
            self.actions.enable_automatic_casting()
        self.assertEqual('<playercorefactory/>', self.file_text(self.xml_path))


class DisableTest(ActionsTestCase):

    def test_nothing_to_disable(self):
        self.actions.disable_automatic_casting()
        self.assertEqual([self.string(32034)], self.kodi.notifications)
        self.assertEqual([], self.kodi.yesno_questions)

    def test_foreign_file_is_not_deleted(self):
        self.put_file(self.xml_path, '<playercorefactory/>')
        self.actions.disable_automatic_casting()
        self.assertEqual([self.string(32035)], self.kodi.ok_dialogs)
        self.assertIn(self.xml_path, self.kodi.files)

    def test_our_file_is_deleted_and_restart_offered(self):
        self.put_file(self.xml_path, self.pcf.PLAYERCOREFACTORY_XML)
        self.kodi.answer_yesno(True)
        self.actions.disable_automatic_casting()
        self.assertNotIn(self.xml_path, self.kodi.files)
        self.assertEqual([self.string(32032)], self.kodi.yesno_questions)
        self.assertEqual(['Quit'], self.kodi.builtins)

    def test_backup_is_restored_on_request(self):
        self.put_file(self.xml_path, self.pcf.PLAYERCOREFACTORY_XML)
        self.put_file(self.backup, '<playercorefactory/>')
        self.kodi.answer_yesno(True, False)
        self.actions.disable_automatic_casting()
        self.assertEqual('<playercorefactory/>', self.file_text(self.xml_path))
        self.assertNotIn(self.backup, self.kodi.files)
        self.assertEqual([self.string(32036), self.string(32032)], self.kodi.yesno_questions)
        self.assertIn(self.string(32047), self.kodi.notifications)

    def test_backup_is_kept_when_restore_declined(self):
        self.put_file(self.xml_path, self.pcf.PLAYERCOREFACTORY_XML)
        self.put_file(self.backup, '<playercorefactory/>')
        self.kodi.answer_yesno(False, False)
        self.actions.disable_automatic_casting()
        self.assertNotIn(self.xml_path, self.kodi.files)
        self.assertIn(self.backup, self.kodi.files)


class StatusAndHelpTest(ActionsTestCase):

    def test_status_disabled(self):
        self.actions.show_status()
        self.assertEqual(1, len(self.kodi.ok_dialogs))
        self.assertTrue(self.kodi.ok_dialogs[0].startswith(self.string(32038)))
        self.assertIn(self.xml_path, self.kodi.ok_dialogs[0])

    def test_status_enabled(self):
        self.put_file(self.xml_path, self.pcf.PLAYERCOREFACTORY_XML)
        self.actions.show_status()
        self.assertTrue(self.kodi.ok_dialogs[0].startswith(self.string(32037)))

    def test_status_foreign(self):
        self.put_file(self.xml_path, '<playercorefactory/>')
        self.actions.show_status()
        self.assertTrue(self.kodi.ok_dialogs[0].startswith(self.string(32039)))

    def test_help(self):
        self.actions.show_help()
        self.assertEqual([self.string(32041)], self.kodi.ok_dialogs)
        self.assertIn('localcast.app/kodi', self.kodi.ok_dialogs[0])


class MainMenuTest(ActionsTestCase):

    def test_menu_lists_four_actions(self):
        self.actions.show_main_menu()
        self.assertEqual([[self.string(32013), self.string(32015),
                           self.string(32017), self.string(32019)]],
                         self.kodi.select_options)

    def test_cancel_does_nothing(self):
        self.actions.show_main_menu()
        self.assertEqual([], self.kodi.ok_dialogs)
        self.assertEqual([], self.kodi.yesno_questions)

    def test_choosing_status_shows_status(self):
        self.kodi.choose(2)
        self.actions.show_main_menu()
        self.assertEqual(1, len(self.kodi.ok_dialogs))

    def test_run_dispatches_named_actions(self):
        self.actions.run(['default.py', 'help'])
        self.assertEqual([self.string(32041)], self.kodi.ok_dialogs)

    def test_run_without_argument_shows_menu(self):
        self.actions.run(['default.py'])
        self.assertEqual(1, len(self.kodi.select_options))

    def test_run_with_unknown_argument_shows_menu(self):
        self.actions.run(['default.py', 'bogus'])
        self.assertEqual(1, len(self.kodi.select_options))


class CastListItemTest(ActionsTestCase):

    def test_not_android(self):
        self.kodi.android = False
        self.actions.cast_listitem()
        self.assertEqual([self.string(32042)], self.kodi.notifications)
        self.assertEqual([], self.kodi.builtins)

    def test_nothing_focused(self):
        self.actions.cast_listitem()
        self.assertEqual([self.string(32043)], self.kodi.notifications)
        self.assertEqual([], self.kodi.builtins)

    def test_plugin_item_explains_automatic_mode(self):
        sys.listitem = types.SimpleNamespace(getPath=lambda: 'plugin://plugin.video.x/play/1')
        self.actions.cast_listitem()
        self.assertEqual([self.string(32044)], self.kodi.ok_dialogs)
        self.assertEqual([], self.kodi.builtins)

    def test_videodb_item_explains_automatic_mode(self):
        self.kodi.infolabels['ListItem.FileNameAndPath'] = 'videodb://movies/titles/1'
        self.actions.cast_listitem()
        self.assertEqual([self.string(32044)], self.kodi.ok_dialogs)

    def test_smb_item_from_sys_listitem_is_sent(self):
        sys.listitem = types.SimpleNamespace(getPath=lambda: 'smb://nas/share/a.mkv')
        self.actions.cast_listitem()
        self.assertEqual(
            ['StartAndroidActivity("de.stefanpledl.localcast",'
             '"android.intent.action.VIEW","video/*","smb://nas/share/a.mkv")'],
            self.kodi.builtins)
        self.assertEqual([self.string(32045)], self.kodi.notifications)
        self.assertTrue(any('smb://nas/share/a.mkv' in line for line in self.kodi.log_lines))

    def test_infolabel_fallback_with_user_agent_suffix(self):
        path = 'http://h/x.m3u8|User-Agent=Mozilla/5.0 (X11; Linux)'
        self.kodi.infolabels['ListItem.FileNameAndPath'] = path
        self.actions.cast_listitem()
        self.assertEqual(1, len(self.kodi.builtins))
        self.assertTrue(self.kodi.builtins[0].endswith(',"' + path + '")'))

    def test_broken_listitem_falls_back_to_infolabel(self):
        def boom():
            raise RuntimeError('no path')
        sys.listitem = types.SimpleNamespace(getPath=boom)
        self.kodi.infolabels['ListItem.FileNameAndPath'] = '/storage/emulated/0/Movies/a.mkv'
        self.actions.cast_listitem()
        self.assertEqual(1, len(self.kodi.builtins))
        self.assertIn('/storage/emulated/0/Movies/a.mkv', self.kodi.builtins[0])


class ReportErrorTest(ActionsTestCase):

    def test_logs_traceback_and_shows_error_class(self):
        self.actions.report_error(ValueError('x'), 'Traceback: fake')
        self.assertTrue(any('Traceback: fake' in line for line in self.kodi.log_lines))
        self.assertEqual([self.string(32046) % 'ValueError'], self.kodi.ok_dialogs)

    def test_log_prefix(self):
        self.kodi_api.log('hello')
        self.assertEqual(['[script.localcast] hello'], self.kodi.log_lines)


class StringsPoTest(unittest.TestCase):

    def test_every_action_string_id_exists_in_every_locale(self):
        fake_kodi.install()
        try:
            from localcast import actions  # noqa: E402
            used = {value for name, value in vars(actions).items()
                    if name.startswith('STR_') and isinstance(value, int)}
        finally:
            fake_kodi.forget()
        self.assertIn(32001, used)
        for locale in LOCALES:
            ids = set(fake_kodi.load_po(locale))
            self.assertTrue(used <= ids, '%s lacks %s' % (locale, sorted(used - ids)))

    def test_settings_and_context_ids_exist(self):
        for locale in LOCALES:
            ids = set(fake_kodi.load_po(locale))
            for needed in (32001,) + tuple(range(32010, 32021)):
                self.assertIn(needed, ids, '%s lacks %d' % (locale, needed))

    def test_all_locales_share_the_same_ids_and_msgids(self):
        english = fake_kodi.load_po('en_gb')
        for locale in LOCALES[1:]:
            other = fake_kodi.load_po(locale)
            self.assertEqual(set(english), set(other), locale)
            for num, (msgid, msgstr) in other.items():
                self.assertEqual(english[num][0], msgid, '%s #%d msgid differs' % (locale, num))
                self.assertTrue(msgstr, '%s #%d has no translation' % (locale, num))
                self.assertEqual(msgid.count('%s'), msgstr.count('%s'),
                                 '%s #%d placeholder mismatch' % (locale, num))

    def test_english_msgstrs_are_empty(self):
        for num, (_, msgstr) in fake_kodi.load_po('en_gb').items():
            self.assertEqual('', msgstr, '#%d' % num)


if __name__ == '__main__':
    unittest.main()
