// SkyLine's corner on the lock screen and login screen: Puff and a greeting.
// It only draws; clicks and typing go straight to the password box underneath.
import QtQuick

Rectangle {
    id: corner
    property string mode: "lock"   // "lock" or "login"
    property string userName: ""

    readonly property bool italian: {
        const langs = (Qt.locale().uiLanguages || []).join(",") + "," + Qt.locale().name
        return langs.toLowerCase().indexOf("it") === 0 || langs.toLowerCase().indexOf(",it") >= 0
    }
    readonly property string line: {
        if (mode === "login") return italian ? "Benvenuto in SkyLine" : "Welcome to SkyLine"
        const h = new Date().getHours()
        if (italian) return h < 5 ? "Buonanotte" : h < 12 ? "Buongiorno" : h < 18 ? "Buon pomeriggio" : "Buonasera"
        return h < 5 ? "Good night" : h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening"
    }

    width: content.implicitWidth + 36
    height: content.implicitHeight + 20
    radius: height / 2
    color: Qt.rgba(0.08, 0.09, 0.22, 0.38)
    border.color: Qt.rgba(1, 1, 1, 0.18)
    border.width: 1

    Row {
        id: content
        anchors.centerIn: parent
        spacing: 12
        PuffPixels { size: 40; animate: true; anchors.verticalCenter: parent.verticalCenter }
        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 1
            Text {
                text: "SkyLine"
                color: "white"
                font.pixelSize: 20
                font.weight: Font.Bold
            }
            Text {
                text: corner.line + (corner.userName ? ", " + corner.userName : "")
                color: "white"
                opacity: 0.85
                font.pixelSize: 13
            }
        }
    }
}
