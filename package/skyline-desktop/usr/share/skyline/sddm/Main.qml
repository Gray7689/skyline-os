// SkyLine login screen: KDE's Breeze login (users, password, sessions) with SkyLine's corner on top.
// BreezeMain.qml is Breeze's own Main.qml, copied next to this file by
// /usr/lib/skyline/sync-breeze-copies whenever the Breeze login theme is installed or updated.
import QtQuick

BreezeMain {
    id: skylineLogin

    SkyLineCorner {
        z: 1000
        mode: "login"
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 28
    }
}
