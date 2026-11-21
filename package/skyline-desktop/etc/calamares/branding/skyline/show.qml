// SkyLine installer slideshow, shown while files are copied.
import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    function nextSlide() {
        presentation.goToNextSlide();
    }

    Timer {
        id: advanceTimer
        interval: 6000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: nextSlide()
    }

    Slide {
        Image {
            id: picture1
            source: "slide1.png"
            width: 560; height: 315
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
            anchors.verticalCenterOffset: -40
        }
        Text {
            anchors.horizontalCenter: picture1.horizontalCenter
            anchors.top: picture1.bottom
            anchors.topMargin: 20
            width: presentation.width - 80
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 18
            color: "#23264A"
            text: "Welcome to SkyLine. Sit back while it installs."
        }
    }

    Slide {
        Image {
            id: picture2
            source: "slide2.png"
            width: 560; height: 315
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
            anchors.verticalCenterOffset: -40
        }
        Text {
            anchors.horizontalCenter: picture2.horizontalCenter
            anchors.top: picture2.bottom
            anchors.topMargin: 20
            width: presentation.width - 80
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 18
            color: "#23264A"
            text: "Make it yours: right-click the desktop or open SkyLine Settings to change panels, widgets, colors and layouts."
        }
    }

    Slide {
        Image {
            id: picture3
            source: "slide3.png"
            width: 560; height: 315
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
            anchors.verticalCenterOffset: -40
        }
        Text {
            anchors.horizontalCenter: picture3.horizontalCenter
            anchors.top: picture3.bottom
            anchors.topMargin: 20
            width: presentation.width - 80
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 18
            color: "#23264A"
            text: "Your sky follows the day: sunrise, day, dusk and night. Install Claude, Discord, Steam and more with SkyLine Apps."
        }
    }

    function onActivate() {
        presentation.currentSlide = 0;
    }

    function onLeave() {
    }
}
