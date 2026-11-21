#!/usr/bin/env bash
# Build the SkyLine ISO.
#
#   sudo ./build.sh               build skyline-1.0-amd64.hybrid.iso
#   sudo ./build.sh --no-claude   build without the Claude app pre-installed
#   sudo ./build.sh --clean       throw away the previous build and start fresh
#
# Run it on Debian 12 or 13: Debian on WSL2, a Debian virtual machine, or a Debian container.
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

WITH_CLAUDE=1
CLEAN=0
for arg in "$@"; do
	case $arg in
		--no-claude) WITH_CLAUDE=0 ;;
		--clean) CLEAN=1 ;;
		-h | --help)
			sed -n '2,8s/^# \{0,1\}//p' "$0"
			exit 0
			;;
		*)
			echo "Unknown option: $arg (try --help)" >&2
			exit 2
			;;
	esac
done

say() { printf '\n\033[1;35mSkyLine:\033[0m %s\n' "$*"; }
die() {
	printf '\n\033[1;31mSkyLine build stopped:\033[0m %s\n' "$*" >&2
	exit 1
}

if [[ $EUID -ne 0 ]]; then
	exec sudo bash "$0" "$@"
fi

# shellcheck disable=SC1091
. /etc/os-release
[[ ${ID:-} == debian ]] || die "run this on Debian 12 or 13 (this is ${PRETTY_NAME:-an unknown system}). See README, 'Build it'."

case $PWD in
	/mnt/*) die "you're inside a Windows folder ($PWD). Copy the kit to your Linux home first:  cp -r \"$PWD\" ~/ && cd ~/$(basename "$PWD")" ;;
esac

free_gb=$(df -Pk . | awk 'NR==2 {print int($4/1024/1024)}')
((free_gb >= 20)) || die "the build needs about 20 GB of free space here; found ${free_gb} GB."

say "installing the build tools"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
	live-build debootstrap squashfs-tools xorriso mtools dosfstools curl ca-certificates dpkg-dev >/dev/null

say "checking files"
# Windows can strip the "executable" flag and add CRLF line endings. Fix both.
if grep -rlI $'\r' auto config hooks-optional package tools >/dev/null 2>&1; then
	grep -rlI $'\r' auto config hooks-optional package tools | xargs sed -i 's/\r$//'
	say "converted Windows line endings"
fi
chmod 0755 auto/* config/hooks/normal/*.hook.chroot hooks-optional/*.hook.chroot tools/*.sh

say "packaging SkyLine (skyline-desktop)"
rm -rf config/packages.chroot
mkdir -p config/packages.chroot
cp "$(bash tools/build-deb.sh)" config/packages.chroot/

rm -f config/hooks/normal/0520-skyline-claude.hook.chroot
if ((WITH_CLAUDE)); then
	cp hooks-optional/0520-skyline-claude.hook.chroot config/hooks/normal/
	say "the Claude app will be pre-installed"
else
	say "building without the Claude app (SkyLine Apps can add it later)"
fi

say "branding the USB boot menu"
rm -rf config/bootloaders
mkdir -p config/bootloaders
for d in grub-pc isolinux syslinux_common; do
	if [[ -d /usr/share/live/build/bootloaders/$d ]]; then
		cp -r "/usr/share/live/build/bootloaders/$d" config/bootloaders/
	fi
done
{ grep -rlI 'Live system' config/bootloaders || true; } | xargs -r sed -i 's/Live system/SkyLine/g'
while IFS= read -r -d '' png; do
	cp assets/boot-splash.png "$png"
	rm -f "$(dirname "$png")/splash.svg" "$(dirname "$png")/splash.svg.in"
done < <(find config/bootloaders -name splash.png -print0)

if ((CLEAN)); then
	say "cleaning the previous build"
	lb clean --purge
fi

say "building SkyLine. This takes 30-90 minutes and downloads about 3 GB. Grab a snack."
lb config
lb build

iso=$(find . -maxdepth 1 -name "*.iso" -print -quit)
[[ -n $iso ]] || die "no ISO was made. Look at build.log for the first error (search for 'E:' or 'error')."
sha256sum "$iso" >"$iso.sha256"
say "done! $(du -h "$iso" | cut -f1)  $iso"
echo "Checksum saved in $iso.sha256"
echo "Next: try it in a virtual machine, then put it on a USB stick (see README)."
