// SkyLine login splash: the logo on a peach sky with a small progress bar.
import QtQuick

Rectangle {
    id: root
    color: "#FFD8CC"

    // Set by Plasma while the desktop loads (1 to 6).
    property int stage

    Image {
        id: logo
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -32
        source: "images/logo.svg"
        sourceSize.width: 168
        sourceSize.height: 168
        smooth: true
    }

    Rectangle {
        id: track
        width: 220
        height: 8
        radius: 4
        color: "#FFC3B2"
        anchors.top: logo.bottom
        anchors.topMargin: 44
        anchors.horizontalCenter: parent.horizontalCenter

        Rectangle {
            height: parent.height
            radius: 4
            color: "#23264A"
            width: parent.width * Math.min(1, Math.max(0.08, root.stage / 6))
            Behavior on width {
                NumberAnimation { duration: 300; easing.type: Easing.InOutQuad }
            }
        }
    }
}
