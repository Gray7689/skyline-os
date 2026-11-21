// One app in the SkyLine Dock: the icon grows a little on hover, bounces while the app starts,
// and shows a dot when it's running (a longer pill for the window you're using).
import QtQuick
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami

MouseArea {
    id: tile

    property var iconSource
    property string label
    property bool running
    property bool starting
    property bool active
    property bool attention
    property int windows
    property real iconSize: 40
    property bool vertical: false

    signal leftClicked()
    signal middleClicked()
    signal menuRequested()

    hoverEnabled: true
    acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
    onClicked: mouse => {
        if (mouse.button === Qt.MiddleButton) middleClicked()
        else if (mouse.button === Qt.RightButton) menuRequested()
        else leftClicked()
    }
    onPressAndHold: menuRequested()

    PlasmaCore.ToolTipArea {
        anchors.fill: parent
        mainText: tile.label
        subText: tile.windows > 1 ? i18np("%1 window", "%1 windows", tile.windows) : ""
        location: PlasmaCore.Types.Floating
    }

    // soft glow behind the app you're using
    Rectangle {
        anchors.centerIn: icon
        width: tile.iconSize + 12
        height: width
        radius: width / 3.2
        color: Kirigami.Theme.highlightColor
        opacity: tile.active ? 0.22 : (tile.containsMouse ? 0.12 : 0)
        Behavior on opacity { NumberAnimation { duration: 140 } }
    }

    Kirigami.Icon {
        id: icon
        source: tile.iconSource
        width: tile.iconSize
        height: tile.iconSize
        anchors.centerIn: parent
        anchors.verticalCenterOffset: tile.vertical ? 0 : -(lift + bounce)
        anchors.horizontalCenterOffset: tile.vertical ? lift + bounce : 0
        active: tile.containsMouse
        scale: tile.pressed ? 0.92 : (tile.containsMouse ? 1.12 : 1.0)
        property real lift: tile.containsMouse ? 3 : 0
        property real bounce: 0
        Behavior on scale { NumberAnimation { duration: 140; easing.type: Easing.OutBack } }
        Behavior on lift { NumberAnimation { duration: 140 } }

        // bounces while the app is starting
        SequentialAnimation on bounce {
            running: tile.starting
            loops: Animation.Infinite
            NumberAnimation { to: 8; duration: 260; easing.type: Easing.OutQuad }
            NumberAnimation { to: 0; duration: 260; easing.type: Easing.InQuad }
        }
    }
    onStartingChanged: if (!starting) icon.bounce = 0

    // running indicator
    Rectangle {
        visible: tile.running || tile.attention
        width: tile.vertical ? 4 : (tile.active ? 14 : 5)
        height: tile.vertical ? (tile.active ? 14 : 5) : 4
        radius: 2
        color: tile.attention ? "#FF6F61" : (tile.active ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor)
        opacity: tile.active || tile.attention ? 1 : 0.55
        anchors.horizontalCenter: tile.vertical ? undefined : parent.horizontalCenter
        anchors.bottom: tile.vertical ? undefined : parent.bottom
        anchors.bottomMargin: 2
        anchors.verticalCenter: tile.vertical ? parent.verticalCenter : undefined
        anchors.left: tile.vertical ? parent.left : undefined
        anchors.leftMargin: 2
        Behavior on width { NumberAnimation { duration: 160 } }
        Behavior on height { NumberAnimation { duration: 160 } }
    }
}
