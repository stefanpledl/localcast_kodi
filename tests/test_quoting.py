import unittest

from tests import _path  # noqa: F401  (adds resources/lib to sys.path)

from localcast.quoting import quote_builtin_arg


def kodi_unquote(quoted):
    """Undo Kodi's built-in argument quoting the way CBuiltins splits it.

    Strips the surrounding double quotes and resolves ``\\x`` escapes.
    """
    assert quoted.startswith('"') and quoted.endswith('"'), quoted
    body = quoted[1:-1]
    out = []
    i = 0
    while i < len(body):
        char = body[i]
        if char == '\\' and i + 1 < len(body):
            out.append(body[i + 1])
            i += 2
        else:
            out.append(char)
            i += 1
    return ''.join(out)


class QuoteBuiltinArgTest(unittest.TestCase):

    def test_plain_value_is_wrapped_in_double_quotes(self):
        self.assertEqual('"smb://nas/share/a.mkv"', quote_builtin_arg('smb://nas/share/a.mkv'))

    def test_double_quote_round_trips(self):
        value = 'http://h/say "hi".mp4'
        quoted = quote_builtin_arg(value)
        self.assertEqual('"http://h/say \\"hi\\".mp4"', quoted)
        self.assertEqual(value, kodi_unquote(quoted))

    def test_backslash_round_trips(self):
        value = 'smb://nas/share\\sub\\a.mkv'
        quoted = quote_builtin_arg(value)
        self.assertEqual('"smb://nas/share\\\\sub\\\\a.mkv"', quoted)
        self.assertEqual(value, kodi_unquote(quoted))

    def test_backslash_before_quote_round_trips(self):
        value = 'a\\"b'
        self.assertEqual(value, kodi_unquote(quote_builtin_arg(value)))

    def test_user_agent_suffix_is_left_intact(self):
        value = 'http://h/x.m3u8|User-Agent=Mozilla/5.0 (X11; Linux)'
        quoted = quote_builtin_arg(value)
        self.assertEqual('"' + value + '"', quoted)
        self.assertIn('|User-Agent=Mozilla/5.0 (X11; Linux)', quoted)
        self.assertEqual(value, kodi_unquote(quoted))

    def test_commas_are_not_escaped_only_quoted(self):
        quoted = quote_builtin_arg('a,b')
        self.assertEqual('"a,b"', quoted)

    def test_none_and_empty_become_empty_quoted_string(self):
        self.assertEqual('""', quote_builtin_arg(''))
        self.assertEqual('""', quote_builtin_arg(None))


if __name__ == '__main__':
    unittest.main()
