// Puff in the taskbar: a little animated pixel cloud. Click it to chat with the SkyLine Assistant.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    preferredRepresentation: compactRepresentation
    toolTipMainText: "Puff"
    toolTipSubText: i18n("Your SkyLine Assistant. Click to chat.")

    P5Support.DataSource {
        id: shell
        engine: "executable"
        connectedSources: []
        onNewData: (source, data) => disconnectSource(source)
    }

    compactRepresentation: MouseArea {
        id: area
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        Layout.minimumWidth: Kirigami.Units.iconSizes.medium
        Layout.preferredWidth: Math.max(Kirigami.Units.iconSizes.medium, height * 1.4)
        onClicked: shell.connectSource("setsid -f skyline-assistant")

        Rectangle {
            anchors.fill: parent
            anchors.margins: 2
            radius: 8
            color: Kirigami.Theme.highlightColor
            opacity: area.containsMouse ? 0.2 : 0
        }
        PuffPixels {
            anchors.centerIn: parent
            size: Math.min(area.height * 0.85, area.width * 0.6)
            fast: area.containsMouse
        }
    }
}
