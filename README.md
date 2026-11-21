# SkyLine OS

SkyLine is a cute, very customizable desktop operating system: **KDE Plasma 6** on top of **Debian 13**.
It boots with **Secure Boot on**, runs the official **Claude app**, and its sky follows your day:
peach at sunrise, blue at noon, lavender at dusk, starry at night.

This folder is the whole recipe. One command turns it into an ISO you can put on a USB stick.

## What's in SkyLine 1.3

| | |
|---|---|
| **Desktop** | KDE Plasma 6. Drag, resize and restyle anything: panels, widgets, window buttons, icons, fonts, animations. |
| **Dynamic sky** | Wallpaper, colors and lock screen follow the time of day, and the **real weather** (rain, snow, clouds) if you set your city. |
| **Taskbar styles** | Follows the sky, **black**, **white**, **glass** (see-through) or **clear** (invisible). |
| **SkyLine Shell** | SkyLine's own desktop: the **Cloud Menu** (start menu with Puff, search, pinned apps, sky and power buttons), the **SkyLine Dock**, **Puff in the dock**, the **sky pill** in the top bar (temperature and quick switches), **round-button window style** that follows the sky, and SkyLine's **lock and login screens**. |
| **Italiano** | All of SkyLine speaks Italian (Settings, Puff, widgets, dialogs). It follows KDE's language. Translations: `package/skyline-desktop/usr/share/skyline/l10n/it.json`. |
| **SkyLine Setup** | First-start setup for new users: language, Wi-Fi, sky, layout and windows, apps, Puff's AI. |
| **Layouts** | One click: **Classic** (bar at the bottom), **Dock** (top bar + app dock), **Minimal** (small floating bar), **SkyLine Shell** (top bar + dock with the Cloud Menu and Puff). |
| **Puff, the Assistant** | A pixel cloud you chat with. Changes your sky, layout, taskbar, Game Mode and apps. Works offline for simple requests (English and Italian); connect **Claude, OpenAI, NVIDIA, Groq, Gemini, OpenRouter, Ollama** or any OpenAI-compatible server to talk about anything. |
| **SkyLine Settings** | One app for sky, weather, layout, taskbar, accent color, icons, sounds, apps, gaming, Puff and updates. |
| **Game Mode** | Maximum performance and muted notifications. `skyline-play` runs games on the NVIDIA card. |
| **SkyLine Apps** | Tick boxes to install Claude, Discord, Steam, Roblox (Sober), Roblox Studio (Vinegar), Minecraft (Prism), Spotify, VS Code, OBS and the NVIDIA driver. |
| **NVIDIA** | One-click driver: turns on non-free sources, registers the Secure Boot key and enables external monitors. |
| **Updates** | SkyLine checks GitHub once a day and offers "Update now". Discover updates Debian and your apps. |
| **Look** | 16 wallpapers (4 times of day x clear, cloudy, rain, snow), pastel folder icons, soft sounds, boot splash, login and installer. |
| **Claude** | The official Claude desktop app (Linux beta) comes pre-installed. |
| **Secure Boot** | Uses Debian's Microsoft-signed boot chain (shim + GRUB). No need to turn Secure Boot off. |

## Already on SkyLine 1.0? Update in two commands

(On 1.1 or newer, just run `skyline-update install`.)

```
curl -LO https://github.com/Gray7689/skyline-os/releases/download/v1.3.0/skyline-desktop_1.3.0_all.deb
sudo apt install ./skyline-desktop_1.3.0_all.deb
```
Log out and back in. From now on SkyLine tells you when a new version is out.

## How the repository is organized

| Folder | What it is |
|---|---|
| `package/skyline-desktop/` | Every SkyLine file, laid out as it lands on the system (`usr/bin/skyline-sky` becomes `/usr/bin/skyline-sky`). Built into the **skyline-desktop** package. |
| `package/debian/` | Package details (version, dependencies) and its install script. Bump `Version:` for a new release. |
| `config/`, `auto/` | The live-build recipe for the ISO. The ISO installs the skyline-desktop package. |
| `tools/` | `make-assets.py` (all artwork), `make-colors.py` (color schemes), `build-deb.sh` (the package). |
| `.github/workflows/` | `build-iso.yml` builds the ISO on demand; `release.yml` tests and publishes the package whenever its version changes. |

**To release a new version:** change `Version:` in `package/debian/control` and the notes in `package/RELEASE_NOTES.md`, then commit and push to `main`. GitHub tests it on Debian 13 and publishes the release.

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
   cp skyline-1.1-amd64.hybrid.iso /mnt/c/Users/YOU/Downloads/
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
| Wallpapers, weather skies, icons, sounds, boot and installer art | `tools/make-assets.py`, then run it |
| Pre-installed programs | `config/package-lists/skyline.list.chroot` |
| Desktop layouts | `package/skyline-desktop/usr/lib/skyline/layouts/*.js` |
| SkyLine Shell widgets (Cloud Menu, Dock, sky pill, Puff) | `package/skyline-desktop/usr/share/plasma/plasmoids/org.skyline.*/` (QML) |
| Window style (title bars) | `tools/make-windows.py` writes `usr/share/aurorae/themes/SkyLine-*` |
| Translations | `usr/share/skyline/l10n/<lang>.json`; check with `python3 tools/l10n.py check`, widget files with `python3 tools/l10n.py mo` |
| Puff's offline commands | `local_brain` in `package/skyline-desktop/usr/bin/skyline-assistant` |
| AI services Puff can use | `PROVIDERS` in `package/skyline-desktop/usr/lib/skyline/skyline_ai.py` |
| When each sky starts | `sky_for_now` in `package/skyline-desktop/usr/bin/skyline-sky` |

## Known limits

- The start-up menu entry says **"Debian GNU/Linux"** on purpose. Debian's signed GRUB expects that name, and renaming it can break Secure Boot after an update. Fixing this safely is on the roadmap.
- The Claude app for Linux is a beta: no Computer Use and no voice dictation yet.
- Games with strict anti-cheat that block Linux won't run. Keep Windows for those.
- Roblox has no official Linux support. Sober and Vinegar are unofficial and can break when Roblox updates.

## Roadmap

- 1.2: "SkyLine" in the start-up menu (tested with Secure Boot), custom cursors, more layouts.
- Later: Puff on the lock screen, a SkyLine app store page, more weather (fog, storms).
