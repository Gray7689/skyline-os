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
curl -LO https://github.com/Gray7689/skyline-os/releases/download/v1.1.1/skyline-desktop_1.1.1_all.deb
sudo apt install ./skyline-desktop_1.1.1_all.deb
```
Then log out and back in.
