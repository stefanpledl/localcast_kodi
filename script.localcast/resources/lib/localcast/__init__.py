"""LocalCast Kodi add-on.

``quoting``, ``android_activity`` and ``playercorefactory`` are pure Python
with no Kodi dependency so they can be unit-tested on any machine.
``kodi_api`` is the only module that imports the ``xbmc*`` packages, and
``actions`` ties the two sides together.
"""
