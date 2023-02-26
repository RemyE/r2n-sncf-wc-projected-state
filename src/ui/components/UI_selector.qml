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

    // Composant à placer avec les ancres. aucune dimensions à placer
    anchors.fill: parent

    // Propriétés sur l'image
    property string image: ""
    readonly property string path: "../assets"

    // Propriété sur le nom de la mission
    property int fontSize: 12
    property string missionName: ""

    // Propriétés sur les couleurs utilisées
    property string backgroundColor: "#000000"
    property string textColor: "#C8C8C8"
    property string borderColor: "#C8C8C8"
    property string highlightColor: "#000080"

    // Signaux à surchager en QML ou en Python
    signal clicked(string text)


    // Rectangle pour la couleur du fond du bouton
    Rectangle{
        id: body

        anchors.fill: parent

        color: root.backgroundColor
        border.width: 2
        border.color: borderColor



        // Image centrée sur le bouton
        Image {
            id: image

            anchors.top: parent.top
            anchors.topMargin: body.border.width
            anchors.left: parent.left
            anchors.leftMargin: body.border.width
            anchors.right: parent.right
            anchors.rightMargin: body.border.width
            fillMode: Image.PreserveAspectFit

            source: root.image !== "" ? (root.path + root.image)
                                      : ""
        }

        // Texte visible au centre du bouton
        Text{
            id: text

            anchors.top: image.bottom
            anchors.bottom: parent.bottom
            anchors.bottomMargin: body.border.width
            anchors.verticalCenter: parent.verticalCenter

            text: root.text
            font.pixelSize: root.font_size
            font.family: "Verdana"
            color: root.textColor
        }

        // Zone de détection de souris pour détecter les clics
        MouseArea{
            id: area

            anchors.fill: parent

            hoverEnabled: true
            enabled: true


            // Répétition des signaux
            onClicked: root.clicked(root.text)
        }

        // Rectangle pour le highlight
        Rectangle {
            id: highlight

            anchors.fill: parent
            anchors.margins: body.border.width

            color: root.highlightColor
            opacity: 0.3
        }
    }
}
