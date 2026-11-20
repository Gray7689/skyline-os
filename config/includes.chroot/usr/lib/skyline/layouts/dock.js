// SkyLine layout "Dock": a thin top bar plus a centered app dock at the bottom.
var old = panels();
for (var i = 0; i < old.length; i++) {
    old[i].remove();
}

var topBar = new Panel("org.kde.panel");
topBar.location = "top";
topBar.height = 2 * Math.ceil(gridUnit * 1.6 / 2);

var launcher = topBar.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "skyline");

topBar.addWidget("org.kde.plasma.appmenu");
topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.digitalclock");
topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.systemtray");

var dock = new Panel("org.kde.panel");
dock.location = "bottom";
dock.height = 2 * Math.ceil(gridUnit * 3.5 / 2);
dock.alignment = "center";
dock.lengthMode = "fit";

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", "applications:skyline-settings.desktop,preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop,applications:org.kde.discover.desktop");
