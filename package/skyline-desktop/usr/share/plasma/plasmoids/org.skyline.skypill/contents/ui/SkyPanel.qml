// The panel that opens from the sky pill.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PC3
import org.kde.kirigami as Kirigami

Item {
    id: panel

    property var sky
    property string skyName
    property string weatherName
    property string iconName
    property string temperature
    property string city
    property bool gameMode
    property string updateText

    signal runCommand(string command)
    signal openAndClose(string command)

    implicitWidth: Kirigami.Units.gridUnit * 21
    implicitHeight: column.implicitHeight + Kirigami.Units.largeSpacing * 2
    Layout.preferredWidth: implicitWidth
    Layout.preferredHeight: implicitHeight

    readonly property var skyColors: ({ sunrise: ["#FFD8CC", "#FFB8A3", "#23264A"], day: ["#CDEBFF", "#9FD3FF", "#1F2A44"],
                                        dusk: ["#E4DBFF", "#C3B0FF", "#2A2350"], night: ["#2E3360", "#1B2150", "#EEF0FF"] })
    readonly property var colorsNow: skyColors[sky.sky] || skyColors.day

    ColumnLayout {
        id: column
        anchors.fill: parent
        anchors.margins: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing

        // a new SkyLine version is out
        Rectangle {
            visible: panel.updateText !== ""
            Layout.fillWidth: true
            Layout.preferredHeight: visible ? updateRow.implicitHeight + Kirigami.Units.largeSpacing : 0
            radius: 12
            color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.22)
            RowLayout {
                id: updateRow
                anchors.fill: parent
                anchors.margins: Kirigami.Units.smallSpacing
                Kirigami.Icon { source: "system-software-update"; Layout.preferredWidth: Kirigami.Units.iconSizes.smallMedium; Layout.preferredHeight: Layout.preferredWidth }
                PC3.Label { text: panel.updateText; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                PC3.ToolButton {
                    text: i18n("Update now")
                    onClicked: panel.openAndClose("setsid -f skyline-update-screen")
                }
            }
        }

        // the sky right now
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 5
            radius: 16
            gradient: Gradient {
                GradientStop { position: 0; color: panel.colorsNow[0] }
                GradientStop { position: 1; color: panel.colorsNow[1] }
            }
            RowLayout {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.largeSpacing
                spacing: Kirigami.Units.largeSpacing
                Kirigami.Icon {
                    source: panel.iconName
                    Layout.preferredWidth: Kirigami.Units.iconSizes.large
                    Layout.preferredHeight: Kirigami.Units.iconSizes.large
                }
                ColumnLayout {
                    spacing: 0
                    Layout.fillWidth: true
                    Text {
                        text: panel.temperature ? panel.temperature : panel.skyName
                        color: panel.colorsNow[2]
                        font.pixelSize: Kirigami.Units.gridUnit * 1.7
                        font.weight: Font.Bold
                    }
                    Text {
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                        color: panel.colorsNow[2]
                        opacity: 0.85
                        text: {
                            const bits = []
                            if (panel.temperature) bits.push(panel.skyName)
                            if (panel.weatherName && panel.sky.weather === "on") bits.push(panel.weatherName)
                            if (panel.city) bits.push(panel.city)
                            return bits.length ? bits.join(" · ") : i18n("Set your city in SkyLine Settings to see the temperature")
                        }
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        // sky buttons
        PC3.Label { text: i18n("Sky"); font.weight: Font.DemiBold }
        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            Repeater {
                model: [
                    { id: "sunrise", label: i18n("Sunrise"), fill: "#FFD8CC", ink: "#23264A" },
                    { id: "day", label: i18n("Day"), fill: "#CDEBFF", ink: "#1F2A44" },
                    { id: "dusk", label: i18n("Dusk"), fill: "#E4DBFF", ink: "#2A2350" },
                    { id: "night", label: i18n("Night"), fill: "#1B2150", ink: "#EEF0FF" },
                    { id: "auto", label: i18n("Auto"), fill: "transparent", ink: Kirigami.Theme.textColor }
                ]
                delegate: MouseArea {
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.preferredHeight: Kirigami.Units.gridUnit * 1.9
                    hoverEnabled: true
                    onClicked: panel.runCommand("skyline-sky " + modelData.id)
                    Rectangle {
                        anchors.fill: parent
                        radius: height / 2
                        color: modelData.fill
                        border.width: panel.sky.mode === modelData.id ? 2 : 1
                        border.color: panel.sky.mode === modelData.id ? Kirigami.Theme.highlightColor
                                      : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.18)
                        scale: parent.containsMouse ? 1.04 : 1
                        Behavior on scale { NumberAnimation { duration: 100 } }
                        Text {
                            anchors.centerIn: parent
                            text: modelData.label
                            color: modelData.ink
                            font.pixelSize: 12
                            font.weight: Font.DemiBold
                        }
                    }
                }
            }
        }

        // quick switches
        GridLayout {
            Layout.fillWidth: true
            columns: 3
            columnSpacing: Kirigami.Units.smallSpacing
            rowSpacing: Kirigami.Units.smallSpacing
            QuickTile {
                icon: "input-gaming"
                label: i18n("Game Mode")
                on: panel.gameMode
                onClicked: panel.runCommand("skyline-gamemode " + (panel.gameMode ? "off" : "on"))
            }
            QuickTile {
                icon: "weather-showers"
                label: i18n("Real weather")
                on: panel.sky.weather === "on"
                onClicked: {
                    if (!panel.sky.lat) panel.openAndClose("skyline-settings --page sky")
                    else panel.runCommand("skyline-sky weather " + (panel.sky.weather === "on" ? "off" : "on"))
                }
            }
            QuickTile {
                icon: "skyline"
                label: i18n("Ask Puff")
                on: false
                onClicked: panel.openAndClose("setsid -f skyline-assistant")
            }
        }

        // taskbar look
        PC3.Label { text: i18n("Taskbar"); font.weight: Font.DemiBold }
        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            Repeater {
                model: [
                    { id: "auto", label: i18n("Auto") }, { id: "black", label: i18n("Black") },
                    { id: "white", label: i18n("White") }, { id: "glass", label: i18n("Glass") },
                    { id: "clear", label: i18n("Clear") }
                ]
                delegate: PC3.ToolButton {
                    required property var modelData
                    Layout.fillWidth: true
                    text: modelData.label
                    onClicked: panel.openAndClose("skyline-taskbar " + modelData.id)
                }
            }
        }

        PC3.ToolButton {
            Layout.alignment: Qt.AlignRight
            icon.name: "configure"
            text: i18n("SkyLine Settings")
            onClicked: panel.openAndClose("skyline-settings")
        }
    }
}
