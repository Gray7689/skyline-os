// The SkyLine Cloud Menu: Puff's greeting, search (apps, files, or ask Puff), pinned apps,
// all apps, the sky buttons, and lock / sleep / restart / power off.
import QtQuick
import QtQuick.Layouts
import QtQml.Models
import org.kde.kirigami as Kirigami
import org.kde.plasma.components as PC3

Item {
    id: menu

    // Filled in by main.qml (Plasma's own app and search models).
    property var appsModel: null
    property var resultsModel: null
    property string userName: ""
    property string skyMode: "auto"
    // Desktop file ids (or parts of them) shown under "Pinned", in this order of preference.
    property var pins: ["org.kde.dolphin", "firefox", "claude", "com.discordapp.Discord",
                        "com.valvesoftware.Steam", "skyline-settings", "org.kde.konsole", "org.kde.discover"]
    property bool showAll: false
    readonly property string query: search.text.trim()

    signal launch(var model, int row)
    signal runCommand(string command)
    signal askPuff(string text)

    function reset() {
        search.text = ""
        showAll = false
        pinnedApps.refresh()
        search.forceActiveFocus()
    }

    function greeting() {
        const h = new Date().getHours()
        const part = h < 5 ? "Good night" : h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening"
        return userName ? part + ", " + userName + "!" : part + "!"
    }

    implicitWidth: 580
    implicitHeight: 640
    Layout.preferredWidth: 580
    Layout.preferredHeight: 640
    Layout.minimumWidth: 480
    Layout.minimumHeight: 560

    // ---------------------------------------------------------------- pinned apps
    DelegateModel {
        id: pinnedApps
        model: menu.appsModel
        groups: [ DelegateModelGroup { name: "pinned" } ]
        filterOnGroup: "pinned"

        function refresh() {
            for (let i = 0; i < items.count; ++i) {
                const item = items.get(i)
                const id = String(item.model.favoriteId || "")
                item.inPinned = menu.pins.some(p => id.indexOf(p) >= 0)
            }
        }

        delegate: AppTile {
            required property var model
            icon: model.decoration
            label: model.display
            onLaunched: menu.launch(menu.appsModel, DelegateModel.itemsIndex)
        }
    }

    Connections {
        target: menu.appsModel
        ignoreUnknownSignals: true
        function onCountChanged() { pinnedApps.refresh() }
        function onModelReset() { pinnedApps.refresh() }
    }
    Component.onCompleted: pinnedApps.refresh()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 6
        spacing: 12

        // ------------------------------------------------------------ cloud header with Puff
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 108

            Rectangle {
                id: cloud
                anchors.fill: parent
                anchors.topMargin: 22
                radius: 22
                color: Kirigami.Theme.alternateBackgroundColor
            }
            Row {
                anchors.horizontalCenter: cloud.horizontalCenter
                y: 0
                spacing: -18
                Repeater {
                    model: [44, 56, 50, 60, 46, 54]
                    delegate: Rectangle {
                        required property int modelData
                        width: modelData + 34
                        height: width
                        radius: width / 2
                        y: 46 - height / 2
                        color: cloud.color
                    }
                }
            }
            RowLayout {
                anchors.fill: cloud
                anchors.leftMargin: 20
                anchors.rightMargin: 20
                spacing: 16

                PuffPixels {
                    size: 54
                    Layout.preferredWidth: implicitWidth
                    Layout.preferredHeight: implicitHeight
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    PC3.Label {
                        Layout.fillWidth: true
                        text: menu.greeting()
                        font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.45
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                    }
                    PC3.Label {
                        Layout.fillWidth: true
                        text: "What do you want to do?"
                        opacity: 0.7
                    }
                }
            }
        }

        // ------------------------------------------------------------ search
        PC3.TextField {
            id: search
            Layout.fillWidth: true
            Layout.preferredHeight: 42
            placeholderText: "Search apps and files, or ask Puff…"
            focus: true
            Keys.onReturnPressed: {
                if (menu.resultsModel && menu.resultsModel.count > 0) {
                    menu.launch(menu.resultsModel, 0)
                } else if (menu.query.length > 0) {
                    menu.askPuff(menu.query)
                }
            }
            Keys.onDownPressed: {
                results.currentIndex = 0
                results.forceActiveFocus()
            }
        }

        // ------------------------------------------------------------ middle: results, all apps, or pinned
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Search results
            ColumnLayout {
                anchors.fill: parent
                visible: menu.query.length > 0
                spacing: 4

                MouseArea {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: menu.askPuff(menu.query)
                    Rectangle {
                        anchors.fill: parent
                        radius: 12
                        color: Kirigami.Theme.highlightColor
                        opacity: parent.containsMouse ? 0.22 : 0.1
                    }
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        spacing: 12
                        PuffPixels { size: 28; animate: false; Layout.preferredWidth: implicitWidth; Layout.preferredHeight: implicitHeight }
                        PC3.Label {
                            Layout.fillWidth: true
                            text: "Ask Puff: “" + menu.query + "”"
                            elide: Text.ElideRight
                        }
                    }
                }

                ListView {
                    id: results
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: menu.resultsModel
                    keyNavigationEnabled: true
                    highlightMoveDuration: 0
                    Keys.onReturnPressed: menu.launch(menu.resultsModel, currentIndex)
                    Keys.onUpPressed: event => {
                        if (currentIndex <= 0) search.forceActiveFocus()
                        else event.accepted = false
                    }
                    delegate: MouseArea {
                        required property int index
                        required property var model
                        width: ListView.view.width
                        height: 46
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: menu.launch(menu.resultsModel, index)
                        Rectangle {
                            anchors.fill: parent
                            radius: 10
                            color: Kirigami.Theme.highlightColor
                            opacity: parent.containsMouse || parent.ListView.isCurrentItem ? 0.22 : 0
                        }
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            spacing: 12
                            Kirigami.Icon { source: model.decoration; Layout.preferredWidth: 30; Layout.preferredHeight: 30 }
                            PC3.Label { text: model.display; Layout.fillWidth: true; elide: Text.ElideRight }
                            PC3.Label {
                                text: model.description || ""
                                opacity: 0.6
                                elide: Text.ElideRight
                                Layout.maximumWidth: 200
                            }
                        }
                    }
                }
            }

            // All apps
            ListView {
                id: allApps
                anchors.fill: parent
                visible: menu.query.length === 0 && menu.showAll
                clip: true
                model: menu.appsModel
                header: MouseArea {
                    width: ListView.view.width
                    height: 36
                    cursorShape: Qt.PointingHandCursor
                    onClicked: menu.showAll = false
                    PC3.Label { anchors.verticalCenter: parent.verticalCenter; text: "‹  Pinned"; opacity: 0.75 }
                }
                delegate: MouseArea {
                    required property int index
                    required property var model
                    width: ListView.view.width
                    height: 44
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: menu.launch(menu.appsModel, index)
                    Rectangle {
                        anchors.fill: parent
                        radius: 10
                        color: Kirigami.Theme.highlightColor
                        opacity: parent.containsMouse ? 0.22 : 0
                    }
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        spacing: 12
                        Kirigami.Icon { source: model.decoration; Layout.preferredWidth: 30; Layout.preferredHeight: 30 }
                        PC3.Label { text: model.display; Layout.fillWidth: true; elide: Text.ElideRight }
                    }
                }
            }

            // Pinned
            ColumnLayout {
                anchors.fill: parent
                visible: menu.query.length === 0 && !menu.showAll
                spacing: 6
                RowLayout {
                    Layout.fillWidth: true
                    PC3.Label { text: "Pinned"; opacity: 0.7; font.weight: Font.DemiBold; Layout.fillWidth: true }
                    PC3.ToolButton { text: "All apps  ›"; onClicked: menu.showAll = true }
                }
                GridView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    cellWidth: Math.floor(width / 4)
                    cellHeight: 104
                    interactive: false
                    model: pinnedApps
                }
            }
        }

        // ------------------------------------------------------------ sky
        PC3.Label { text: "Sky"; opacity: 0.7; font.weight: Font.DemiBold }
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Repeater {
                model: [
                    { id: "sunrise", label: "Sunrise", bg: "#FFD8CC", fg: "#23264A" },
                    { id: "day", label: "Day", bg: "#CDEBFF", fg: "#23264A" },
                    { id: "dusk", label: "Dusk", bg: "#E4DBFF", fg: "#23264A" },
                    { id: "night", label: "Night", bg: "#1B2150", fg: "#EEF0FF" },
                    { id: "auto", label: "Follow the day", bg: "transparent", fg: "" }
                ]
                delegate: MouseArea {
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.preferredWidth: modelData.id === "auto" ? 150 : 90
                    Layout.preferredHeight: 38
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        menu.skyMode = modelData.id
                        menu.runCommand("skyline-sky " + modelData.id)
                    }
                    Rectangle {
                        anchors.fill: parent
                        radius: height / 2
                        color: modelData.bg
                        border.width: menu.skyMode === modelData.id ? 3 : 1
                        border.color: menu.skyMode === modelData.id ? Kirigami.Theme.highlightColor
                                                                    : Qt.rgba(0.5, 0.5, 0.6, 0.45)
                    }
                    PC3.Label {
                        anchors.centerIn: parent
                        text: modelData.label
                        color: modelData.fg || Kirigami.Theme.textColor
                        font.weight: Font.DemiBold
                    }
                }
            }
        }

        // ------------------------------------------------------------ you and power
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: Kirigami.Theme.textColor
            opacity: 0.15
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Kirigami.Icon { source: "user-identity"; Layout.preferredWidth: 28; Layout.preferredHeight: 28 }
            PC3.Label { text: menu.userName; font.weight: Font.DemiBold; Layout.fillWidth: true; elide: Text.ElideRight }
            Repeater {
                model: [
                    { label: "Lock", icon: "system-lock-screen", cmd: "loginctl lock-session" },
                    { label: "Sleep", icon: "system-suspend", cmd: "systemctl suspend" },
                    { label: "Restart", icon: "system-reboot",
                      cmd: "dbus-send --session --type=method_call --dest=org.kde.LogoutPrompt /LogoutPrompt org.kde.LogoutPrompt.promptReboot" },
                    { label: "Off", icon: "system-shutdown",
                      cmd: "dbus-send --session --type=method_call --dest=org.kde.LogoutPrompt /LogoutPrompt org.kde.LogoutPrompt.promptShutDown" }
                ]
                delegate: PC3.ToolButton {
                    required property var modelData
                    text: modelData.label
                    icon.name: modelData.icon
                    onClicked: menu.runCommand(modelData.cmd)
                }
            }
        }
    }
}
