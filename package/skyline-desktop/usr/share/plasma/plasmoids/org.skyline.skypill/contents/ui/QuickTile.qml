// A square on/off tile in the sky panel.
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

MouseArea {
    id: tile
    property string icon
    property string label
    property bool on

    implicitWidth: Kirigami.Units.gridUnit * 6
    implicitHeight: Kirigami.Units.gridUnit * 4
    Layout.fillWidth: true
    hoverEnabled: true

    Rectangle {
        anchors.fill: parent
        radius: 14
        color: tile.on ? Kirigami.Theme.highlightColor
                       : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b,
                                 tile.containsMouse ? 0.12 : 0.07)
        Behavior on color { ColorAnimation { duration: 120 } }
    }
    Column {
        anchors.centerIn: parent
        spacing: 4
        Kirigami.Icon {
            source: tile.icon
            width: Kirigami.Units.iconSizes.medium
            height: width
            anchors.horizontalCenter: parent.horizontalCenter
        }
        Text {
            text: tile.label
            color: tile.on ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
            font.pixelSize: 11
            font.weight: Font.DemiBold
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}
