# SkyLine OS

SkyLine is a cute, very customizable desktop operating system: **KDE Plasma 6** on top of **Debian 13**.
It boots with **Secure Boot on**, runs the official **Claude app**, and its sky follows your day:
peach at sunrise, blue at noon, lavender at dusk, starry at night.

This folder is the whole recipe. One command turns it into an ISO you can put on a USB stick.

## What's in SkyLine 1.0

| | |
|---|---|
| **Desktop** | KDE Plasma 6. Drag, resize and restyle anything: panels, widgets, window buttons, icons, fonts, animations. |
| **Dynamic sky** | Wallpaper and colors switch with the time of day. Pin one sky any time (`skyline-sky night`). |
| **Layouts** | One-click desktop layouts: **Classic** (bar at the bottom), **Dock** (top bar + app dock), **Minimal** (small floating bar). |
| **SkyLine Settings** | One window for sky, layout and apps. Everything else is in KDE System Settings. |
| **SkyLine Apps** | Tick boxes to install Claude, Discord, Steam, Roblox (Sober), Roblox Studio (Vinegar), Minecraft (Prism), Spotify, VS Code, OBS. |
| **Claude** | The official Claude desktop app (Linux beta) comes pre-installed. |
| **Look** | SkyLine boot splash, login screen, loading screen, installer, icon and 4 wallpapers. |
| **Installer** | Calamares, branded SkyLine. Can install next to Windows. |
| **Secure Boot** | Uses Debian's Microsoft-signed boot chain (shim + GRUB). No need to turn Secure Boot off. |

## Build it

The build has to run on **Debian 12 or 13**. Pick one way:

### A. On your Windows PC with WSL (easiest)

1. Open **PowerShell as administrator** and run:
   ```
   wsl --install -d Debian
   ```
   Restart if asked, then open **Debian** from the Start menu and choose a username and password.
2. In the Debian window, copy the kit into Linux (replace `YOU` with your Windows user name):
   ```
   sudo apt update && sudo apt install -y unzip
   cp /mnt/c/Users/YOU/Downloads/skyline-os.zip ~ && cd ~ && unzip skyline-os.zip && cd skyline-os
   ```
   Build inside your Linux home (`~`), not inside `/mnt/c`, or the build breaks.
3. Build:
   ```
   sudo ./build.sh
   ```
   It takes 30–90 minutes, downloads about 3 GB and needs about 20 GB free.
4. Copy the ISO to Windows:
   ```
   cp skyline-1.0-amd64.hybrid.iso /mnt/c/Users/YOU/Downloads/
   ```

### B. In a Debian virtual machine
Install Debian 13 in VirtualBox (40 GB disk), copy this folder in, and run `sudo ./build.sh`.

### C. On GitHub's servers
Push this folder to a **public** GitHub repository, open **Actions → Build SkyLine ISO → Run workflow**, and download the ISO from the finished run.

**Build options:** `--no-claude` leaves the Claude app out, `--clean` starts from scratch. If a build fails, open `build.log` and search for the first `E:` line.

## Try it safely first (virtual machine)

In **VirtualBox 7**: New VM → Linux / Debian (64-bit), 4 GB RAM, 2 CPUs, 30 GB disk.
Then **Settings → System → Enable EFI** and **Enable Secure Boot**, attach the ISO and start it.
You get the SkyLine live desktop. Nothing is installed until you click **Install SkyLine**.

## Install it on your PC (next to Windows)

1. **Back up** anything important. If your PC uses BitLocker, save your recovery key first.
2. In Windows **Disk Management**, right-click C: → **Shrink Volume** to free at least 60 GB.
3. Write the ISO to a USB stick (8 GB+) with **Rufus**. If Rufus asks, choose **DD Image mode**.
4. Restart and open the boot menu (usually **F12**, **F11**, **F8** or **Esc**) and pick the USB stick. Leave Secure Boot on.
5. Try SkyLine, then click **Install SkyLine** and choose **Install alongside**.

After that, a menu at start-up lets you pick SkyLine or Windows.

## Make it yours (for developers)

| Change | Where |
|---|---|
| Colors of every app and window | `tools/make-colors.py`, then run it |
| Wallpapers, icon, boot and installer art | `tools/make-assets.py`, then run it |
| Pre-installed programs | `config/package-lists/skyline.list.chroot` |
| Desktop layouts | `config/includes.chroot/usr/lib/skyline/layouts/*.js` |
| Apps offered in SkyLine Apps | `usr/bin/skyline-apps` and `usr/lib/skyline/install-apps` |
| Name and version | `config/hooks/normal/0500-skyline-branding.hook.chroot`, `auto/config`, installer `branding.desc` |
| When each sky starts | `sky_for_now` in `usr/bin/skyline-sky` |

Everything in `config/includes.chroot/` is copied into the system as-is, so `config/includes.chroot/usr/bin/x` becomes `/usr/bin/x`.

## Known limits in 1.0

- The start-up menu entry says **"Debian GNU/Linux"** on purpose. Debian's signed GRUB expects that name, and renaming it can break Secure Boot after an update. Fixing this safely is on the roadmap.
- The Claude app for Linux is a beta: no Computer Use and no voice dictation yet.
- Games with strict anti-cheat that block Linux won't run. Keep Windows for those.
- Roblox has no official Linux support. Sober and Vinegar are unofficial and can break when Roblox updates.

## Roadmap

- 1.1: SkyLine Settings as a real app (live previews instead of dialogs), accent color picker, more layouts.
- 1.2: SkyLine icon set and cursor, custom login screen, "SkyLine" in the start-up menu (tested with Secure Boot).
- Later: SkyLine app store page, automatic updates notifier, a mascot.
