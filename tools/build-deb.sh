#!/usr/bin/env bash
# Build dist/skyline-desktop_<version>_all.deb (and its .sha256) from package/skyline-desktop.
# Needs only dpkg-deb, so it runs on Debian, Ubuntu or GitHub's runners.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

version=$(sed -n 's/^Version: //p' package/debian/control)
name="skyline-desktop_${version}_all.deb"
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT

cp -a package/skyline-desktop/. "$stage/"
find "$stage" -name '__pycache__' -prune -exec rm -rf {} +
# Windows can add CRLF line endings to scripts; strip them.
{ grep -rlI $'\r' "$stage" || true; } | xargs -r sed -i 's/\r$//'

find "$stage" -type d -exec chmod 0755 {} +
find "$stage" -type f -exec chmod 0644 {} +
chmod 0755 "$stage"/usr/bin/* \
	"$stage"/usr/lib/skyline/install-apps "$stage"/usr/lib/skyline/install-claude \
	"$stage"/usr/lib/skyline/install-nvidia "$stage"/usr/lib/skyline/ensure-nonfree \
	"$stage"/usr/lib/skyline/dnd-hold "$stage"/usr/lib/skyline/sync-breeze-copies

mkdir -p "$stage/DEBIAN"
cp package/debian/control "$stage/DEBIAN/control"
echo "Installed-Size: $(du -sk "$stage" | cut -f1)" >>"$stage/DEBIAN/control"
install -m 0755 package/debian/postinst "$stage/DEBIAN/postinst"
install -m 0755 package/debian/prerm "$stage/DEBIAN/prerm"
install -m 0755 package/debian/preinst "$stage/DEBIAN/preinst"
install -m 0755 package/debian/postrm "$stage/DEBIAN/postrm"
install -m 0644 package/debian/triggers "$stage/DEBIAN/triggers"

mkdir -p dist
dpkg-deb --root-owner-group -Zxz --build "$stage" "dist/$name" >/dev/null
(cd dist && sha256sum "$name" >"$name.sha256")
echo "dist/$name"
