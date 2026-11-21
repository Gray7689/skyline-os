// SkyLine Cloud Menu (Plasma widget). The panel shows the SkyLine logo; clicking it, or pressing
// the Meta/Windows key, opens the Cloud Menu. Apps and search come from Plasma's own launcher models.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import org.kde.plasma.private.kicker as Kicker
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property string userName: ""
    property string skyMode: "auto"
    property string query: ""

    signal opened()
    readonly property var appsModel: rootModel.count > 0 ? rootModel.modelForRow(0) : null

    switchWidth: Kirigami.Units.gridUnit * 20
    switchHeight: Kirigami.Units.gridUnit * 20
    toolTipMainText: "Cloud Menu"
    toolTipSubText: "Your apps, search, the sky and Puff"

    Kicker.RootModel {
        id: rootModel
        autoPopulate: false
        appletInterface: root
        flat: true
        sorted: true
        showSeparators: false
        showTopLevelItems: false
        showAllApps: true
        showAllAppsCategorized: false
        showRecentApps: false
        showRecentDocs: false
        showPowerSession: false
        Component.onCompleted: refresh()
    }

    Kicker.RunnerModel {
        id: runnerModel
        appletInterface: root
        mergeResults: true
        query: root.expanded ? root.query : ""
    }

    // Runs shell commands (sky changes, power buttons, opening Puff).
    P5Support.DataSource {
        id: shell
        engine: "executable"
        connectedSources: []
        onNewData: (source, data) => {
            const out = (data["stdout"] || "").trim()
            if (source.indexOf("skyline-sky status") >= 0) {
                const m = out.match(/^mode: (\w+)/m)
                if (m) root.skyMode = m[1]
            } else if (source.indexOf("getent passwd") >= 0 && out.length > 0) {
                root.userName = out.split("\n")[0]
            }
            disconnectSource(source)
        }
    }
    function run(command) {
        shell.connectSource(command)
    }
    function quote(text) {
        return "'" + String(text).replace(/'/g, "'\\''") + "'"
    }

    Component.onCompleted: {
        run("sh -c 'n=$(getent passwd \"$USER\" | cut -d: -f5 | cut -d, -f1); echo \"${n:-$USER}\"'")
    }
    onExpandedChanged: {
        if (expanded) {
            run("skyline-sky status")
            root.opened()
        }
    }

    compactRepresentation: MouseArea {
        id: button
        hoverEnabled: true
        Layout.minimumWidth: Kirigami.Units.iconSizes.small
        Layout.preferredWidth: height
        onClicked: root.expanded = !root.expanded
        Kirigami.Icon {
            anchors.fill: parent
            anchors.margins: 2
            source: "skyline"
            active: button.containsMouse || root.expanded
        }
    }

    fullRepresentation: CloudMenu {
            id: cloudMenu
            appsModel: root.appsModel
            resultsModel: runnerModel.count > 0 ? runnerModel.modelForRow(0) : null
            userName: root.userName
            skyMode: root.skyMode
            onLaunch: (model, row) => {
                model.trigger(row, "", null)
                root.expanded = false
            }
            onRunCommand: command => {
                root.run(command)
                if (command.indexOf("skyline-sky") < 0) root.expanded = false
            }
            onAskPuff: text => {
                root.run("setsid -f skyline-assistant --say " + root.quote(text))
                root.expanded = false
            }
            onQueryChanged: root.query = query
            Connections {
                target: root
                function onOpened() { cloudMenu.reset() }
            }
    }
}
