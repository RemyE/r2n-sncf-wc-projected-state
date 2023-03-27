import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"


Item {
    id: root

    // Propriétés sur la rame paramétrée
    property string operationName: ""

    // Propriété sur la validité des valeurs
    readonly property bool valid: root.operationName !== "" && root.cleanWaterData.length !== 0 && root.poopooWaterData.length !== 0 && root.flushData.length !== 0 && root.sinkData.length !== 0

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

    // Propriété sur les missions
    property var cleanWaterData: []         // format [[[year, month, day], [value, average]], ...] -> Format barSeries + SplineSeries
    property var poopooWaterData: []        // format [[[year, month, day], [value, average]], ...] -> Format barSeries + SplineSeries
    property var flushData: []              // format [[[year, month, day], value], ...]            -> Format barSeries
    property var sinkData: []               // format [[[year, month, day], value], ...]            -> Format BarSeries

    // Propriété sur la sélection du graphe effectuée
    property string visibleData: "levels"      // Valeurs possibles : "levels", "uses"
    onVisibleDataChanged: { root.update() }
    property string visiblePeriod: "week"           // Valeurs possibles : "week", "month", "year"
    onVisiblePeriodChanged: { root.update() }


    // Fonction de mise à jour des graphiques, à appeler à chaque fois que la marche visible ou la sélection change
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
        borderWidth: 1

        text: "retour"
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
        borderWidth: returnButton.borderWidth

        text: "sauvegarder"
    }


    // Rectangle de structure pour le graphe
    Rectangle {
        id: operationBody

        anchors.top:  returnButton.bottom
        anchors.topMargin: returnButton.anchors.topMargin
        anchors.left: returnButton.left
        anchors.right: saveButton.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: returnButton.anchors.topMargin
        border.width: 3 * returnButton.borderWidth

        color: returnButton.backgroundColor
        border.color: returnButton.textEnabledColor



        UI_chartview {
            id: operationChart

            anchors.fill: parent

            xTitle: "Date de la marche"
            xDecimals: 0
            xTicks: 4
            xMinorTicks: 0

            ySplinesTitle: root.visibleData === "levels" ? "Niveaux d'eau (en l, moyenné sur 7 jours)"  // Niveaux d'eau moyennés sur 7 jours en mode "levels"
                                                         : root.visibleData === "uses" ? ""             // Aucune spline series en mode "uses"
                                                                                       : ""             // Nouvelle donnée non définie
            ySplinesDecimals: root.visibleData === "levels" ? 2                                         // contenance (pas entier)
                                                            : root.visibleData === "uses" ? 0           // Aucune valeur
                                                                                          : 0           // Nouvelle donnée non définie
            ySplinesTicks: 4
            ySplinesMinorTicks: 2

            yBarsTitle: root.visibleData === "levels" ? "Niveaux d'eau (en l)"                          // Niveaux d'eau moyennés sur 7 jours en mode "levels"
                                                       : root.visibleData === "uses" ? ""               // Aucune spline series en mode "uses"
                                                                                     : ""               // Nouvelle donnée non définie
            yBarsDecimals: root.visibleData === "levels" ? 2                                            // contenance (pas entier)
                                                          : root.visibleData === "uses" ? 0             // Compte (entier)
                                                                                        : 0             // Nouvelle donnée non définie
            yBarsTicks: 4
            yBarsMinorTicks: 2

            splinesData: [[[0.0, 1], [0.5, 0.2]], [[0.1, 0.3], [0.2, 0.7], [0.6, 0.4]]]
            splinesLegend: [["#40E0D0", "Eau claire"], ["#B8860B", "Eau sale"]]
        }

        // Row Layout pour sélectionner le temps à afficher
        RowLayout {
            id: periodLayout

            anchors.top: parent.top
            anchors.topMargin: 8 + parent.border.width
            anchors.left: parent.left
            anchors.leftMargin: anchors.topMargin
            height: returnButton.height
            width: returnButton.width * periodRepeater.count + spacing * (periodRepeater.count - 1)
            spacing: anchors.topMargin - parent.border.width

            // Liste des UI_button pour sélectionner entre le jour, le mois et l'année
            Repeater {
                id: periodRepeater

                model: [["semaine", "week"],
                        ["mois", "month"],
                        ["année", "year"]]

                UI_button {
                    width: returnButton.width
                    height: returnButton.height
                    radius: width / 2
                    borderWidth: returnButton.borderWidth * (returnButton.borderWidth + (operationBody.border.width - returnButton.borderWidth) * (root.visiblePeriod === modelData[1]))

                    text: modelData[0]

                    onClicked: { root.visiblePeriod = modelData[1] }
                }
            }
        }

        // Row Layout pour sélectionner le type de données visible
        RowLayout {
            id: dataLayout

            anchors.top: parent.top
            anchors.topMargin: 8 + parent.border.width
            anchors.right: parent.right
            anchors.rightMargin: anchors.topMargin
            height: returnButton.height
            width: returnButton.width * dataRepeater.count + spacing * (dataRepeater.count - 1)
            spacing: anchors.topMargin - parent.border.width

            // Liste des UI_button pour sélectionner entre le jour, le mois et l'année
            Repeater {
                id: dataRepeater

                model: [["Niveau d'eau", "levels"],
                        ["utilisations", "uses"]]

                UI_button {
                    width: returnButton.width
                    height: returnButton.height
                    radius: width / 2
                    borderWidth: returnButton.borderWidth * (1 + (root.visibleData === modelData[1]))

                    text: modelData[0]

                    onClicked: { root.visibleData = modelData[1] }
                }
            }
        }
    }
}