import QtQuick 2.15
import QtQuick.Controls 2.15

// Documentation de la personalisation des composants
// https://doc.qt.io/qt-6/qtqml-documents-definetypes.html

// Liste des documentations pour les composants utilisés
// Rectangle :      https://doc.qt.io/qt-6/qml-qtquick-rectangle.html
// Image :          https://doc.qt.io/qt-6/qml-qtquick-image.html
// Text :           https://doc.qt.io/qt-6/qml-qtquick-text.html
// MouseArea :      https://doc.qt.io/qt-6/qml-qtquick-mousearea.html


Item {
    id: root

    width: selectorBody.width
    height: selectorBody.height

    // Propriétés sur l'image
    property string source: ""
    property string path: "../assets/"

    // Propriété sur le nom de la mission
    property int fontSize: 12
    property string name: ""

    // Propriétés sur les couleurs utilisées
    property string backgroundColor: "#000000"
    property string textColor: "#C8C8C8"
    property string borderColor: "#C8C8C8"
    property string highlightColor: "#000080"

    // Signaux à surchager en QML ou en Python
    signal clicked(string text)


    // Rectangle pour la couleur du fond du bouton
    Rectangle{
        id: selectorBody

        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: selectorImage.height + root.fontSize * 1.5


        color: root.backgroundColor
        border.width: 1
        border.color: borderColor
    }


    // Image centrée sur le bouton
    Image {
        id: selectorImage

        anchors.top: parent.top
        anchors.topMargin: selectorBody.border.width
        anchors.left: parent.left
        anchors.leftMargin: selectorBody.border.width
        anchors.right: parent.right
        anchors.rightMargin: selectorBody.border.width
        fillMode: Image.PreserveAspectFit

        source: root.source !== "" ? (root.path + root.source)
                                   : ""
    }

    // Texte visible au centre du bouton
    Text{
        id: selectorText

        anchors.top: selectorImage.bottom
        anchors.bottom: parent.bottom
        anchors.bottomMargin: selectorBody.border.width
        anchors.horizontalCenter: parent.horizontalCenter

        text: root.name
        font.pixelSize: root.fontSize
        font.family: "Verdana"
        color: root.textColor
    }

    // Zone de détection de souris pour détecter les clics
    MouseArea{
        id: selectorArea

        anchors.fill: parent

        hoverEnabled: true
        enabled: true


        // Répétition des signaux
        onClicked: root.clicked(root.name)
    }

    // Rectangle pour le highlight
    Rectangle {
        id: selectorHighlight

        anchors.fill: parent
        anchors.margins: selectorBody.border.width

        color: root.highlightColor
        opacity: selectorArea.containsPress ? 0.5 : 0.3
        visible: selectorArea.containsMouse
    }
}
