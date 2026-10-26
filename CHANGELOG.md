# Changelog

## 1.0.0 (2026-10-26)

- First release.
- Automatic casting: writes a `playercorefactory.xml` into the Kodi profile that
  routes every video (local files, SMB, disc images, internet streams) to the
  LocalCast app. A foreign `playercorefactory.xml` is backed up as
  `playercorefactory.xml.localcast.bak` and can be restored when automatic
  casting is turned off again.
- Context menu entry "Cast with LocalCast" on single items (Android only).
  Items served by Kodi add-ons (`plugin://`) explain that they need automatic
  mode instead.
- Settings page with Enable / Disable / Status / Help buttons; the same four
  actions are offered as a menu when the add-on is launched from Programs.
- Strings in English, German, French, Spanish, Italian and Brazilian
  Portuguese.
