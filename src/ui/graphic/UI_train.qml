import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"


Item {
    id: root

    // Propriétés sur la rame paramétrée
    property string trainName: ""

    // Propriété sur la validité des valeurs
    readonly property bool valid: root.trainName !== "" && root.cleanWaterData.length !== 0 && root.poopooWaterData.length !== 0 && root.flushData.length !== 0 && root.sinkData.length !== 0

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

    // Propriété sur les valeurs
    property var cleanWaterData: []         // format [["operation", [year, month, day], value], ...] -> Format SplineSeries
    property var poopooWaterData: []        // format [["operation", [year, month, day], value], ...] -> Format SplineSeries
    property var flushData: []              // format [["operation", [year, month, day], value], ...] -> Format barSeries
    property var sinkData: []               // format [["operation", [year, month, day], value], ...] -> Format BarSeries


    // Fonction de mise à jour des graphiques, à appeler dès que les données changent où qu'une marche est ajoutée/supprimée
    function update() {
        // TODO : définir
    }



    // Bouton de retour
    UI_button {
        id: returnButton
        objectName: "returnButton"
        
        anchors.top: parent.top
        anchors.topMargin: 8
        anchors.left: parent.left
        anchors.leftMargin : 8
        width: 100
        height: 30
        
        text: "retour"
    }
    
    // Titre
    Text {
        id: title
        
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: returnButton.verticalCenter
        
        text: root.trainName
        color: root.valid ? returnButton.textEnabledColor : returnButton.textDisabledColor
        
    }
    
    // Bouton de sauvegarde
    UI_button {
        id: saveButton
        objectName: "saveButton"
        
        anchors.top: parent.top
        anchors.topMargin: returnButton.anchors.topMargin
        anchors.right: parent.right
        anchors.rightMargin: returnButton.anchors.leftMargin
        width: returnButton.width
        height: returnButton.height

        text: "sauvegarder"
    }


    // Rectangle pour la structure de visualisation, de sélection et d'ajout des missions
        Rectangle {
        id: selectorBody

        anchors.top:  returnButton.bottom
        anchors.topMargin: returnButton.anchors.topMargin
        anchors.left: returnButton.left
        anchors.right: saveButton.right
        height: returnButton.height * 3     // TODO : préciser
        border.width: 3 * returnButton.borderWidth

        color: returnButton.backgroundColor
        border.color: returnButton.textEnabledColor

        // TODO : ajouter le RowLayout de sélection
    }


        // Rectangle pour la structure de visualisation, de sélection et d'ajout des missions
        Rectangle {
        id: trainBody

        anchors.top:  selectorBody.bottom
        anchors.topMargin: selectorBody.anchors.topMargin
        anchors.left: returnButton.left
        anchors.right: saveButton.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: returnButton.anchors.topMargin
        border.width: 3 * returnButton.borderWidth

        color: returnButton.backgroundColor
        border.color: returnButton.textEnabledColor

        // TODO : ajouter le UI_chartview
    }
}