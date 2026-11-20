// SkyLine layout "Minimal": one small floating bar, centered at the bottom.
var old = panels();
for (var i = 0; i < old.length; i++) {
    old[i].remove();
}

var panel = new Panel("org.kde.panel");
panel.location = "bottom";
panel.height = 2 * Math.ceil(gridUnit * 2.5 / 2);
panel.alignment = "center";
panel.lengthMode = "fit";

var launcher = panel.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "skyline");

var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", "applications:skyline-settings.desktop,preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop");

panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
