// SkyLine first-login desktop: Plasma's default panel, the SkyLine launcher icon,
// pinned apps and the sunrise wallpaper. Change it any time with "SkyLine Settings > Desktop layout".
loadTemplate("org.kde.plasma.desktop.defaultPanel");

var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    var d = desktopsArray[j];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/SkyLine-Peach/contents/images/3840x2160.png");
}

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    var launchers = allPanels[i].widgets("org.kde.plasma.kickoff");
    for (var k = 0; k < launchers.length; k++) {
        launchers[k].currentConfigGroup = ["General"];
        launchers[k].writeConfig("icon", "skyline");
    }
    var tasks = allPanels[i].widgets("org.kde.plasma.icontasks");
    for (var t = 0; t < tasks.length; t++) {
        tasks[t].currentConfigGroup = ["General"];
        tasks[t].writeConfig("launchers", "applications:skyline-settings.desktop,preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop,applications:org.kde.discover.desktop");
    }
}
