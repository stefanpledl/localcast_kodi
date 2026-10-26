# LocalCast for Kodi (`script.localcast`)

A small Kodi add-on for **Android** that hands the videos Kodi plays to the
[LocalCast](https://localcast.app) app, which casts them to Chromecast, DLNA
and Smart TVs, Roku, Fire TV, AirPlay receivers and more.

It does two things:

1. **Automatic casting.** The add-on writes a `playercorefactory.xml` into
   your Kodi profile that registers LocalCast as an external player for every
   video. From then on, whatever Kodi would play - a file on the device, a
   share over SMB/NFS, a disc image, an internet stream, a stream resolved by
   a Kodi add-on - opens in LocalCast instead and is cast to the TV you pick.
2. **Context menu entry "Cast with LocalCast".** Long-press (or press the
   menu key on) a single video and send just that one item to LocalCast. This
   works for files, shares and direct URLs. Items that come from a Kodi
   add-on (`plugin://` paths) cannot be sent this way, because Kodi only
   resolves those streams while it plays them itself; the add-on tells you to
   use automatic mode for them.

Automatic casting is the recommended mode. Turning it on or off requires one
Kodi restart; the add-on offers to close Kodi for you.

## Requirements

- Kodi 19 (Matrix) or newer on Android - a phone, tablet, Android TV box or
  Fire TV running the Android build of Kodi.
- The [LocalCast app](https://play.google.com/store/apps/details?id=de.stefanpledl.localcast)
  installed on the same device.

Nothing in this add-on runs on other platforms; the context menu entry is
hidden there and the settings buttons only ever touch files inside your Kodi
profile folder.

## Install

1. Download `script.localcast.zip` from the
   [releases](https://github.com/stefanpledl/localcast_kodi/releases) (or
   build it yourself, see below) and put it where Kodi can see it - the
   device's Download folder is fine.
2. In Kodi: **Settings → System → Add-ons → Unknown sources** must be on.
3. **Settings → Add-ons → Install from zip file** → pick the zip.

## Usage

### Automatic casting

**Settings → Add-ons → My add-ons → Program add-ons → LocalCast → Configure →
Enable automatic casting**, then let the add-on close Kodi and start Kodi
again. Every video now opens in LocalCast. The dialog also shows up when you
launch LocalCast from the Programs section.

**Disable automatic casting** removes the file again (and offers to restore a
backup if the add-on replaced a `playercorefactory.xml` you had before).
**Status** shows which state you are in and where the file lives.

If you would rather do it by hand: the file is
`special://profile/playercorefactory.xml` (on Android usually
`/sdcard/Android/data/org.xbmc.kodi/files/.kodi/userdata/`). Deleting it
restores Kodi's own player. The file starts with a comment saying it was
written by this add-on; the add-on refuses to delete a `playercorefactory.xml`
it did not write.

### Context menu

Open the context menu on a single video and choose **Cast with LocalCast**.
The path is passed to LocalCast verbatim, including any `|User-Agent=...`
header suffix Kodi appends to stream URLs.

## How it works

`playercorefactory.xml` is Kodi's standard mechanism for external players. On
Android the `<filename>` of an `ExternalPlayer` is an application id, and
Kodi starts that app with an `ACTION_VIEW` intent carrying the media URL. The
file the add-on writes is:

```xml
<?xml version="1.0" encoding="UTF-8"?>
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
```

There are no `rtmp`/`rtsp` rules on purpose: LocalCast cannot play those
protocols, so Kodi keeps them.

The context menu entry uses the Kodi built-in
`StartAndroidActivity("de.stefanpledl.localcast","android.intent.action.VIEW","video/*","<path>")`.

## Development

```
script.localcast/
├── addon.xml, icon.png, LICENSE.txt
├── default.py              # RunScript entry: enable | disable | status | help | (menu)
├── context.py              # context menu entry
└── resources/
    ├── settings.xml        # four action buttons
    ├── language/…/strings.po
    └── lib/localcast/
        ├── quoting.py             # pure: quoting for Kodi built-in arguments
        ├── android_activity.py    # pure: StartAndroidActivity command, castable-path rules
        ├── playercorefactory.py   # pure: the XML, marker detection, status
        ├── kodi_api.py            # the only module importing xbmc*
        └── actions.py             # orchestration
```

The three pure modules never import `xbmc*`, so they are unit-tested without
Kodi:

```sh
python3 -m unittest discover -s tests -v
```

Byte-compile check:

```sh
find script.localcast -name '*.py' -exec python3 -m py_compile {} +
```

Build the zip (writes `dist/script.localcast-<version>.zip` and
`dist/script.localcast.zip`, top-level folder `script.localcast/`):

```sh
./build.sh
```

Run the official add-on checker (install with
`pip3 install --user kodi-addon-checker`):

```sh
kodi-addon-checker --branch omega script.localcast
```

## Submitting to the official Kodi repository

- Pull requests go to <https://github.com/xbmc/repo-scripts>, branch of the
  oldest Kodi version the add-on supports (`matrix`, `nexus`, `omega`, ...).
  The PR adds the folder `script.localcast/` with exactly the files from this
  repository's `script.localcast/` (no `dist/`, no tests).
- The checker must pass with `--PR`; a warning about the `source`/`forum`
  URLs is expected until those pages exist.
- `addon.xml`'s `<news>` and `CHANGELOG.md` must describe the release; bump
  the version in `addon.xml` for every PR.
- Kodi's reviewers expect `LICENSE.txt` inside the add-on folder, a 512x512
  `icon.png`, PO-format strings and `<platform>android</platform>` since the
  context item and the external player only make sense there.

## License

GPL-3.0-only. See [LICENSE](LICENSE).
