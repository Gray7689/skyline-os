// One app in the Cloud Menu: a big icon with its name under it.
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.components as PC3

MouseArea {
    id: tile

    property var icon
    property string label
    property bool current: false

    signal launched()

    width: 120
    height: 100
    hoverEnabled: true
    cursorShape: Qt.PointingHandCursor
    onClicked: tile.launched()

    Rectangle {
        anchors.fill: parent
        anchors.margins: 2
        radius: 14
        color: Kirigami.Theme.highlightColor
        opacity: tile.containsMouse || tile.current ? 0.22 : 0
        Behavior on opacity { NumberAnimation { duration: 120 } }
    }

    ColumnLayout {
        anchors.centerIn: parent
        width: parent.width - 12
        spacing: 6

        Kirigami.Icon {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 52
            Layout.preferredHeight: 52
            source: tile.icon
        }
        PC3.Label {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            text: tile.label
            elide: Text.ElideRight
            maximumLineCount: 1
        }
    }
}
