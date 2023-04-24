import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"

Item {
    id: root

    // Nom de l'opération actuellement sélectionnée
    property string operationName: ""

    // Indique si les valeurs sont valides pour effectuer l'opération
    readonly property bool valid: root.operationName !== "" && root.cleanWaterData.length !== 0 && root.poopooWaterData.length !== 0

    // Date du jour au format UTC
    property int day: (new Date()).getUTCDate()
    property int month: (new Date()).getUTCMonth() + 1
    property int year: (new Date()).getUTCFullYear()

    // Données de consommation d'eau propre et de remplissage d'eau sale
    // Format des données : [[[année, mois, jour], [min, moy, max]], ...]
    property var cleanWaterData: []
    onCleanWaterDataChanged: root.update()
    property var poopooWaterData: []
    onPoopooWaterDataChanged: root.update()

    // Période de temps visible sur le graphique (semaine, mois, année, tout)
    property string visiblePeriod: "week"
    onVisiblePeriodChanged: root.update()

    // Met à jour les graphiques en fonction des données et de la période visible
    function update() {
        // Calcule la date limite en fonction de la période visible
        var daysVisible = root.visiblePeriod == "year" ? 365 : root.visiblePeriod == "month" ? 30 : root.visiblePeriod == "week" ? 7 : parseInt(Date.parse(new Date())  / 24 / 60 / 60 / 1000)
        var limitDate = new Date() - daysVisible * 24 * 60 * 60 * 1000

        // Traite les données d'eau propre
        var datas = []
        for (var splineIndex = 0; splineIndex < root.cleanWaterData.length; splineIndex++) {
            datas.push([])
            for (var pointIndex = 0; pointIndex < root.cleanWaterData[splineIndex].length; pointIndex++) {
                // Convertit la date en timestamp UNIX et ajoute la valeur avec la date au format UNIX si elle doit être affichée
                var unixDate = (new Date(root.cleanWaterData[splineIndex][pointIndex][0][0], root.cleanWaterData[splineIndex][pointIndex][0][1] - 1, root.cleanWaterData[splineIndex][pointIndex][0][2])).getTime()
                if (unixDate > limitDate) {
                    datas[datas.length - 1].push([unixDate, root.cleanWaterData[splineIndex][pointIndex][1]])
                }
            }

            // Trie les points de la courbe par ordre croissant sur l'axe des x
            datas[datas.length - 1].sort(function(a, b) {return a[0] - b[0]})
        }

        // Traite les données d'eau sale
        for (var splineIndex = 0; splineIndex < root.poopooWaterData.length; splineIndex++) {
            datas.push([])
            for (var pointIndex = 0; pointIndex < root.poopooWaterData[splineIndex].length; pointIndex++) {
                // Convertit la date en timestamp UNIX et ajoute la valeur avec la date au format UNIX si elle doit être affichée
                var unixDate = (new Date(root.poopooWaterData[splineIndex][pointIndex][0][0], root.poopooWaterData[splineIndex][pointIndex][0][1] - 1, root.poopooWaterData[splineIndex][pointIndex][0][2])).getTime()
                if (unixDate > limitDate) {
                    datas[datas.length - 1].push([unixDate, root.poopooWaterData[splineIndex][pointIndex][1]])
                }
            }

            // Trie les points de la courbe par ordre croissant sur l'axe des x
            datas[datas.length - 1].sort(function(a, b) {return a[0] - b[0]})
        }

        // Met à jour les données du graphique, ce qui actualise également les limites et les valeurs visibles
        operationChart.datas = datas
    }

    // Bouton pour revenir à l'écran précédent
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

    // Titre de l'opération en cours
    Text {
        id: title

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: returnButton.verticalCenter

        text: root.operationName
        font.pixelSize: 24
        font.family: "Verdana"
        color: root.valid ? returnButton.textEnabledColor : returnButton.textDisabledColor
    }

    // Bouton pour sauvegarder les données
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

    // Conteneur du graphique pour visualiser les données
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

        // Graphique pour afficher les données des réservoirs d'eau
        UI_chartview {
            id: operationChart

            anchors.fill: parent
            anchors.bottomMargin: fontSize
            anchors.leftMargin: fontSize
            anchors.topMargin: 1.5 * fontSize
            anchors.rightMargin: 3 * fontSize

            xTitle: "Date de la marche"
            xMinimumAuto: true
            xMinimum: (parseInt(Date.parse(new Date()) / (24 * 60 * 60 * 1000))
                       - (root.visiblePeriod == "year" ? 365 : root.visiblePeriod == "month" ? 30 : root.visiblePeriod == "week" ? 7 : parseInt(Date.parse(new Date())  / 24 / 60 / 60 / 1000)))
                       * (24 * 60 * 60 * 1000)
            xMaximumAuto: false
            xMaximum: parseInt(Date.parse(new Date()) / (24 * 60 * 60 * 1000)) * (24 * 60 * 60 * 1000)
            xDecimals: 0
            xTicks: 4
            xDateFormat: true

            yTitle: "Delta de remplissage des réservoirs d'eau"
            yMinimumAuto: false
            yMinimum: 0
            yMaximumAuto: true
            yMaximum: 100
            yDecimals: 2
            yTicks: 4
            yDateFormat: false

            // Données des courbes définies par la fonction de mise à jour
            names: ["Consommation eau claire (minimum)", "Consommation eau claire (moyenne)", "Consommation eau claire (maximum)",
                    "Remplissage eau sale (minimum)", "Remplissage eau sale (moyenne)", "Remplissage eau sale (maximum)"]
            colors: ["#ADD8E6", "#6495ED", "#0000FF", "#DEB887", "#DAA520", "#A0522D"]
            widths: [1, 2, 1, 1, 2, 1]
        }

        // Barre de sélection pour choisir la période à afficher
        RowLayout {
            id: periodLayout

            anchors.top: parent.top
            anchors.topMargin: 8 + parent.border.width
            anchors.right: parent.right
            anchors.rightMargin: anchors.topMargin
            height: returnButton.height
            width: returnButton.width * periodRepeater.count + spacing * (periodRepeater.count - 1)
            spacing: anchors.topMargin - parent.border.width

            // Liste des boutons pour choisir entre semaine, mois, année et tout
            Repeater {
                id: periodRepeater

                model: [["semaine", "week"],
                        ["mois", "month"],
                        ["année", "year"],
                        ["complet", "tout"]]

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
    }
}
