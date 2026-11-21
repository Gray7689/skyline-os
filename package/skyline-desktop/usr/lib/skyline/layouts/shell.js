// SkyLine layout "SkyLine Shell": SkyLine's own desktop.
// Top bar: the sky pill (sky, temperature, quick switches), the clock and the system icons.
// Floating dock: the Cloud Menu, the SkyLine Dock (pinned apps and open windows) and Puff.
// The Meta/Windows key opens the Cloud Menu.
var old = panels();
for (var i = 0; i < old.length; i++) {
    old[i].remove();
}

var topBar = new Panel("org.kde.panel");
topBar.location = "top";
topBar.height = 2 * Math.ceil(gridUnit * 1.6 / 2);
topBar.addWidget("org.skyline.skypill");
topBar.addWidget("org.kde.plasma.panelspacer");
var clock = topBar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateDisplayFormat", "BesideTime");
topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.systemtray");

var dock = new Panel("org.kde.panel");
dock.location = "bottom";
dock.height = 2 * Math.ceil(gridUnit * 3.5 / 2);
dock.alignment = "center";
dock.lengthMode = "fit";

dock.addWidget("org.skyline.cloudmenu");

var apps = dock.addWidget("org.skyline.dock");
apps.currentConfigGroup = ["General"];
apps.writeConfig("launchers", "preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop,applications:skyline-settings.desktop,applications:org.kde.discover.desktop");

dock.addWidget("org.skyline.puff");
