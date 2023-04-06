import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"


Item {
    id: root

    // Prorpriétés sur la liste des marches
    property var operationNames: []
    property var operationSources: []

    // Propriétés sur les couleurs utilisées
    property string backgroundColor: "#FFFFFF"
    property string textColor: "#949494"
    property string borderColor: "#949494"


    // Signaux à surchager en QML ou en Python
    signal operationClicked(string text)



    // Listview pour les marches
    Rectangle {
        id: operationBody

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: predictionButton.bottom
        anchors.margins: 12

        color: root.backgroundColor
        border.width: 2
        border.color: root.borderColor



        // Rectangle pour le titre
        Rectangle {
            id: operationTitle

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 36

            color: root.backgroundColor
            border.width: 2
            border.color: root.borderColor


            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter

                text: "Marches"
                font.pixelSize: 24
                font.family: "Verdana"
                color: root.textColor
            }
        }

        // Liste des marches à visualiser
        ListView {
            id: operationView

            anchors.left: parent.left
            anchors.leftMargin: operationBody.border.width
            anchors.right: parent.right
            anchors.rightMargin: operationBody.border.width
            anchors.bottom: parent.bottom
            anchors.bottomMargin: operationBody.border.width
            anchors.top: operationTitle.bottom

            flickableDirection: Flickable.VerticalFlick
            boundsBehavior: Flickable.StopAtBounds
            clip: true
            spacing: 0

            model: Math.min(root.operationNames.length, root.operationSources.length)

            delegate: UI_selector {
                anchors.left: parent ? parent.left : undefined
                anchors.right: parent ? parent.right : undefined

                path: "../assets/operations/"
                name: root.operationNames[index]
                source: root.operationSources[index]


                // Répétition des signaux
                onClicked: function(text) {root.operationClicked(text)}
            }

            ScrollBar.vertical: ScrollBar {}
        }
    }


    // Bouton pour l'outil de prédiction
    UI_button {
        id: predictionButton
        objectName: "predictionButton"

        anchors.left: operationBody.left
        anchors.right: operationBody.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: operationBody.anchors.margins
        anchors.topMargin: operationBody.anchors.margins
        height: 72
        borderWidth:  2

        text: "Outil de prédiction"
        fontSize: 24
    }
}