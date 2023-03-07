import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"


Item {
    id: root

    // Propriétés sur la rame paramétrée
    property string operationName: ""

    // Propriété sur la validité des valeurs
    readonly property bool valid: true       // TODO : définir, selon les données

    // Propriété sur la date du jour
    property int day: 0
    property int month: 0
    property int year: 0
    Component.onCompleted: {
        var date = new Date()
        root.day = date.getDate()
        root.month = date.getMonth() + 1
        root.year = date.getFullYear()
    }



    // Bouton de retour
    UI_button {
        id: returnButton
        objectName: "returnButton"

        anchors.top: parent.top
        anchors.topMargin: 8
        anchors.left: parent.left
        anchors.leftMargin : 8
        width: 60
        height: 30

        text: "return"
    }

    // Titre
    Text {
        id: title

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: returnButton.verticalCenter

        text: root.operationName
        color: root.valid ? returnButton.textEnabledColor : returnButton.textDisabledColor

    }

    // Bouton de sauegarde
    UI_button {
        id: saveButton
        objectName: "saveButton"

        anchors.top: parent.top
        anchors.topMargin: returnButton.anchors.topMargin
        anchors.right: parent.right
        anchors.rightMargin: returnButton.anchors.leftMargin
        width: returnButton.width
        height: returnButton.height
    }
}