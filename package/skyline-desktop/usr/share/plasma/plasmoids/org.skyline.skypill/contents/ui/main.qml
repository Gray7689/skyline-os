// SkyLine Sky: a pill in the top bar with the sky and the temperature.
// Click it for quick switches: the sky, Game Mode, real weather, the taskbar look and Puff.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property var sky: ({ mode: "auto", sky: "day", weather: "off", kind: "clear", place: "", lat: "", lon: "" })
    property string temperature: ""
    property bool gameMode: false
    property string updateText: ""

    readonly property string skyName: ({ sunrise: i18n("Sunrise"), day: i18n("Day"), dusk: i18n("Dusk"),
                                         night: i18n("Night") })[sky.sky] || i18n("Day")
    readonly property string weatherName: ({ clear: i18n("Clear"), cloudy: i18n("Cloudy"), rain: i18n("Rain"),
                                             snow: i18n("Snow") })[sky.kind] || ""
    readonly property string iconName: {
        const night = sky.sky === "night"
        if (sky.kind === "rain") return "weather-showers"
        if (sky.kind === "snow") return "weather-snow"
        if (sky.kind === "cloudy") return night ? "weather-few-clouds-night" : "weather-clouds"
        if (sky.sky === "sunrise" || sky.sky === "dusk") return "weather-few-clouds"
        return night ? "weather-clear-night" : "weather-clear"
    }
    readonly property string city: (sky.place || "").split(",")[0]

    switchWidth: Kirigami.Units.gridUnit * 12
    switchHeight: Kirigami.Units.gridUnit * 12
    toolTipMainText: city ? i18n("%1 in %2", skyName, city) : skyName
    toolTipSubText: temperature ? temperature + (weatherName ? " · " + weatherName : "") : i18n("Click for quick switches")

    P5Support.DataSource {
        id: shell
        engine: "executable"
        connectedSources: []
        onNewData: (source, data) => {
            const out = (data["stdout"] || "").trim()
            if (source === "skyline-sky json") {
                try { root.sky = JSON.parse(out); root.fetchTemperature() } catch (e) {}
            } else if (source === "skyline-gamemode status") {
                root.gameMode = out === "on"
            } else if (source === "skyline-update check") {
                // exit code 10 = a new SkyLine version is out
                root.updateText = data["exit code"] === 10 ? out : ""
            }
            disconnectSource(source)
        }
    }
    function run(command) { shell.connectSource(command) }
    function refresh() { run("skyline-sky json"); run("skyline-gamemode status") }

    function fetchTemperature() {
        if (!sky.lat || !sky.lon) { temperature = ""; return }
        const xhr = new XMLHttpRequest()
        xhr.onreadystatechange = () => {
            if (xhr.readyState !== XMLHttpRequest.DONE || xhr.status !== 200) return
            try {
                const t = JSON.parse(xhr.responseText).current.temperature_2m
                root.temperature = Math.round(t) + "°"
            } catch (e) {}
        }
        xhr.open("GET", "https://api.open-meteo.com/v1/forecast?latitude=" + sky.lat + "&longitude=" + sky.lon
                 + "&current=temperature_2m")
        xhr.send()
    }

    Timer { interval: 10 * 60 * 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: root.refresh() }
    onExpandedChanged: if (expanded) { refresh(); run("skyline-update check") }

    compactRepresentation: MouseArea {
        id: pill
        hoverEnabled: true
        Layout.minimumWidth: row.implicitWidth + Kirigami.Units.largeSpacing * 2
        Layout.preferredWidth: Layout.minimumWidth
        onClicked: root.expanded = !root.expanded

        Rectangle {
            anchors.fill: parent
            anchors.topMargin: 3
            anchors.bottomMargin: 3
            radius: height / 2
            color: Kirigami.Theme.textColor
            opacity: root.expanded ? 0.16 : (pill.containsMouse ? 0.12 : 0.07)
            Behavior on opacity { NumberAnimation { duration: 120 } }
        }
        Row {
            id: row
            anchors.centerIn: parent
            spacing: Kirigami.Units.smallSpacing
            Kirigami.Icon {
                source: root.iconName
                width: Kirigami.Units.iconSizes.small
                height: width
                anchors.verticalCenter: parent.verticalCenter
            }
            Text {
                text: root.temperature ? root.temperature + (root.city ? "  " + root.city : "") : root.skyName
                color: Kirigami.Theme.textColor
                font.pixelSize: Math.max(11, Math.round(pill.height * 0.42))
                font.weight: Font.DemiBold
                anchors.verticalCenter: parent.verticalCenter
            }
            Rectangle {
                visible: root.gameMode
                width: 6; height: 6; radius: 3
                color: "#4CC38A"
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    fullRepresentation: SkyPanel {
        sky: root.sky
        skyName: root.skyName
        weatherName: root.weatherName
        iconName: root.iconName
        temperature: root.temperature
        city: root.city
        gameMode: root.gameMode
        updateText: root.updateText
        onRunCommand: command => { root.run(command); refreshLater.restart() }
        onOpenAndClose: command => { root.run(command); root.expanded = false }
        Timer { id: refreshLater; interval: 1500; onTriggered: root.refresh() }
    }
}
