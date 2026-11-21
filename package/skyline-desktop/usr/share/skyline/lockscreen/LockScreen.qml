// SkyLine lock screen: KDE's Breeze lock screen (it handles the password and unlocking) with
// SkyLine's corner on top. BreezeLockScreen.qml is Breeze's own LockScreen.qml, copied next to this
// file by /usr/lib/skyline/sync-breeze-copies whenever Breeze is installed or updated.
import QtQuick

BreezeLockScreen {
    id: skylineLock

    SkyLineCorner {
        z: 1000
        mode: "lock"
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 28
    }
}
