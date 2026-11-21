## SkyLine 1.2

**SkyLine Shell, part 1: SkyLine's own desktop begins.**
- **Cloud Menu:** SkyLine's own start menu. Puff greets you, then search (apps and files, or ask Puff), pinned apps, all apps, the sky buttons, and lock, sleep, restart, power off. Opens with the Meta/Windows key too.
- **Puff in the taskbar:** an animated pixel Puff button. Click it to chat.
- **New layout "SkyLine Shell":** a thin top bar with the clock and system icons, and a floating dock with the Cloud Menu, your apps and Puff. Pick it in SkyLine Settings > Layout, or ask Puff for "skyline shell".
- "Ask Puff" in the Cloud Menu opens Puff with your question already sent.

## SkyLine 1.1.2

- Your own wallpaper stays: if you pick a wallpaper in KDE, SkyLine only changes the colors. Choosing a sky in SkyLine Settings (or asking Puff) brings the SkyLine wallpaper back.
- New: Settings > Sky > "Keep my own wallpaper", and Puff understands "keep my wallpaper".

## SkyLine 1.1.1

- Fix: installing on a PC with Debian's desktop-base package (every SkyLine 1.0 install) stopped with "trying to overwrite /etc/xdg/kcm-about-distrorc".

## SkyLine 1.1

**New**
- **Puff, the SkyLine Assistant:** a pixel cloud that changes your sky, layout, taskbar and Game Mode, and installs or opens apps when you ask (English and Italian). Add a Claude or Groq key to chat about anything.
- **SkyLine Settings app:** sky, weather, layout, taskbar, accent color, icons, sounds, apps, gaming, Assistant and updates in one window.
- **Taskbar styles:** follows the sky, black, white, glass (see-through) or clear (invisible).
- **Weather sky:** the wallpaper shows real rain, snow and clouds for your city (Open-Meteo, no account needed).
- **Game Mode:** maximum performance and muted notifications; `skyline-play` runs games on the NVIDIA card.
- **SkyLine look:** pastel folder icons, soft sounds, and a lock screen that follows the sky.
- **Updater:** a daily check with an "Update now" notification.

**Fixes**
- One-click NVIDIA driver (SkyLine Apps or Settings > Gaming): handles non-free sources, the Secure Boot key and external monitors.

**Install on SkyLine 1.0**
```
curl -LO https://github.com/Gray7689/skyline-os/releases/download/v1.2.0/skyline-desktop_1.2.0_all.deb
sudo apt install ./skyline-desktop_1.2.0_all.deb
```
Then log out and back in.
