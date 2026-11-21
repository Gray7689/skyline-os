// SkyLine layout "SkyLine Shell": a thin top bar (clock and system icons) and a floating dock
// with the Cloud Menu, your apps and Puff. The Meta/Windows key opens the Cloud Menu.
var old = panels();
for (var i = 0; i < old.length; i++) {
    old[i].remove();
}

var topBar = new Panel("org.kde.panel");
topBar.location = "top";
topBar.height = 2 * Math.ceil(gridUnit * 1.6 / 2);
topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.digitalclock");
topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.systemtray");

var dock = new Panel("org.kde.panel");
dock.location = "bottom";
dock.height = 2 * Math.ceil(gridUnit * 3.5 / 2);
dock.alignment = "center";
dock.lengthMode = "fit";

dock.addWidget("org.skyline.cloudmenu");

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", "preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop,applications:skyline-settings.desktop,applications:org.kde.discover.desktop");

dock.addWidget("org.skyline.puff");
