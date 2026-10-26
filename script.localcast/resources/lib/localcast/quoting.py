"""Quoting of arguments for Kodi built-in functions.

Kodi splits a built-in call such as ``StartAndroidActivity(a,b,c,d)`` on
commas unless the argument is wrapped in double quotes.  Inside the quotes a
backslash escapes the next character, so backslashes and double quotes in the
value itself have to be escaped.
"""


def quote_builtin_arg(value):
    """Return *value* wrapped in double quotes, safe for a Kodi built-in call.

    Backslashes and double quotes inside *value* are escaped with a backslash.
    Everything else - commas, spaces, ``|User-Agent=...`` header suffixes - is
    passed through untouched.
    """
    if value is None:
        value = ''
    escaped = str(value).replace('\\', '\\\\').replace('"', '\\"')
    return '"' + escaped + '"'
