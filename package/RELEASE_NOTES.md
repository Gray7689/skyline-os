## SkyLine 1.3.2

- After an update, the update screen asks to **restart the computer** ("Restart now" / "Later") instead of logging out, so every part of SkyLine (boot screen, login, drivers) is fresh.

## SkyLine 1.3.1

- **New update screen:** "Update now" (notification, SkyLine Settings, the sky pill, or asking Puff) opens a full-screen "Updating SkyLine" with Puff, spinning dots, a percentage and the progress bar, in the colors of your sky. When it's done: "Restart now" or "Later". Esc turns it into a normal window. In a terminal, `skyline-update install` still works in text.

## SkyLine 1.3

**SkyLine in Italian, a friendly first start, and the rest of SkyLine Shell.**
- **Italiano:** SkyLine Settings, Puff, the Cloud Menu, the dock, the top bar, notifications, dialogs and installers all speak Italian. SkyLine follows KDE's language; switch it in SkyLine Settings > About (or in SkyLine Setup). New SkyLine USB sticks include Italian for Firefox and LibreOffice too.
- **SkyLine Setup:** a first-start setup with Puff: language, Wi-Fi, sky and weather, desktop layout and window style, your apps (and the NVIDIA driver if needed), and connecting an AI. It opens by itself for new users; run it again from SkyLine Settings > About.
- **SkyLine Dock:** SkyLine's own dock for your pinned apps and open windows. Icons grow on hover, bounce while starting, and show a dot when running. Right-click to pin, unpin, open a new window or close.
- **Sky pill (top bar):** the sky and the temperature, with quick switches: sky, Game Mode, real weather, taskbar look, Puff, and an "Update now" banner when a new SkyLine is out.
- **Window style:** new title bars with three round buttons (close, minimize, maximize). Their colors change with the sky. SkyLine Settings > Look lets you pick SkyLine or Breeze, buttons left or right.
- **Lock screen and login screen:** Puff and a greeting in the corner, on top of KDE's own password handling, so they stay as reliable as before.
- **Boot screen:** "SkyLine booting up…" under the logo.
- **Puff:** understands "update skyline" / "aggiorna skyline", and replies in Italian when the desktop is in Italian.

The SkyLine Shell layout now uses all of these. Pick it in SkyLine Settings > Layout.

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
curl -LO https://github.com/Gray7689/skyline-os/releases/download/v1.3.2/skyline-desktop_1.3.2_all.deb
sudo apt install ./skyline-desktop_1.3.2_all.deb
```
Then log out and back in.
