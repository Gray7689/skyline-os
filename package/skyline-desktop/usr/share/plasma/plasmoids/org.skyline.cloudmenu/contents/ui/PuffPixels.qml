// Puff, the SkyLine pixel cloud. Set `size` (height in pixels); Puff bobs and blinks.
import QtQuick

Item {
    id: puff

    property real size: 32
    property bool animate: true
    property bool fast: false

    readonly property int px: Math.max(1, Math.floor(size / 12))
    readonly property var rows: [
        "......oooo......",
        "...oooowwwwo....",
        "..owwwwwwwwwoo..",
        ".owwwwwwwwwwwwo.",
        "owwwwwwwwwwwwwwo",
        "owwweewwwweewwwo",
        "owwweewwwweewwwo",
        "owbbwwwwwwwwbbwo",
        "owwwwwmwwmwwwwwo",
        ".owwwwwmmwwwwwo.",
        "..oooooooooooo.."
    ]
    readonly property var colors: ({ "o": "#23264A", "w": "#FFFFFF", "e": "#23264A", "m": "#23264A", "b": "#FFB3A6" })

    property real bob: 0
    property bool blink: false

    implicitWidth: 16 * px
    implicitHeight: 12 * px

    SequentialAnimation on bob {
        running: puff.animate
        loops: Animation.Infinite
        NumberAnimation { from: 0; to: 1; duration: puff.fast ? 300 : 900; easing.type: Easing.InOutSine }
        NumberAnimation { from: 1; to: 0; duration: puff.fast ? 300 : 900; easing.type: Easing.InOutSine }
    }

    Timer {
        interval: 3800
        repeat: true
        running: puff.animate
        onTriggered: {
            puff.blink = true
            blinkOff.restart()
        }
    }
    Timer {
        id: blinkOff
        interval: 160
        onTriggered: puff.blink = false
    }

    Repeater {
        model: 16 * 11
        delegate: Rectangle {
            required property int index
            readonly property int row: Math.floor(index / 16)
            readonly property int col: index % 16
            readonly property string ch: puff.rows[row].charAt(col)
            visible: ch !== "."
            x: col * puff.px
            y: row * puff.px + Math.round(puff.bob * puff.px)
            width: puff.px
            height: puff.px
            color: (ch === "e" && puff.blink && row === 5) ? "#FFFFFF" : (puff.colors[ch] || "transparent")
        }
    }
}
