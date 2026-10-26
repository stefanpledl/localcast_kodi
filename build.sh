#!/usr/bin/env bash
# Build the installable add-on zip into dist/.
# The zip's top-level folder must be script.localcast/ (Kodi requires it),
# so the archive is created from the repository root.
set -euo pipefail

cd "$(dirname "$0")"

ADDON_ID="script.localcast"
VERSION="$(sed -n 's/.*<addon[^>]*[[:space:]]version="\([^"]*\)".*/\1/p' "$ADDON_ID/addon.xml" | head -n 1)"
if [[ -z "$VERSION" ]]; then
  echo "could not read version from $ADDON_ID/addon.xml" >&2
  exit 1
fi

rm -rf dist
mkdir -p dist

VERSIONED="dist/$ADDON_ID-$VERSION.zip"
LATEST="dist/$ADDON_ID.zip"

zip -r -X "$VERSIONED" "$ADDON_ID" -x '*__pycache__*' '*.pyc' '*.DS_Store'
cp "$VERSIONED" "$LATEST"

echo
echo "Built:"
echo "  $PWD/$VERSIONED"
echo "  $PWD/$LATEST"
echo
echo "Top-level entries:"
unzip -l "$LATEST" | awk 'NR>3 && $4 != "" {print $4}' | cut -d/ -f1 | sort -u | sed 's/^/  /'
