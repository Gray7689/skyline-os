// SkyLine layout "Classic": one bar along the bottom.
var old = panels();
for (var i = 0; i < old.length; i++) {
    old[i].remove();
}

var panel = new Panel("org.kde.panel");
panel.location = "bottom";
panel.height = 2 * Math.ceil(gridUnit * 2.5 / 2);

var launcher = panel.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "skyline");

panel.addWidget("org.kde.plasma.pager");

var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", "applications:skyline-settings.desktop,preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop,applications:org.kde.discover.desktop");

panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
panel.addWidget("org.kde.plasma.showdesktop");
