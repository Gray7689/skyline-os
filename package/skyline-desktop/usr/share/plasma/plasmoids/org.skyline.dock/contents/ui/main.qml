// SkyLine Dock: pinned apps and open windows, with a dot under running apps.
// Built on Plasma's own task model, so windows, launchers and "pin" behave like KDE's task manager.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.extras as PlasmaExtras
import org.kde.taskmanager as TaskManager
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    readonly property bool vertical: Plasmoid.formFactor === PlasmaCore.Types.Vertical
    readonly property real cell: vertical ? width : height
    readonly property real iconSize: Math.round(cell * 0.66)

    preferredRepresentation: fullRepresentation
    Plasmoid.constraintHints: Plasmoid.CanFillArea

    Layout.fillWidth: false
    Layout.fillHeight: false
    Layout.minimumWidth: vertical ? Kirigami.Units.iconSizes.medium : apps.count * cell
    Layout.preferredWidth: vertical ? -1 : apps.count * cell
    Layout.minimumHeight: vertical ? apps.count * cell : Kirigami.Units.iconSizes.medium
    Layout.preferredHeight: vertical ? apps.count * cell : -1

    TaskManager.VirtualDesktopInfo { id: desktops }
    TaskManager.ActivityInfo { id: activities }

    TaskManager.TasksModel {
        id: tasks
        virtualDesktop: desktops.currentDesktop
        activity: activities.currentActivity
        screenGeometry: Plasmoid.containment.screenGeometry
        filterByVirtualDesktop: true
        filterByActivity: true
        filterByScreen: false
        hideActivatedLaunchers: true
        launchInPlace: true
        separateLaunchers: false
        sortMode: TaskManager.TasksModel.SortManually
        groupMode: TaskManager.TasksModel.GroupApplications
        groupInline: false
        onLauncherListChanged: Plasmoid.configuration.launchers = launcherList
        Component.onCompleted: {
            launcherList = Plasmoid.configuration.launchers
            apps.model = tasks
        }
    }

    function index(row, child) {
        return child === undefined ? tasks.makeModelIndex(row) : tasks.makeModelIndex(row, child)
    }

    GridLayout {
        anchors.centerIn: parent
        rowSpacing: 0
        columnSpacing: 0
        flow: root.vertical ? GridLayout.TopToBottom : GridLayout.LeftToRight
        rows: root.vertical ? -1 : 1
        columns: root.vertical ? 1 : -1

        Repeater {
            id: apps
            delegate: DockIcon {
                id: icon
                Layout.preferredWidth: root.cell
                Layout.preferredHeight: root.cell
                iconSource: model.decoration
                label: model.AppName || model.display || ""
                running: !model.IsLauncher && !model.IsStartup
                starting: model.IsStartup === true
                active: model.IsActive === true
                attention: model.IsDemandingAttention === true
                windows: model.IsGroupParent ? model.ChildCount : (running ? 1 : 0)
                iconSize: root.iconSize
                vertical: root.vertical
                property int cycle: 0

                onLeftClicked: {
                    if (model.IsLauncher) {
                        tasks.requestActivate(root.index(index))
                    } else if (model.IsGroupParent) {
                        // several windows of one app: each click brings the next one forward
                        cycle = (cycle + 1) % Math.max(1, model.ChildCount)
                        tasks.requestActivate(root.index(index, cycle))
                    } else if (model.IsMinimized) {
                        tasks.requestToggleMinimized(root.index(index))
                        tasks.requestActivate(root.index(index))
                    } else if (model.IsActive) {
                        tasks.requestToggleMinimized(root.index(index))
                    } else {
                        tasks.requestActivate(root.index(index))
                    }
                }
                onMiddleClicked: tasks.requestNewInstance(root.index(index))
                onMenuRequested: {
                    menu.row = index
                    menu.launcherUrl = model.LauncherUrlWithoutIcon || ""
                    menu.isLauncher = model.IsLauncher === true
                    menu.visualParent = icon
                    menu.openRelative()
                }
            }
        }
    }

    PlasmaExtras.Menu {
        id: menu
        property int row: -1
        property string launcherUrl: ""
        property bool isLauncher: false
        readonly property bool pinned: launcherUrl !== "" && tasks.launcherPosition(launcherUrl) >= 0
        placement: root.vertical ? PlasmaExtras.Menu.RightPosedTopAlignedPopup : PlasmaExtras.Menu.TopPosedLeftAlignedPopup

        PlasmaExtras.MenuItem {
            text: i18n("New window")
            icon: "window-new"
            visible: !menu.isLauncher
            onClicked: tasks.requestNewInstance(root.index(menu.row))
        }
        PlasmaExtras.MenuItem {
            text: menu.pinned ? i18n("Unpin from dock") : i18n("Pin to dock")
            icon: menu.pinned ? "window-unpin" : "window-pin"
            visible: menu.launcherUrl !== ""
            onClicked: menu.pinned ? tasks.requestRemoveLauncher(menu.launcherUrl)
                                   : tasks.requestAddLauncher(menu.launcherUrl)
        }
        PlasmaExtras.MenuItem {
            text: i18n("Close")
            icon: "window-close"
            visible: !menu.isLauncher
            onClicked: tasks.requestClose(root.index(menu.row))
        }
    }
}
